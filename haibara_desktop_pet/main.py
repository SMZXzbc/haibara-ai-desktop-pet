# -*- coding: utf-8 -*-
"""
桌面宠物 - 灰原哀
名侦探柯南主题桌面宠物，使用 MiMo API 提供对话和语音功能。

运行方式：python main.py
依赖安装：pip install PyQt5 requests openai pygame
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config_manager import load_config, get_api_key
from pet_window import PetWindow


def check_api_key():
    """检查 API Key 是否已设置"""
    api_key = get_api_key()
    if not api_key:
        app = QApplication.instance() or QApplication(sys.argv)
        msg = QMessageBox()
        msg.setWindowTitle("灰原哀 - 初始设置")
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            "欢迎使用桌面宠物！\n\n"
            "请先设置 MiMo API Key：\n\n"
            "方法一（推荐）：\n"
            "  设置环境变量 MIMO_API_KEY\n\n"
            "方法二：\n"
            "  在 config.json 中填写 api_key 字段\n\n"
            "API 获取地址：https://token-plan-cn.xiaomimimo.com\n\n"
            "设置完成后请重新启动程序。"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return False
    return True


def main():
    """程序入口"""
    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 检查 API Key
    if not check_api_key():
        sys.exit(0)

    # 创建并显示宠物窗口
    pet = PetWindow()
    pet.show()

    # 启动时显示问候语
    pet.show_bubble_text("嗯...又是你啊。有什么事吗？", 4000)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
