from peewee import *


def plugin(q_sub_type, q_post_type, q_message_type, q_message, q_group_id, q_nickname, q_card, q_user_id, q_message_id, q_add_flag, q_add_comment, q_add_group_id, q_add_user_id, q_add_user_nickname, go_cqhttp_json):
    from main import start_thread, QQApi, Log
    if q_post_type == "message":
        # 数据库信息
        db = MySQLDatabase('qqbot', user='qqbot', password='QQbot.&BotQQ.114514', host='localhost', port=3306)

        # 权限指令：
        admin_id = ["1060524614", "3539757707"]
        if q_user_id in admin_id:
            if len(q_message) > 4 and q_message[:4] == "SAY ":
                start_thread(func=QQApi.send,
                             args=(q_message_type, q_message.split("SAY ")[1], False, q_group_id, q_user_id, q_nickname))
            # 测试指令
            if q_message == "TEST":
                start_thread(func=QQApi.send,
                             args=(q_message_type, "测试中...", False, q_group_id, q_user_id, q_nickname))
                start_thread(func=QQApi.send,
                             args=(q_message_type, "(1\\2)消息发送正常", False, q_group_id, q_user_id, q_nickname))

                # 检测数据库连接是否正常
                try:
                    db.connect()
                    start_thread(func=QQApi.send,
                                 args=(q_message_type, "(2\\2)数据库链接正常", False, q_group_id, q_user_id, q_nickname))
                except Exception as e:
                    start_thread(func=QQApi.send,
                                 args=(q_message_type, "(2\\2)数据库连接异常请查看控制台查看报错", False, q_group_id, q_user_id, q_nickname))

                    Log.error(q_message_type, "数据库连接错误：{}".format(e))
            if q_message == "运行状态":
                status = start_thread(func=QQApi.get_status, args=())
                statu_sent = status["data"]["stat"]["message_sent"]
                statu_received = status["data"]["stat"]["message_received"]
                status_txt = f"运行状态：\n接受消息：{statu_received} 条\n发送消息：{statu_sent} 条"
                start_thread(func=QQApi.send,
                             args=(q_message_type, status_txt, False, q_group_id, q_user_id, q_nickname))
        else:
            admin_com = ["TEST", "运行状态"]
            if q_message in admin_com:
                start_thread(func=QQApi.send,
                             args=(q_message_type, "对不起，您没有权限执行当前指令", False, q_group_id, q_user_id, q_nickname))
            if len(q_message) > 4 and q_message[:4] == "SAY ":
                start_thread(func=QQApi.send,
                             args=(q_message_type, "对不起，您没有权限执行当前指令", False, q_group_id, q_user_id, q_nickname))

        # 随机表情包
        if q_message == "随机表情":
            start_thread(func=QQApi.send,
                         args=(q_message_type, "[CQ:cardimage,file=http://192.168.5.244/api/packages/,cache=0]", False, q_group_id, q_user_id))


"""    # 检测消息前是否带有触发词#
    if len(q_message) > 1 and q_message[:1] == "#":

        # 吧消息去除#后处理
        x_message = q_message.split("#")[1]"""

"""    # 点歌指令
    if len(q_message) > 3 and q_message[:3] == "点歌 ":
        request = requests.get(
            url="http://localhost:3000/search?type=1&limit=10&keywords=" + q_message.split("点歌 ")[1]).text
        json_music = json.loads(request)
        music = str(json_music["result"]["songs"][0]["id"])
        start_thread(func=QQApi.send,
                     args=(q_message_type, f"[CQ:music,type=163,id={music}]", False, q_group_id, q_user_id))"""
