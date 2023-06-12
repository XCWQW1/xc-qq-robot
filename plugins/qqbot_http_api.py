import configparser
import logging
import os
import sys
import threading

from API.flask import request
from API.api_log import LogSP, Log
from API.api_qq import QQApi


def plugin(q_sub_type, q_post_type, q_message_type, q_message, q_group_id, q_group_name, q_nickname, q_card, q_user_id, q_message_id, q_add_flag, q_add_comment, q_add_group_id, q_add_user_id, q_add_user_nickname, go_cqhttp_json):
    pass


class LogApi:
    @staticmethod
    def info(info):
        log = f"[{LogSP.now_time()}] [信息] [接口] {info}"
        print(log)


def http_api():
    from API.flask import Flask

    app = Flask(__name__)

    # 配置日志记录器，将日志级别设置为更高级别以隐藏错误信息
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # 禁止将日志消息传播到父记录器
    log.propagate = False

    # 禁用 Flask 的默认启动日志
    cli_logger = logging.getLogger('werkzeug')
    cli_logger.setLevel(logging.ERROR)

    @app.route('/', methods=['GET'])
    def none_req():
        return_txt = "无效接口"
        LogApi.info(f"[接受] 来自：{request.remote_addr}，请求方法：{request.method}，访问：{request.url}，返回：{return_txt}")
        return return_txt

    @app.route('/send', methods=['GET'])
    def send():
        # 获取 URL 参数
        group_id = request.args.get('group_id')
        message = request.args.get('message')
        message_type = request.args.get('message_type')
        if group_id and message and message_type:
            # 两个参数都存在，执行相应操作
            send_message_id = QQApi.send(q_message_type=message_type, send_msg=message, q_group_id=group_id, auto_escape=False)
            return_txt = {"message_id": send_message_id, "stats": "ok"}
        else:
            # 两个参数都不存在或者有一个参数不存在，返回错误信息
            return_txt = {"stats": "failed", "error": "missing parameter"}
        LogApi.info(f"[接受] 来自：{request.remote_addr}，请求方法：{request.method}，访问：{request.url}，返回：{return_txt}")
        return return_txt

    LogSP.initialize(f'[HTTP_API] 正在启动http api服务于地址：{http_api_ip}，端口：{http_api_port}')
    try:
        app.run(host=http_api_ip, port=http_api_port)
    except Exception as e:
        Log.error(error_txt=f'[HTTP API] 错误信息：{e}', q_message_type="error")


if __import__:
    # 监测配置文件夹是否存在
    folders = ['plugins/qqbot_http_api']

    LogSP.initialize("[HTTP_API] 正在监测配置文件夹是否存在")
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            LogSP.initialize(f'[HTTP_API] 文件夹 {folder} 不存在，已自动创建')
        else:
            LogSP.initialize(f'[HTTP_API] 文件夹 {folder} 已经存在')
    # 配置文件路径
    config_path = "plugins/qqbot_http_api/config.ini"

    # 如果配置文件不存在，则创建一个新的配置文件
    if not os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.add_section("bot_http_api")
        config.set("bot_http_api", "http_api_ip", "127.0.0.1")
        config.set("bot_http_api", "http_api_port", "5000")
        with open(config_path, "w") as f:
            config.write(f)
        LogSP.initialize(f'[HTTP_API] 配置文件 {config_path} 不存在，已自动创建')
        LogSP.initialize("[HTTP_API] 已关闭程序，请重新启动以加载配置")
        sys.exit(0)
    else:
        LogSP.initialize(f'[HTTP_API] 配置文件 {config_path} 已经存在')

    # 读取配置文件
    c_config = configparser.ConfigParser()
    c_config.read(config_path)

    # 获取相应的配置信息
    http_api_ip = c_config.get("bot_http_api", "http_api_ip")
    http_api_port = int(c_config.get("bot_http_api", "http_api_port"))

    # 创建新线程
    t = threading.Thread(target=http_api)

    # 设置线程为守护线程
    t.setDaemon(True)

    # 启动线程
    t.start()
