import signal
import sys
import time
import asyncio

from art import text2art

from API.api_log import Log, LogSP
from API.api_thread import start_thread
from init.main_init import main_init
from colorama import init, Fore, Style

# 初始化colorama
init()

if __name__ == '__main__':
    current_time = time.time()
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
    art_text = text2art('XCBOT')

    # 拆分艺术字的每一行，并在每行前面添加当前时间
    art_lines = art_text.split('\n')
    art_with_time = [f"[{now_time}] [初始]" + ' ' + line for line in art_lines]

    # 将带有时间的每行重新组合成一个字符串
    result = '\n'.join(art_with_time)

    print(Fore.GREEN + result + Style.RESET_ALL)
    # 初始化
    main_init()
    from framework.go_cqhttp import connect_to_go_cqhttp_server

    # 设置Ctrl+C的信号处理函数
    def signal_handler(sig, frame):
        current_time_1 = time.time()
        now_time_1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time_1))
        logs = f"[{now_time_1}] [信息] 程序已关闭"
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
        Log.error("error", "您输入的框架名不存在")


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
