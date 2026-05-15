# -*- coding: utf-8 -*-
"""
桌面宠物窗口模块
实现悬浮窗、动画状态、鼠标拖拽、对话气泡等功能。
支持角色图片显示，图片不存在时回退到纯色方块。
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QMenu, QAction, QDesktopWidget, QApplication,
    QGraphicsDropShadowEffect, QDialog, QLineEdit, QFormLayout,
    QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import (
    Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QRect, QRectF, QSize
)
from PyQt5.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QLinearGradient,
    QPainterPath, QCursor, QPixmap, QImage
)

from config_manager import load_config, update_window_position, set_muted
from chat_engine import chat
from voice_module import speak, stop_playback
from tools import detect_tool_command, execute_tool
import reminder

# 资源目录
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# 宠物状态定义（保留用于回退绘制和标签）
PET_STATES = {
    "idle":    {"color": QColor(173, 216, 230), "text": "灰原", "label": "待机"},
    "talk":    {"color": QColor(144, 238, 144), "text": "...",  "label": "说话"},
    "think":   {"color": QColor(255, 255, 224), "text": "?",    "label": "思考"},
    "tired":   {"color": QColor(216, 191, 216), "text": "Zzz",  "label": "困倦"},
    "serious": {"color": QColor(255, 182, 193), "text": "!",    "label": "认真"},
}


def _load_state_pixmaps():
    """
    加载各状态的角色图片
    返回: {state_name: QPixmap} 字典，加载失败的状态不包含在内
    """
    pixmaps = {}
    for state in PET_STATES:
        filename = f"haibara_{state}.png"
        filepath = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(filepath):
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                # 确保图片尺寸与窗口一致
                if pixmap.size() != QSize(200, 250):
                    pixmap = pixmap.scaled(200, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pixmaps[state] = pixmap
            else:
                print(f"[警告] 图片加载失败: {filepath}")
        else:
            print(f"[警告] 未找到图片: {filepath}")
    return pixmaps


class ChatBubble(QDialog):
    """对话气泡窗口"""

    message_sent = pyqtSignal(str)  # 发送消息信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(320)
        self._setup_ui()

    def _setup_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 气泡容器
        self.container = QWidget()
        self.container.setObjectName("bubble_container")
        self.container.setStyleSheet("""
            #bubble_container {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 12px;
                border: 1px solid #ccc;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(8)

        # 标题
        title = QLabel("灰原哀 - 对话")
        title.setStyleSheet("color: #555; font-weight: bold; font-size: 13px; border: none;")
        title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title)

        # 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                color: #333;
            }
        """)
        self.chat_display.setMinimumHeight(150)
        self.chat_display.setMaximumHeight(300)
        container_layout.addWidget(self.chat_display)

        # 输入区域
        input_layout = QHBoxLayout()

        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(60)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 6px;
                font-size: 12px;
            }
        """)
        self.input_field.setPlaceholderText("输入消息... (Enter 发送, Shift+Enter 换行)")
        self.input_field.installEventFilter(self)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(60, 60)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a5f9e;
            }
        """)
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        container_layout.addLayout(input_layout)
        layout.addWidget(self.container)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

    def eventFilter(self, obj, event):
        """处理回车发送"""
        if obj == self.input_field and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                self._on_send()
                return True
        return super().eventFilter(obj, event)

    def _on_send(self):
        """发送消息"""
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        self.input_field.clear()
        self.append_message("你", text)
        self.message_sent.emit(text)

    def append_message(self, sender, message):
        """添加消息到显示区域"""
        if sender == "你":
            html = f'<p style="text-align:right;"><span style="background:#dcf8c6;padding:4px 8px;border-radius:8px;">{message}</span></p>'
        else:
            html = f'<p style="text-align:left;"><span style="background:#e8e8e8;padding:4px 8px;border-radius:8px;">{message}</span></p>'
        self.chat_display.append(html)
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def show_at(self, pos):
        """在指定位置显示"""
        screen = QDesktopWidget().screenGeometry()
        x = min(pos.x(), screen.width() - self.width() - 10)
        y = min(pos.y() - self.height() - 10, screen.height() - self.height() - 10)
        self.move(max(10, x), max(10, y))
        self.show()
        self.activateWindow()


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(350, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.api_key_input = QLineEdit()
        config = load_config()
        current_key = config.get("api_key", "")
        if current_key:
            self.api_key_input.setText(current_key[:8] + "****")
            self.api_key_input.setReadOnly(True)
            hint = QLabel("（已通过环境变量或配置设置）")
            hint.setStyleSheet("color: #888; font-size: 11px;")
            layout.addRow("API Key:", hint)
        else:
            self.api_key_input.setPlaceholderText("输入 MiMo API Key")
            layout.addRow("API Key:", self.api_key_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _on_accept(self):
        key = self.api_key_input.text().strip()
        if key and not self.api_key_input.isReadOnly():
            from config_manager import set_api_key
            set_api_key(key)
        self.accept()


class PetWindow(QWidget):
    """桌面宠物主窗口"""

    # 状态变化信号
    state_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._current_state = "idle"
        self._drag_pos = None
        self._chat_bubble = None
        self._dots_timer = QTimer()
        self._dots_count = 0

        # 图片相关
        self._pixmaps = _load_state_pixmaps()
        self._use_images = len(self._pixmaps) > 0

        # 淡入淡出动画
        self._fade_opacity = 1.0        # 当前图片透明度
        self._fade_target = 1.0         # 目标透明度
        self._prev_pixmap = None        # 上一状态的图片（用于淡出）
        self._fade_timer = QTimer()
        self._fade_timer.timeout.connect(self._update_fade)
        self._fade_duration = 200       # 过渡时长 ms
        self._fade_step = 0             # 当前步数

        self._init_window()
        self._load_position()

        # 初始化提醒系统
        reminder.set_callback(self._on_reminder)
        reminder.start_checker()

        # 打印图片加载状态
        if self._use_images:
            loaded = list(self._pixmaps.keys())
            missing = [s for s in PET_STATES if s not in self._pixmaps]
            print(f"[信息] 已加载角色图片: {loaded}")
            if missing:
                print(f"[警告] 缺失图片（将使用回退绘制）: {missing}")
        else:
            print("[警告] 未找到角色图片，使用默认绘制")

    def _init_window(self):
        """初始化窗口属性"""
        # 无边框、透明背景、始终置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 250)

        # 点击动画用的计时器
        self._dots_timer.timeout.connect(self._update_dots)
        self._dots_timer.start(500)

    def _load_position(self):
        """加载上次保存的窗口位置"""
        config = load_config()
        x = config.get("window_x", 100)
        y = config.get("window_y", 100)
        # 确保在屏幕范围内
        screen = QDesktopWidget().screenGeometry()
        x = max(0, min(x, screen.width() - self.width()))
        y = max(0, min(y, screen.height() - self.height()))
        self.move(x, y)

    def _save_position(self):
        """保存当前窗口位置"""
        pos = self.pos()
        update_window_position(pos.x(), pos.y())

    def set_state(self, state):
        """切换宠物状态（带淡入淡出）"""
        if state not in PET_STATES or state == self._current_state:
            return

        # 保存旧图片用于淡出
        if self._use_images and self._current_state in self._pixmaps:
            self._prev_pixmap = self._pixmaps[self._current_state]
        else:
            self._prev_pixmap = None

        old_state = self._current_state
        self._current_state = state
        self.state_changed.emit(state)

        # 启动淡入淡出动画
        if self._use_images and (state in self._pixmaps or old_state in self._pixmaps):
            self._start_fade()
        else:
            self.update()

    def _start_fade(self):
        """启动淡入淡出动画"""
        self._fade_opacity = 0.0
        self._fade_step = 0
        total_steps = max(1, self._fade_duration // 16)  # 约 60fps
        self._fade_increment = 1.0 / total_steps
        self._fade_timer.start(16)

    def _update_fade(self):
        """更新淡入淡出动画"""
        self._fade_step += 1
        self._fade_opacity = min(1.0, self._fade_step * self._fade_increment)

        if self._fade_opacity >= 1.0:
            self._fade_timer.stop()
            self._prev_pixmap = None
            self._fade_opacity = 1.0

        self.update()

    def get_state(self):
        """获取当前状态"""
        return self._current_state

    def paintEvent(self, event):
        """绘制宠物外观"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 获取当前状态信息
        state_info = PET_STATES[self._current_state]

        if self._use_images:
            self._paint_with_images(painter, state_info)
        else:
            self._paint_fallback(painter, state_info)

        painter.end()

    def _paint_with_images(self, painter, state_info):
        """使用角色图片绘制"""
        current_pixmap = self._pixmaps.get(self._current_state)

        # 淡出旧图片
        if self._prev_pixmap and self._fade_opacity < 1.0:
            painter.setOpacity(1.0 - self._fade_opacity)
            x = (self.width() - self._prev_pixmap.width()) // 2
            y = (self.height() - self._prev_pixmap.height()) // 2
            painter.drawPixmap(x, y, self._prev_pixmap)

        # 绘制当前图片
        if current_pixmap:
            painter.setOpacity(self._fade_opacity)
            x = (self.width() - current_pixmap.width()) // 2
            y = (self.height() - current_pixmap.height()) // 2
            painter.drawPixmap(x, y, current_pixmap)
        elif self._prev_pixmap:
            # 当前状态无图片，继续显示旧图片
            painter.setOpacity(1.0)
            x = (self.width() - self._prev_pixmap.width()) // 2
            y = (self.height() - self._prev_pixmap.height()) // 2
            painter.drawPixmap(x, y, self._prev_pixmap)
        else:
            # 都没有，回退到纯色方块
            painter.setOpacity(1.0)
            self._paint_fallback(painter, state_info)

        # 重置透明度，绘制底部状态标签
        painter.setOpacity(1.0)
        painter.setPen(QColor(100, 100, 100))
        small_font = QFont("Microsoft YaHei", 9)
        painter.setFont(small_font)
        label_rect = QRect(25, 220, 150, 30)
        painter.drawText(label_rect, Qt.AlignCenter, state_info["label"])

    def _paint_fallback(self, painter, state_info):
        """回退绘制：纯色方块 + 文字（原始方案）"""
        color = state_info["color"]
        text = state_info["text"]

        # 绘制圆角矩形（身体）
        body_rect = QRectF(25, 20, 150, 180)
        path = QPainterPath()
        path.addRoundedRect(body_rect, 20, 20)

        # 渐变效果
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, color.lighter(110))
        gradient.setColorAt(1, color.darker(110))
        painter.fillPath(path, QBrush(gradient))

        # 边框
        painter.setPen(QPen(color.darker(130), 2))
        painter.drawPath(path)

        # 绘制"眼睛"（两个小圆点）
        eye_y = 80
        painter.setBrush(QColor(50, 50, 50))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(65, eye_y, 12, 12)
        painter.drawEllipse(123, eye_y, 12, 12)

        # 绘制文字标签
        painter.setPen(QColor(60, 60, 60))
        font = QFont("Microsoft YaHei", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(body_rect, Qt.AlignCenter, text)

        # 绘制底部小标签（状态名）
        painter.setPen(QColor(100, 100, 100))
        small_font = QFont("Microsoft YaHei", 9)
        painter.setFont(small_font)
        label_rect = QRect(25, 205, 150, 30)
        painter.drawText(label_rect, Qt.AlignCenter, state_info["label"])

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()
            event.accept()
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        """鼠标拖拽移动"""
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.LeftButton:
            # 如果几乎没有移动，视为点击
            if self._drag_pos:
                delta = event.globalPos() - (self.pos() + self._drag_pos)
                if abs(delta.x()) < 5 and abs(delta.y()) < 5:
                    self._on_click()
            self._drag_pos = None
            self._save_position()
            event.accept()

    def _on_click(self):
        """左键点击 - 打开对话气泡"""
        if self._chat_bubble is None:
            self._chat_bubble = ChatBubble(self)
            self._chat_bubble.message_sent.connect(self._handle_message)

        bubble_pos = QPoint(self.pos().x() + self.width() + 5, self.pos().y())
        self._chat_bubble.show_at(bubble_pos)

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
        """)

        settings_action = menu.addAction("设置")
        mute_text = "取消静音" if load_config().get("muted", False) else "静音"
        mute_action = menu.addAction(mute_text)
        menu.addSeparator()
        remind_action = menu.addAction("添加提醒")
        clear_action = menu.addAction("清空对话历史")
        menu.addSeparator()
        quit_action = menu.addAction("退出")

        action = menu.exec_(pos)

        if action == settings_action:
            self._show_settings()
        elif action == mute_action:
            self._toggle_mute()
        elif action == remind_action:
            self._show_add_reminder()
        elif action == clear_action:
            self._clear_history()
        elif action == quit_action:
            self._save_position()
            QApplication.quit()

    def _show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def _toggle_mute(self):
        """切换静音状态"""
        config = load_config()
        new_muted = not config.get("muted", False)
        set_muted(new_muted)
        if new_muted:
            self.show_bubble_text("已静音")
        else:
            self.show_bubble_text("已取消静音")

    def _show_add_reminder(self):
        """显示添加提醒对话框"""
        from PyQt5.QtWidgets import QInputDialog
        time_str, ok1 = QInputDialog.getText(self, "添加提醒", "时间 (HH:MM):")
        if not ok1 or not time_str:
            return
        content, ok2 = QInputDialog.getText(self, "添加提醒", "提醒内容:")
        if not ok2 or not content:
            return
        reminder.add_new_reminder(time_str, content)
        self.show_bubble_text(f"已添加提醒: {time_str}")

    def _clear_history(self):
        """清空对话历史"""
        from chat_engine import clear_history
        clear_history()
        if self._chat_bubble:
            self._chat_bubble.chat_display.clear()
        self.show_bubble_text("对话历史已清空")

    def _handle_message(self, text):
        """处理用户发送的消息"""
        import threading

        # 先检查是否是工具命令
        tool_cmd = detect_tool_command(text)
        if tool_cmd:
            tool_type, param = tool_cmd
            result = execute_tool(tool_type, param)
            if result:
                self.set_state("talk")
                if self._chat_bubble:
                    self._chat_bubble.append_message("灰原", result)
                speak(result, callback=lambda: self.set_state("idle"))
                return

        # 切换到思考状态
        self.set_state("think")

        # 在后台线程调用 API
        def api_call():
            reply, error = chat(text)
            if error:
                # API 失败
                self.set_state("tired")
                error_text = "...连接似乎不太稳定"
                if self._chat_bubble:
                    self._chat_bubble.append_message("灰原", error_text)
                speak(error_text, callback=lambda: self.set_state("idle"))
            else:
                # API 成功
                self.set_state("talk")
                if self._chat_bubble:
                    self._chat_bubble.append_message("灰原", reply)
                speak(reply, callback=lambda: self.set_state("idle"))

        thread = threading.Thread(target=api_call, daemon=True)
        thread.start()

    def show_bubble_text(self, text, duration=3000):
        """在宠物旁边显示临时文本气泡"""
        # 创建临时标签
        label = QLabel(text, self)
        label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid #aaa;
                border-radius: 8px;
                padding: 6px 10px;
                color: #333;
                font-size: 12px;
            }
        """)
        label.setWordWrap(True)
        label.setMaximumWidth(180)
        label.adjustSize()
        label.move(-label.width() - 10, 20)
        label.show()

        # 定时关闭
        QTimer.singleShot(duration, label.deleteLater)

    def _on_reminder(self, message):
        """提醒触发回调"""
        self.set_state("serious")
        self.show_bubble_text(message, 5000)
        speak(message, callback=lambda: self.set_state("idle"))
        # 如果对话框打开，也显示在对话框中
        if self._chat_bubble and self._chat_bubble.isVisible():
            self._chat_bubble.append_message("灰原", message)

    def _update_dots(self):
        """更新说话动画的省略号"""
        if self._current_state == "talk":
            self._dots_count = (self._dots_count + 1) % 4
            dots = "." * self._dots_count if self._dots_count > 0 else ""
            PET_STATES["talk"]["text"] = dots if dots else "..."
            self.update()

    def closeEvent(self, event):
        """窗口关闭事件"""
        self._save_position()
        reminder.stop_checker()
        stop_playback()
        from voice_module import cleanup
        cleanup()
        event.accept()
