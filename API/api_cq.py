import re


def cq_replace(text):
    result = re.findall(r'\[CQ:(.*?)\]', text)
    replaces = {}
    for r in result:
        replaces[r] = "[" + r.split(",")[0].split(":")[-1] + "]"

    # 3. 使用 replace 函数进行替换
    for k, v in replaces.items():
        text = text.replace("[CQ:" + k + "]", v)
