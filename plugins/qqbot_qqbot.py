# 一个示例插件


def plugin(q_sub_type, q_post_type, q_message_type, q_message, q_group_id, q_group_name, q_nickname, q_card, q_user_id, q_message_id, q_group_member_flag, q_group_member_comment, q_group_member_group_id, q_group_member_user_id, q_group_member_user_nickname, q_group_member_operator_id, q_group_member_operator_nickname, go_cqhttp_json):
    from API.api_qq import QQApi
    from API.api_thread import start_thread
    if q_post_type == "message":
        # 权限指令：
        admin_id = ["3539757707"]
        if q_user_id in admin_id:
            if len(q_message) > 4 and q_message[:4] == "SAY ":
                start_thread(func=QQApi.send,
                             args=(q_message_type, q_message.split("SAY ")[1], False, q_group_id, q_user_id, q_nickname))
            # 测试指令
            if q_message == "TEST":
                start_thread(func=QQApi.send,
                             args=(q_message_type, "测试中...", False, q_group_id, q_user_id, q_nickname))
                start_thread(func=QQApi.send,
                             args=(q_message_type, "(1\\1)消息发送正常", False, q_group_id, q_user_id, q_nickname))
                
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
