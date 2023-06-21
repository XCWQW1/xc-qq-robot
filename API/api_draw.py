import os
import random
import time

from PIL import Image, ImageFont, ImageDraw

png_number = str(random.randint(1, 114514)) + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


def draw(txt, x, y, q_message_type, q_message_id, q_group_id, q_user_id):
    from API.api_qq import QQApi
    from API.api_thread import start_thread

    # 打开底图
    # img = Image.open('/home/xcwqw1/桌面/xcbot/IMG/input/menu.jpg')
    img = Image.new('RGB', (x, y), (255, 255, 255))  # 1100
    # 调用绘图在底图中添加文本
    i1 = ImageDraw.Draw(img)

    font = ImageFont.truetype('API/NotoSansSC-Black.otf', 30)

    # 绘制白色文本
    i1.text((10, 10), txt, font=font, fill='black')

    img.save("API/" + png_number + ".png")

    start_thread(func=QQApi.send, args=(q_message_type, f"[CQ:cardimage,file=file:///{os.getcwd()}/API/{str(png_number)}.png]", False, q_group_id, q_user_id))

    os.remove("API/" + png_number + ".png")
