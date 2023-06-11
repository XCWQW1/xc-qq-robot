import queue
import threading
import time
import traceback


def start_thread(func, args):
    from API.api_log import Log
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
        now_time_and_day = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
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
