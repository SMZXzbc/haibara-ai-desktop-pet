# -*- coding: utf-8 -*-
"""
定时提醒模块
管理提醒列表，定时检查并触发提醒。
"""
# 需要安装: pip install schedule

import time
import threading
from datetime import datetime
from config_manager import get_reminders, add_reminder, remove_reminder, load_config

# 提醒回调函数（由主窗口设置）
_reminder_callback = None
# 提醒检查线程
_checker_thread = None
_running = False


def set_callback(callback):
    """设置提醒触发时的回调函数"""
    global _reminder_callback
    _reminder_callback = callback


def start_checker():
    """启动提醒检查线程"""
    global _checker_thread, _running
    if _running:
        return
    _running = True
    _checker_thread = threading.Thread(target=_check_loop, daemon=True)
    _checker_thread.start()


def stop_checker():
    """停止提醒检查"""
    global _running
    _running = False


def _check_loop():
    """提醒检查循环"""
    global _running
    already_triggered = set()  # 已触发的提醒（避免重复触发）

    while _running:
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")

            reminders = get_reminders()
            for i, reminder in enumerate(reminders):
                if not reminder.get("active", True):
                    continue

                # 生成唯一标识（日期+时间+内容）
                trigger_id = f"{current_date}_{reminder['time']}_{reminder['content']}"

                if reminder["time"] == current_time and trigger_id not in already_triggered:
                    already_triggered.add(trigger_id)
                    # 触发提醒
                    if _reminder_callback:
                        msg = _format_reminder(reminder["time"], reminder["content"])
                        _reminder_callback(msg)

            # 每分钟清理一次已触发记录（新的一天）
            if now.second == 0:
                already_triggered.clear()

        except Exception as e:
            print(f"提醒检查出错: {e}")

        time.sleep(30)  # 每 30 秒检查一次


def _format_reminder(time_str, content):
    """格式化提醒消息（灰原语气）"""
    templates = [
        f"已经{time_str}了，你不是说要{content}吗？",
        f"提醒你一下，{time_str}了。{content}——需要我再说一遍吗？",
        f"时间到了，{time_str}。{content}。别告诉我你忘了。",
        f"…{time_str}了。{content}，对吧？去吧。"
    ]
    import random
    return random.choice(templates)


def add_new_reminder(time_str, content):
    """添加新提醒"""
    return add_reminder(time_str, content)


def remove_reminder_by_index(index):
    """删除指定提醒"""
    remove_reminder(index)


def get_all_reminders():
    """获取所有提醒"""
    return get_reminders()


def format_reminder_list():
    """格式化提醒列表为可读文本"""
    reminders = get_reminders()
    if not reminders:
        return "当前没有设置提醒。"

    lines = ["提醒列表："]
    for i, r in enumerate(reminders):
        status = "✓" if r.get("active", True) else "✗"
        lines.append(f"  {i+1}. [{status}] {r['time']} - {r['content']}")
    return "\n".join(lines)
