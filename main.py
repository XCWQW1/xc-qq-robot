import signal
import sys
import time
import asyncio

from API.api_log import Log, LogSP
from API.api_thread import start_thread
from init.main_init import main_init


if __name__ == '__main__':
    # 初始化
    main_init()
    from framework.go_cqhttp import connect_to_go_cqhttp_server
    LogSP.initialize("正在准备连接框架...")

    # 设置Ctrl+C的信号处理函数
    def signal_handler(sig, frame):
        current_time = time.time()
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
        logs = f"[{now_time}] [信息] 程序已关闭"
        LogSP.print_log(logs)
        start_thread(func=LogSP.save_log, args=(logs,))
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) > 1:
        framework = sys.argv[1:]
    else:
        framework = ["go-cqhttp"]
        Log.initialize(f"由于您没有输入参数，默认选择go-cqhttp框架")

    if framework[0] in ["icqq", "go-cqhttp"]:
        Log.initialize(f"当前准备对接的框架是：{framework[0]}")
        if framework[0] == "go-cqhttp":
            loop = asyncio.get_event_loop()
            loop.run_until_complete(connect_to_go_cqhttp_server())
        elif framework[0] == "icqq":
            Log.error("error", "我不会，长大后再制作")
    else:
        Log.error("error", "您输入的框架名不存在或未对接")


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
