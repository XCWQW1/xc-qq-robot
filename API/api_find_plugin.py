import importlib
import os
import sys

from API.api_log import Log


def list_plugins():
    # 插件列表
    p_plugin_list = []
    p_name_list = []
    Log.initialize("检测插件中...")
    Log.initialize("PS：插件中只有go-cqhttp发送来json才会调用此时只是导入了内存地址")

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
        Log.initialize(f"检测到插件：{name}")
        # 动态导入模块
        loader = importlib.machinery.SourceFileLoader(name, os.path.join(plugins_file, plugin_file))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)

        # 将插件函数添加到列表中
        p_plugin_list.append(module.plugin)
        p_name_list.append(name)

    return p_plugin_list, p_name_list
