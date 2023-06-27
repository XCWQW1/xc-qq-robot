import asyncio
import configparser
import json
import re

import websockets

from API.api_find_plugin import list_plugins
from API.api_log import Log
from API.api_qq import QQApi
from API.api_thread import start_thread, start_process


def load_config():
    # 配置文件路径
    c_config_path = "config/config.ini"

    # 读取配置文件
    c_config = configparser.ConfigParser()
    c_config.read(c_config_path)

    # 获取相应的配置信息
    c_ws_websocket_ip = c_config.get("go-cqhttp", "websocket_ip")
    c_ws_websocket_port = c_config.get("go-cqhttp", "websocket_port")
    c_http_api_http_api_ip = c_config.get("go-cqhttp", "http_api_ip")
    c_http_api_http_api_port = c_config.get("go-cqhttp", "http_api_port")
    c_plugin_admin = str(c_config.get("plugin_admin", "admin_qq"))

    return c_ws_websocket_ip, c_ws_websocket_port, c_http_api_http_api_ip, c_http_api_http_api_port, c_plugin_admin


def parse_cq_codes(cq):
    pattern = r"\[CQ:(\w+)((?:,[^,\]]+=[^,\]]+)*)\]"
    matches = re.findall(pattern, cq)
    result = []
    for match in matches:
        cq_code = {"type": match[0]}
        if match[1]:
            params = match[1].split(",")[1:]
            for param in params:
                key, value = param.split("=", 1)
                cq_code[key] = value
        result.append(cq_code)
    return result


def process_message(data, plugin_list, name_list):
    q_post_type = str(data.get("post_type", ""))
    q_sub_type = str(data.get("sub_type", ""))
    # 处理消息变成变量：
    # 验证json类是否为空，空则不执行否则会报错
    if data["post_type"] == "message":
        q_message = str(data.get("message", ""))
        q_group_id = str(data.get("group_id", ""))
        sender = data.get("sender", {})
        q_nickname = str(sender.get("nickname", ""))
        q_user_id = str(sender.get("user_id", ""))
        q_card = str(sender.get("card", sender.get("nickname", "")))
        q_message_id = str(data.get("message_id", ""))
        q_message_type = str(data.get("message_type", ""))
        q_group_name = str(start_thread(func=QQApi.get_group, args=(q_group_id,)) if q_message_type == "group" else "")
    else:
        q_message = ""
        q_group_id = ""
        sender = ""
        q_nickname = ""
        q_user_id = ""
        q_card = ""
        q_message_id = ""
        q_message_type = ""
        q_group_name = ""

    sub_type = ["add", "invite", "approve", "invite", "leave", "kick", "kick_me"]

    if q_sub_type in sub_type:
        q_group_member_flag = str(data.get("flag", ""))
        q_group_member_comment = str(data.get("comment", ""))
        q_group_member_user_id = str(data.get("user_id", ""))
        q_group_member_group_id = str(data.get("group_id", ""))
        q_group_member_user_nickname = str(QQApi.get_user_nickname(q_user_id=q_group_member_user_id))
        q_group_member_operator_id = str(data.get("operator_id", ""))
        q_group_member_operator_nickname = str(QQApi.get_user_nickname(q_user_id=q_group_member_operator_id))
    else:
        q_group_member_flag = ""
        q_group_member_comment = ""
        q_group_member_user_id = ""
        q_group_member_group_id = ""
        q_group_member_user_nickname = ""
        q_group_member_operator_id = ""
        q_group_member_operator_nickname = ""

    # 发送消息日志
    if q_post_type == "message":
        start_thread(func=Log.accepted_info,
                     args=(q_message_type, q_message, q_group_id, q_nickname, q_card, q_user_id, q_message_id, q_group_name))
    elif "sub_type" in data and data["sub_type"] == "add":
        start_thread(func=Log.accepted_group_add_request,
                     args=(q_group_member_flag, q_group_member_comment, q_group_member_group_id, q_group_member_user_id, q_group_member_user_nickname))
    elif q_sub_type == "kick":
        start_thread(func=Log.group_kick,
                     args=(q_sub_type, q_group_member_group_id, q_group_member_user_id, q_group_member_user_nickname, q_group_member_operator_id, q_group_member_user_nickname))
    elif q_sub_type == "leave":
        start_thread(func=Log.group_leave,
                     args=(q_sub_type, q_group_member_group_id, q_group_member_user_id, q_group_member_user_nickname))

    for index, (plugin, name) in enumerate(zip(plugin_list, name_list)):
        try:
            start_thread(func=plugin, args=(q_sub_type, q_post_type, q_message_type, q_message, q_group_id, q_group_name, q_nickname, q_card, q_user_id, q_message_id, q_group_member_flag, q_group_member_comment, q_group_member_group_id, q_group_member_user_id, q_group_member_user_nickname, q_group_member_operator_id, q_group_member_operator_nickname, data))
        except Exception as e:
            Log.error("error", f"调用插件 {name} 报错：{e}")


