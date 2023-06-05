import configparser
import os
import re
import signal
import sys
import time
import json
import queue
import asyncio
import requests
import threading
import traceback
import importlib
import websockets

from colorama import init, Fore, Back, Style

# 初始化colorama
init()


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


def start_thread(func, args):
    # 创建一个队列对象
    result_queue = queue.Queue()

    # 在新线程中执行函数，并将结果存入队列中
    def thread_func():
        try:
            thread_result = func(*args)
            result_queue.put(thread_result)
        except Exception as e:
            result_queue.put(e)

    # 创建新线程
    t = threading.Thread(target=thread_func)

    # 设置线程为守护线程
    t.setDaemon(True)

    # 启动线程
    t.start()

    # 等待线程执行完成，并获取结果
    t.join()
    result = result_queue.get()

    # 如果结果是异常对象，将异常信息打印出来
    if isinstance(result, Exception):
        now_time_and_day = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_file = f'errors/{now_time_and_day}.log'  # 日志文件名
        with open(log_file, 'a') as f_log:
            # 使用 traceback 模块打印完整的错误信息
            trace = ''.join(traceback.format_exception(type(result), result, result.__traceback__))
            # 设置日志内容
            logs = f"[{Log.now_time()}] [错误] [线] {trace}"
            # 显示日志
            print(logs)
            f_log.write(f"子线程执行出错: {trace}\n")
        return None

    # 返回结果
    return result


class Log:
    @staticmethod
    def now_time():
        # 当前时间获取
        current_time = time.time()
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
        return now_time

    @staticmethod
    def initialize(initialize_txt):
        # 设置群日志内容
        logs = f"[{Log.now_time()}] [初始] {initialize_txt}"
        # 显示日志
        print(logs)
        LogSP.save_log(logs)

    # @是防止第一个变量输入为self
    # 正常信息
    @staticmethod
    def accepted_info(q_message_type, q_message, q_group_id, q_nickname, q_card, q_user_id, q_message_id, q_group_name):
        # 判断私聊还是群发
        if q_message_type == "group":
            # 设置群日志内容
            logs = f"[{Log.now_time()}] [信息] [群] [接收] [{q_group_name}({q_group_id})] [{q_nickname}-{q_user_id}({q_card})] : {q_message} ({q_message_id})"
            # 显示日志
            print(logs)
            LogSP.save_log(logs)
        elif q_message_type == "private":
            # 设置群日志内容
            logs = f"[{Log.now_time()}] [信息] [私] [接收] [{q_nickname}-{q_user_id}] : {q_message} ({q_message_id})"
            # 显示日志
            print(logs)
            LogSP.save_log(logs)

    # 错误信息
    @staticmethod
    def error(q_message_type, error_txt):
        if q_message_type == "group":
            # 设置日志内容
            logs = Fore.RED + f"[{Log.now_time()}] [错误] [群] {error_txt}" + Style.RESET_ALL
            # 显示日志
            print(logs)
            LogSP.save_log(logs)
        elif q_message_type == "private":
            # 设置日志内容
            logs = Fore.RED + f"[{Log.now_time()}] [错误] [私] {error_txt}" + Style.RESET_ALL
            # 显示日志
            print(logs)
            LogSP.save_log(logs)

        elif q_message_type == "error":
            # 设置日志内容
            logs = Fore.RED + f"[{Log.now_time()}] [错误] {error_txt}" + Style.RESET_ALL
            # 显示日志
            print(logs)
            LogSP.save_log(logs)

    # 发送 信息
    @staticmethod
    def send(send_msg, q_message_type, q_group_id="", q_message_id="", q_group_name="", q_user_name="", q_user_id=""):
        # 判断私聊还是群发
        if q_message_type == "group":
            # 设置日志内容
            logs = f"[{Log.now_time()}] [信息] [群] [发送] {send_msg} ({q_message_id}) -> [{q_group_name}({q_group_id})] "
            # 显示日志
            print(logs)
            LogSP.save_log(logs)
        elif q_message_type == "private":
            # 设置日志内容
            logs = f"[{Log.now_time()}] [信息] [私] [发送] {send_msg} ({q_message_id}) -> [{q_user_name}({q_user_id})] "
            # 显示日志
            print(logs)
            LogSP.save_log(logs)

    # 撤回 群信息
    @staticmethod
    def del_msg(q_message_type, q_user_id="", q_message_id="", q_group_name="", q_user_name=""):
        if q_message_type == "group":
            # 设置日志内容
            logs = f"[{Log.now_time()}] [信息] [群] [撤回] [{q_message_id}] ({q_message_id}) -> [{q_group_name}({q_user_id})] "
            # 显示日志
            print(logs)
            LogSP.save_log(logs)
        elif q_message_type == "private":
            # 设置日志内容
            logs = f"[{Log.now_time()}] [信息] [私] [撤回] [{q_message_id}] ({q_message_id}) -> [{q_user_name}({q_user_id})] "
            # 显示日志
            print(logs)
            LogSP.save_log(logs)

    @staticmethod
    def accepted_group_add_request(q_add_flag, q_add_comment, q_add_group_id, q_add_user_id, q_add_user_nickname):
        # 设置群日志内容
        logs = f"[{Log.now_time()}] [加群] 群：[{QQApi.get_group(q_add_group_id)}({q_add_group_id})] 用户：[{q_add_user_nickname}({q_add_user_id})] 验证信息：{q_add_comment} flag：{q_add_flag}"
        # 显示日志
        print(logs)
        LogSP.save_log(logs)


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

    initialize_config_bool = True

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


