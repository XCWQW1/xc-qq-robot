import base64
import io
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

    # 将图片转换为字节流
    image_byte_array = io.BytesIO()
    img.save(image_byte_array, format='PNG')

    # 获取字节流的内容
    image_bytes = image_byte_array.getvalue()

    # 将字节流编码为base64字符串
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    start_thread(func=QQApi.send, args=(q_message_type, f"[CQ:cardimage,file=base64://{base64_image}]", False, q_group_id, q_user_id))
