# -*- coding: utf-8 -*-
"""
配置管理模块
负责读写 config.json，保存用户设置、窗口位置、提醒列表等。
"""

import json
import os

# 默认配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# 默认配置
DEFAULT_CONFIG = {
    "window_x": 100,           # 窗口 X 坐标
    "window_y": 100,           # 窗口 Y 坐标
    "muted": False,            # 是否静音
    "api_key": "",             # MiMo API Key（优先从环境变量读取）
    "reminders": [],           # 提醒列表 [{"time": "14:00", "content": "复习线性代数", "active": true}]
    "conversation_history": [] # 对话历史（最近 5 轮）
}


def load_config():
    """加载配置文件，不存在则创建默认配置"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 补充缺失的默认字段
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    except (json.JSONDecodeError, IOError):
        # 配置文件损坏时重建
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"保存配置失败: {e}")


def get_api_key():
    """获取 API Key，优先从环境变量读取"""
    env_key = os.environ.get("MIMO_API_KEY", "")
    if env_key:
        return env_key
    config = load_config()
    return config.get("api_key", "")


def update_window_position(x, y):
    """更新窗口位置"""
    config = load_config()
    config["window_x"] = x
    config["window_y"] = y
    save_config(config)


def set_muted(muted):
    """设置静音状态"""
    config = load_config()
    config["muted"] = muted
    save_config(config)


def add_reminder(time_str, content):
    """添加提醒"""
    config = load_config()
    config["reminders"].append({
        "time": time_str,
        "content": content,
        "active": True
    })
    save_config(config)
    return len(config["reminders"]) - 1


def remove_reminder(index):
    """删除指定索引的提醒"""
    config = load_config()
    if 0 <= index < len(config["reminders"]):
        config["reminders"].pop(index)
        save_config(config)


def get_reminders():
    """获取所有提醒"""
    config = load_config()
    return config.get("reminders", [])


def save_conversation_history(history):
    """保存对话历史（最多保留 5 轮）"""
    config = load_config()
    config["conversation_history"] = history[-10:]  # 保留最近 10 条消息（5 轮对话）
    save_config(config)


def load_conversation_history():
    """加载对话历史"""
    config = load_config()
    return config.get("conversation_history", [])


def set_api_key(key):
    """手动设置 API Key"""
    config = load_config()
    config["api_key"] = key
    save_config(config)
