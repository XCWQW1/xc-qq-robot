import configparser
import os
import re
import signal
import sys
import time
import json
import asyncio

import importlib
import websockets

from API.api_log import Log, LogSP
from API.api_qq import QQApi
from API.api_thread import start_thread
from init.main_init import main_init


def list_plugins():
    # 插件列表
    p_plugin_list = []
    Log.initialize("检测插件中")

    # 遍历插件目录，将所有插件模块动态导入并保存到列表中
    for plugin_file in os.listdir("plugins"):
        if sys.stdin.isatty():
            plugins_file = f"plugins"
        else:
            plugins_file = "plugins"

        # 忽略非 .py 文件和以 . 开头的文件
        if not plugin_file.endswith('.py') or plugin_file.startswith('.'):
            continue

        # 获取模块名
        name = os.path.splitext(plugin_file)[0]
        # 动态导入模块
        loader = importlib.machinery.SourceFileLoader(name, os.path.join(plugins_file, plugin_file))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)

        # 将插件函数添加到列表中
        p_plugin_list.append(module.plugin)
        Log.initialize(f"检测到插件：{name}")

    return p_plugin_list


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

    return c_ws_websocket_ip, c_ws_websocket_port, c_http_api_http_api_ip, c_http_api_http_api_port


# 配置文件路径
config_path = "config/config.ini"

if os.path.exists(config_path):
    # 配置文件路径
    config_path = "config/config.ini"

    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    # 获取相应的配置信息
    http_api_http_api_ip = config.get("go-cqhttp", "http_api_ip")
    http_api_http_api_port = config.get("go-cqhttp", "http_api_port")
    cqhttp_url = F"http://{http_api_http_api_ip}:{http_api_http_api_port}/"


def process_message(data):
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
        q_add_flag = str(data.get("flag", ""))
        q_add_comment = str(data.get("comment", ""))
        q_all_user_id = str(data.get("user_id", ""))
        q_all_group_id = str(data.get("group_id", ""))
        q_all_user_nickname = str(QQApi.get_user_nickname(q_user_id=q_all_user_id))
    else:
        q_add_flag = ""
        q_add_comment = ""
        q_all_user_id = ""
        q_all_group_id = ""
        q_all_user_nickname = ""

    # 发送消息日志
    if q_post_type == "message":
        start_thread(func=Log.accepted_info,
                     args=(q_message_type, q_message, q_group_id, q_nickname, q_card, q_user_id, q_message_id, q_group_name))
    elif "sub_type" in data and data["sub_type"] == "add":
        start_thread(func=Log.accepted_group_add_request,
                     args=(q_add_flag, q_add_comment, q_all_group_id, q_all_user_id, q_all_user_nickname))

    # 处理机器人功能
    # 遍历插件目录
    for plugin in plugin_list:
        try:
            start_thread(func=plugin, args=(q_sub_type, q_post_type, q_message_type, q_message, q_group_id, q_group_name, q_nickname, q_card, q_user_id, q_message_id, q_add_flag, q_add_comment, q_all_group_id, q_all_user_id, q_all_user_nickname, data))
        except Exception as e:
            Log.error(q_message_type, f"调用插件 {plugin} 报错：{e}")


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
                    else:
                        # 使用新线程处理其他类型的消息
                        start_thread(process_message, (data,))
        except Exception as e:
            Log.error(error_txt=f'websocket服务连接失败，错误信息：{e}', q_message_type="error")
            retry_count -= 1
            if retry_count > 0:
                Log.initialize(f'{retry_delay}秒后重试...')
                await asyncio.sleep(retry_delay)
            else:
                Log.error(error_txt='websocket服务连接失败，已达最大重试次数，程序退出', q_message_type="error")


if __name__ == '__main__':
    # 初始化
    main_init()
    LogSP.initialize("正在连接go-cqhttp的websocket服务...")

    # 设置Ctrl+C的信号处理函数
    def signal_handler(sig, frame):
        current_time = time.time()
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
        logs = f"[{now_time}] [信息] 程序已关闭"
        LogSP.print_log(logs)
        start_thread(func=LogSP.save_log, args=(logs,))
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    go_cqhttp_ws_websocket_ip, go_cqhttp_ws_websocket_port, go_cqhttp_http_api_http_api_ip, go_cqhttp_http_api_http_api_port = load_config()
    plugin_list = list_plugins()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_go_cqhttp_server())


'''
                    _ooOoo_
                   o8888888o
                   88" . "88
                   (| -_- |)
                    O\ = /O
                ____/`---'\____
              .   ' \\| |// `.
               / \\||| : |||// \
             / _||||| -:- |||||- \
               | | \\\ - /// | |
             | \_| ''\---/'' | |
              \ .-\__ `-` ___/-. /
           ___`. .' /--.--\ `. . __
        ."" '< `.___\_<|>_/___.' >'"".
        | | : `- \`.;`\ _ /`;.`/ - ` : | |
         \ \ `-. \_ __\ /__ _/ .-` / /
 ======`-.____`-.___\_____/___.-`____.-'======
                    `=---='

 .............................................
          佛祖保佑             永无BUG
'''
