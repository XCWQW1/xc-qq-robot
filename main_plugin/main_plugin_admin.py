import configparser
import os

from API.api_qq import QQApi

unload_plugin = []


def m_plugin_admin(plugin_admin, name_list, q_post_type, q_message_type, q_message, q_group_id, q_user_id, q_message_id):
    # 配置文件路径
    config_path = "config/config.ini"
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    unload_plugin = config.get("plugin_admin", "unload_plugin")

    if q_post_type == "message":
        if q_user_id == plugin_admin:
            if q_message == "#插件 帮助":
                plugin_help = "#插件 帮助 - 显示当前页面\n"\
                              "#插件 列表 - 显示当前检索到的插件\n"\
                              "#插件 启用 <插件名> - 启用某个插件\n"\
                              "#插件 禁用 <插件名> - 禁用某个插件"
                QQApi.send(q_message_type, plugin_help, False, int(q_group_id))

            if q_message == "#插件 列表":
                plugin_name_list = ''
                for plugin_name in name_list:
                    if plugin_name in unload_plugin:
                        plugin_stats = False
                    else:
                        plugin_stats = True

                    plugin_name_list += f'插件：[{plugin_name}] 状态：{str(plugin_stats).replace("True", "✓").replace("False", "✗")}\n'

                QQApi.send(q_message_type, "当前检索到的插件列表：\n" + plugin_name_list, False, int(q_group_id))
