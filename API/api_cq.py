import re


def replace_cq_content(text):
    pattern = r'\[CQ:(\w+)(?:,[^\]]+)?\]'
    replaced_text = re.sub(pattern, r'[\1]', text)
    return replaced_text