async def connect_to_go_cqhttp_server():
    retry_count = 5  # 最大重试次数
    retry_delay = 5  # 每次重试等待时间（秒）
    while retry_count > 0:
        try:
            async with websockets.connect(f'ws://{go_cqhttp_ws_websocket_ip}:{go_cqhttp_ws_websocket_port}') as websocket:
                # 连接成功后，发送一个 ping 消息
                await websocket.ping()
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("post_type") == "meta_event" and data.get("meta_event_type") == "heartbeat":
                        # 过滤掉心跳包
                        continue
                    elif data.get("post_type") == "meta_event" and data.get(
                            "meta_event_type") == "lifecycle" and data.get("sub_type") == "connect":
                        # 如果收到连接成功的消息，输出提示信息
                        user_z = data["self_id"]
                        Log.initialize("websocket服务连接成功！")
                        Log.initialize(f"当前登陆的机器人账号为：{user_z}")
                        plugin_list, name_list = list_plugins()
                    else:
                        # 使用新进程处理其他类型的消息
                        start_process(process_message, (data, plugin_list, name_list))
        except websockets.ConnectionClosed as e:
            Log.error(error_txt=f'websocket服务连接失败，错误码: {e.code}, 原因: {e.reason}', q_message_type="error")
            retry_count -= 1
            if retry_count > 0:
                Log.initialize(f'{retry_delay}秒后重试...')
                await asyncio.sleep(retry_delay)
            else:
                Log.error(error_txt='websocket服务连接失败，已达最大重试次数，程序退出', q_message_type="error")
        except websockets.ConnectionClosedOK:
            Log.error('error', "WebSocket 连接被主机关闭")
            retry_count -= 1
            if retry_count > 0:
                Log.initialize(f'{retry_delay}秒后重试...')
                await asyncio.sleep(retry_delay)
            else:
                Log.error('error', "WebSocket 连接被主机关闭")
        except websockets.ConnectionClosedError as e:
            Log.error('error', f"WebSocket 连接非正常关闭关闭，错误码: {e.code}, 原因: {e.reason}")
            retry_count -= 1
            if retry_count > 0:
                Log.initialize(f'{retry_delay}秒后重试...')
                await asyncio.sleep(retry_delay)
            else:
                Log.initialize(f'{retry_delay}秒后重试...')
                break
        except websockets.ConnectionClosed as e:
            Log.error('error', f"WebSocket 连接已断开，代码: {e.code}, 原因: {e.reason}")
            retry_count -= 1
            if retry_count > 0:
                Log.initialize(f'{retry_delay}秒后重试...')
                await asyncio.sleep(retry_delay)
            else:
                Log.error('error', f"WebSocket 连接已断开，代码: {e.code}, 原因: {e.reason}")
                break
        except Exception as e:
            Log.error('error', "发生未知错误 :" + str(e))
            retry_count -= 1
            if retry_count > 0:
                Log.initialize(f'{retry_delay}秒后重试...')
                await asyncio.sleep(retry_delay)
            else:
                Log.error('error', "发生未知错误 :" + str(e))
                break


if __import__:
    go_cqhttp_ws_websocket_ip, go_cqhttp_ws_websocket_port, go_cqhttp_http_api_http_api_ip, go_cqhttp_http_api_http_api_port, plugin_admin = load_config()
