import configparser
import json
import os

import requests

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
        """
        发送消息
        @param q_message_type:group / private 消息类型
        @param send_msg:要发送的内容
        @param auto_escape:消息内容是否作为纯文本发送 ( 即不解析 CQ 码 )
        @param q_group_id:群号
        @param q_user_id:QQ 号
        @param q_user_name:昵称
        @return:
        """
        from API.api_log import Log
        from API.api_thread import start_thread
        if q_message_type == "group":
            # 发送信息
            response = requests.get(url=cqhttp_url + f"send_msg?group_id={q_group_id}&message={send_msg}&auto_escape={auto_escape}").text

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
                             args=(send_msg, q_message_type, q_group_id, q_message_id, q_group_name, q_user_id,))

            else:
                start_thread(func=Log.error,
                             args=(q_message_type, "消息发送失败，可能消息过长也可能是被腾讯吞了或者帐号被冻结"))
                requests.get(url=cqhttp_url + f"send_msg?group_id={q_group_id}&message=消息发送失败")

            # 返回消息ID
            return q_message_id
        elif q_message_type == "private":
            # 发送信息
            response = requests.get(url=cqhttp_url + f"send_msg?user_id={q_user_id}&message={send_msg}&auto_escape={auto_escape}").text

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
        """
        获取群名称
        @param q_group_id:群号
        @return:
        """
        response = requests.get(url=cqhttp_url + f"get_group_info?group_id={q_group_id}").text
        json_send = json.loads(response)
        return json_send["data"]["group_name"]

    # 撤回信息
    @staticmethod
    def del_msg(q_message_id):
        """
        撤回消息
        @param q_message_id:消息 ID
        @return:
        """
        request = requests.get(url=cqhttp_url + f"delete_msg?message_id={q_message_id}").json()
        return request["status"]

    # 取用户信息
    @staticmethod
    def get_user_nickname(q_user_id):
        """
        获取用户昵称
        @param q_user_id:QQ 号
        @return:
        """
        response = requests.get(url=cqhttp_url + f"get_stranger_info?user_id={q_user_id}&no_cache=true").text
        json_send = json.loads(response)
        q_user_name = json_send["data"]["nickname"]
        return q_user_name

    @staticmethod
    def get_user_group_card(q_user_id, q_group_id):
        """
        获取群成员名片／备注
        @param q_user_id:QQ 号
        @param q_group_id:群号
        @return:
        """
        from API.api_thread import start_thread
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
        """
        获取Go-CqHttp状态
        @return:
        """
        response = requests.get(url=cqhttp_url + "get_status").json()
        return response

    @staticmethod
    def set_group_add_request(q_add_type, q_add_flag, q_add_approve, q_add_reason=''):
        """
        处理加群请求／邀请
        @param q_add_type:请求类型
        @param q_add_flag:加群请求的 flag
        @param q_add_approve:是否同意请求／邀请
        @param q_add_reason:拒绝理由
        @return:
        """
        request = requests.get(url=cqhttp_url + f"set_group_add_request?flag={q_add_flag}&approve={q_add_approve}&type={q_add_type}&reason={q_add_reason}").json()
        return request

    @staticmethod
    def set_group_ban(q_group_id, q_user_id, duration):
        """
        群单人禁言
        @param q_group_id:群号
        @param q_user_id:目标QQ 号
        @param duration:禁言时长
        @return:
        """
        request = requests.get(url=cqhttp_url + f"set_group_ban?group_id={q_group_id}&user_id={q_user_id}&duration={duration}")