class QQApi:
    # 发送消息
    @staticmethod
    def send(q_message_type, send_msg, auto_escape, q_group_id="", q_user_id="", q_user_name=""):
        if q_message_type == "group":
            # 发送信息
            response = requests.get(
                url=cqhttp_url + f"send_msg?group_id={q_group_id}&message={send_msg}&auto_escape={auto_escape}").text

            # 转换返回的json为python格式
            json_send = json.loads(response)

            # 取消息ID
            if json_send["status"] == "failed":
                q_message_id = ''
            else:
                q_message_id = str(json_send.get("data", {}).get("message_id", ""))

            # 判断消息是否发送成功
            if json_send["status"] == "ok":
                # 取群名称
                q_group_name = QQApi.get_group(q_group_id)

                # 发送日志
                start_thread(func=Log.send,
                             args=(send_msg, q_message_type, q_group_id, q_message_id, q_group_name, q_user_id, ))

            else:
                start_thread(func=Log.error,
                             args=(q_message_type, "消息发送失败，可能消息过长也可能是被腾讯吞了或者帐号被冻结"))
                requests.get(url=cqhttp_url + f"send_msg?group_id={q_group_id}&message=消息发送失败")

            # 返回消息ID
            return q_message_id
        elif q_message_type == "private":
            # 发送信息
            response = requests.get(
                url=cqhttp_url + f"send_msg?user_id={q_user_id}&message={send_msg}&auto_escape={auto_escape}").text

            # 吧json转换为python格式
            json_send = json.loads(response)

            # 判断类是否存在 存在则吧变量设置为类的值 不存在则设置为空
            # 取消息ID
            q_message_id = str(json_send.get("data", {}).get("message_id", ""))

            # 判断消息是否发送成功
            if json_send["status"] == "ok":
                # 发送日志
                start_thread(func=Log.send,
                             args=(send_msg, q_message_type, q_group_id, q_message_id, q_user_name, q_user_id))
            else:
                start_thread(func=Log.error,
                             args=(q_message_type, "消息发送失败，可能被腾讯吞了或者帐号被冻结"))

    # 取群信息
    @staticmethod
    def get_group(q_group_id):
        response = requests.get(url=cqhttp_url + f"get_group_info?group_id={q_group_id}").text
        json_send = json.loads(response)
        return json_send["data"]["group_name"]

    # 撤回信息
    @staticmethod
    def del_msg(q_message_id):
        request = requests.get(url=cqhttp_url + f"delete_msg?message_id={q_message_id}").json()
        return request["status"]

    # 取用户信息
    @staticmethod
    def get_user_nickname(q_user_id):
        response = requests.get(url=cqhttp_url + f"get_stranger_info?user_id={q_user_id}&no_cache=true").text
        json_send = json.loads(response)
        q_user_name = json_send["data"]["nickname"]
        return q_user_name

    @staticmethod
    def get_user_group_card(q_user_id, q_group_id):
        response = requests.get(url=cqhttp_url + f"get_group_member_info?group_id={q_group_id}&user_id={q_user_id}&no_cache=false").text
        json_send = json.loads(response)
        q_user_group_card = ""
        if json_send["data"]["card"]:
            q_user_group_card = json_send["data"]["card"]
        else:
            start_thread(func=QQApi.get_user_nickname, args=(q_user_id,))
        return q_user_group_card

    # 取运行状态
    @staticmethod
    def get_status():
        response = requests.get(url=cqhttp_url + "get_status").json()
        return response

    @staticmethod
    def set_group_add_request(q_add_type, q_add_flag, q_add_approve, q_add_reason=''):
        request = requests.get(url=cqhttp_url + f"set_group_add_request?flag={q_add_flag}&approve={q_add_approve}&type={q_add_type}&reason={q_add_reason}").json()
        return request

    @staticmethod
    def set_group_ban(q_group_id, q_user_id, duration):
        request = requests.get(url=cqhttp_url + f"set_group_ban?group_id={q_group_id}&user_id={q_user_id}&duration={duration}")


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
        start_thread(func=plugin, args=(q_sub_type, q_post_type, q_message_type, q_message, q_group_id, q_nickname, q_card, q_user_id, q_message_id, q_add_flag, q_add_comment, q_all_group_id, q_all_user_id, q_all_user_nickname, data))


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
    class LogSP:
        now_time_and_day = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        now_time_and_day_file = time.strftime('%Y-%m-%d%H-%M-%S', time.localtime())

        @staticmethod
        def now_time():
            # 当前时间获取
            current_time = time.time()
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
            return now_time

        @staticmethod
        def save_log(logs):
            log_sp = LogSP()
            if not os.path.exists('logs'):
                os.mkdir('logs')
            with open(f'logs/{LogSP.now_time_and_day_file}.log', 'a') as f_0:
                f_0.write(f"{logs}\n")

        @staticmethod
        def print_log(logs):
            print(logs)
            LogSP.save_log(logs)

        @staticmethod
        def initialize(initialize_txt):
            log_sp = LogSP()
            # 设置群日志内容
            logs = f"[{log_sp.now_time()}] [初始] {initialize_txt}"
            # 显示日志
            print(logs)
            LogSP.save_log(logs)


    # 监测配置文件夹是否存在
    folders = ['plugins', 'logs', 'errors', 'config']

    LogSP.initialize("正在监测配置文件夹是否存在")
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            LogSP.initialize(f'文件夹 {folder} 不存在，已自动创建')
        else:
            LogSP.initialize(f'文件夹 {folder} 已经存在')

    # 配置文件路径
    config_path = "config/config.ini"

    # 如果配置文件不存在，则创建一个新的配置文件
    if not os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.add_section("go-cqhttp")
        config.set("go-cqhttp", "websocket_ip", "localhost")
        config.set("go-cqhttp", "websocket_port", "8080")
        config.set("go-cqhttp", "http_api_ip", "127.0.0.1")
        config.set("go-cqhttp", "http_api_port", "5700")
        with open(config_path, "w") as f:
            config.write(f)
        LogSP.initialize(f'配置文件 {config_path} 不存在，已自动创建')
        LogSP.initialize("已关闭程序，请重新启动以加载配置")
        sys.exit(0)
    else:
        LogSP.initialize(f'配置文件 {config_path} 已经存在')

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
