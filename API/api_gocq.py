# -*- coding:utf-8 -*-
# @FileName :api_gocq.py
# @Time     : 3:00
# @Author   :Endermite
import requests
import urllib.parse
import configparser

config_path = "config/config.ini"

if os.path.exists(config_path):
    # 配置文件路径
    config_path = "config/config.ini"

    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    # 获取相应的配置信息
    http_api_ip = config.get("go-cqhttp", "http_api_ip")
    http_api_port = config.get("go-cqhttp", "http_api_port")
    cqhttp_url = F"http://{http_api_http_api_ip}:{http_api_http_api_port}/"


class CQApi:
    class Message:
        """
        有关消息操作的 API
        """

        @staticmethod
        def send_private_msg(user_id: int, group_id: int, message: str, auto_escape: bool = False):
            """
            发送私聊消息
            @param user_id:对方 QQ 号
            @param group_id:主动发起临时会话时的来源群号(可选, 机器人本身必须是管理员/群主)
            @param message:要发送的内容
            @param auto_escape:消息内容是否作为纯文本发送 ( 即不解析 CQ 码 ) , 只在 message 字段是字符串时有效
            """
            params = {
                'user_id': user_id,
                'group_id': group_id,
                'message': message,
                'auto_escape': auto_escape,
            }
            url = cqhttp_url + "send_private_msg?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def send_group_msg(group_id: int, message: str, auto_escape: bool = False):
            """
            发送群聊消息
            @param group_id:群号
            @param message:要发送的内容
            @param auto_escape:消息内容是否作为纯文本发送 ( 即不解析 CQ 码 ) , 只在 message 字段是字符串时有效
            """
            params = {
                'group_id': group_id,
                'message': message,
                'auto_escape': auto_escape,
            }
            url = cqhttp_url + "send_group_msg?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def send_msg(user_id: int = None, group_id: int = None, message: str = "", message_type: str = "",
                     auto_escape: bool = False):
            """
            发送消息
            @param user_id:对方 QQ 号 ( 消息类型为 private 时需要 )
            @param group_id:群号 ( 消息类型为 group 时需要 )
            @param message:要发送的内容
            @param message_type:消息类型, 支持 private、group , 分别对应私聊、群组, 如不传入, 则根据传入的 *_id 参数判断
            @param auto_escape:	消息内容是否作为纯文本发送 ( 即不解析 CQ 码 ) , 只在 message 字段是字符串时有效
            """
            if message_type == "" and user_id is not None and group_id is None:
                message_type = "private"
            elif message_type == "" and user_id is not None and group_id is not None:
                message_type = "private"
            elif message_type == "" and group_id is not None and user_id is None:
                message_type = "group"
            if message_type == "private":
                params = {
                    'user_id': user_id,
                    'message': message,
                    'group_id': group_id,
                    'auto_escape': auto_escape,
                }
                url = cqhttp_url + "send_private_msg?" + urlencode(params)
                response = requests.get(url=url)
                return response.text

            elif message_type == "group":
                params = {
                    'group_id': group_id,
                    'message': message,
                    'auto_escape': auto_escape,
                }
                url = cqhttp_url + "send_group_msg?" + urlencode(params)
                response = requests.get(url=url)
                return response.text

        @staticmethod
        def get_msg(message_id: int):
            """
            获取消息
            @param message_id:消息 ID
            """
            params = {
                'message_id': message_id,
            }
            url = cqhttp_url + "get_msg?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def delete_msg(message_id: int):
            """
            撤回消息
            @param message_id:消息 ID
            """
            params = {
                'message_id': message_id,
            }
            url = cqhttp_url + "delete_msg?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def mark_msg_as_read(message_id: int):
            """
            标记消息已读
            @param message_id: 消息 ID
            """
            params = {
                'message_id': message_id,
            }
            url = cqhttp_url + "mark_msg_as_read?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def get_forward_msg(message_id: int):
            """
            获取合并转发内容
            @param message_id:消息 ID
            """
            params = {
                'message_id': message_id,
            }
            url = cqhttp_url + "get_forward_msg?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def send_group_forward_msg(group_id: int, messages: list):
            """
            发送合并转发 ( 群聊 )
            @param group_id:群号
            @param messages:自定义转发消息
            """
            params = {
                'group_id': group_id,
                'messages': messages,
            }
            url = cqhttp_url + "send_group_forward_msg?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def send_private_forward_msg(user_id: int, messages: list):
            """
            发送合并转发 ( 好友 )
            @param user_id:好友QQ号
            @param messages:自定义转发消息
            """
            params = {
                'user_id': user_id,
                'messages': messages,
            }
            url = cqhttp_url + "send_private_forward_msg?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def get_group_msg_history(message_seq: int, group_id: int):
            """
            获取群消息历史记录
            @param message_seq:起始消息序号, 可通过 get_msg 获得
            @param group_id:群号
            """
            params = {
                'message_seq': message_seq,
                'group_id': group_id,
            }
            url = cqhttp_url + "get_group_msg_history?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

    class Bot:
        """
        有关 Bot 账号的相关 API
        """

        @staticmethod
        def get_login_info():
            """
            获取登录号信息
            """
            url = cqhttp_url + "get_login_info"
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def set_qq_profile(nickname: str, company: str, email: str, college: str, personal_note: str):
            """
            设置登录号资料
            @param nickname:名称
            @param company:公司
            @param email:邮箱
            @param college:学校
            @param personal_note:个人说明
            """
            params = {
                'nickname': nickname,
                'company': company,
                'email': email,
                'college': college,
                'personal_note': personal_note,
            }
            url = cqhttp_url + "set_qq_profile?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def qidian_get_account_info():
            """
            获取企点账号信息，该API只有企点协议可用
            """
            url = cqhttp_url + "qidian_get_account_info"
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def _get_model_show(model: str):
            """
            获取在线机型
            @param model:机型名称
            """
            params = {
                'model': model,
            }
            url = cqhttp_url + "_get_model_show?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def _set_model_show(model: str, model_show: str):
            """
            设置在线机型
            @param model:机型名称
            @param model_show:
            """
            params = {
                'model': model,
                'model_show': model_show,
            }
            url = cqhttp_url + "_set_model_show?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def get_online_clients(no_cache: bool):
            """
            获取当前账号在线客户端列表
            @param no_cache:是否无视缓存
            """
            params = {
                'no_cache': no_cache,
            }
            url = cqhttp_url + "get_online_clients?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

    class Image:
        """
        图片相关 API
        """

        @staticmethod
        def get_image(file: str):
            """
            获取图片信息
            @param file:图片缓存文件名
            """
            params = {
                'file': file,
            }
            url = cqhttp_url + "get_image?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def can_send_image():
            """
            检查是否可以发送图片
            """
            url = cqhttp_url + "can_send_image"
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def ocr_image(image: str):
            """
            图片 OCR
            @param image:图片ID
            """
            params = {
                'image': image,
            }
            url = cqhttp_url + ".ocr_image?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

    class Voice:
        """
        语音相关 API
        """
        @staticmethod
        def get_record(file: str, out_format: str):
            """
            获取语音
            @param file:收到的语音文件名（消息段的 file 参数）, 如 0B38145AA44505000B38145AA4450500.silk
            @param out_format:要转换到的格式, 目前支持 mp3、amr、wma、m4a、spx、ogg、wav、flac
            """
            params = {
                'file': file,
                'out_format': out_format,
            }
            url = cqhttp_url + "get_record?" + urlencode(params)
            response = requests.get(url=url)
            return response.text

        @staticmethod
        def can_send_record():
            """
            检查是否可以发送语音
            """
            url = cqhttp_url + "can_send_record"
            response = requests.get(url=url)
            return response.text
