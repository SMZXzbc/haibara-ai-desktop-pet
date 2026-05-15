# -*- coding: utf-8 -*-
"""
快捷工具模块
提供天气查询、时间获取、打开系统应用等功能。
"""
# 需要安装: pip install requests

import os
import subprocess
import webbrowser
import requests
from datetime import datetime


def get_current_time():
    """获取当前时间"""
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")


def get_weather(city="auto"):
    """
    查询天气（使用 wttr.in 免费 API）
    city: 城市名，默认自动检测
    """
    try:
        url = f"https://wttr.in/{city}?format=%l:+%c+%t+%h+%w&lang=zh"
        response = requests.get(url, timeout=10)
        response.encoding = "utf-8"
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "天气查询失败，请稍后再试。"
    except Exception as e:
        return f"网络连接异常: {e}"


def open_calculator():
    """打开系统计算器"""
    try:
        if os.name == "nt":  # Windows
            subprocess.Popen("calc.exe")
        else:  # macOS / Linux
            subprocess.Popen(["gnome-calculator"])
        return "已打开计算器。"
    except Exception as e:
        return f"打开计算器失败: {e}"


def open_browser(url=None):
    """打开默认浏览器"""
    try:
        if url:
            webbrowser.open(url)
        else:
            webbrowser.open("about:blank")
        return "已打开浏览器。"
    except Exception as e:
        return f"打开浏览器失败: {e}"


def detect_tool_command(text):
    """
    检测用户输入中的工具命令
    返回: (命令类型, 参数) 或 None
    """
    text = text.lower().strip()

    if "几点" in text or "时间" in text or "现在几点" in text:
        return ("time", None)

    if "天气" in text or "气温" in text or "温度" in text:
        # 尝试提取城市名
        city = _extract_city(text)
        return ("weather", city)

    if "计算器" in text or "calc" in text:
        return ("calculator", None)

    if "浏览器" in text or "browser" in text:
        url = _extract_url(text)
        return ("browser", url)

    return None


def _extract_city(text):
    """从文本中提取城市名"""
    # 简单提取逻辑
    keywords = ["天气", "气温", "温度"]
    for kw in keywords:
        if kw in text:
            idx = text.index(kw)
            city = text[:idx].strip()
            if city and len(city) <= 10:
                return city
    return "auto"


def _extract_url(text):
    """从文本中提取 URL"""
    import re
    urls = re.findall(r'https?://\S+', text)
    return urls[0] if urls else None


def execute_tool(tool_type, param=None):
    """执行工具命令并返回结果"""
    if tool_type == "time":
        return get_current_time()
    elif tool_type == "weather":
        return get_weather(param or "auto")
    elif tool_type == "calculator":
        return open_calculator()
    elif tool_type == "browser":
        return open_browser(param)
    else:
        return None
