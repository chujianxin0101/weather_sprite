# -*- coding: utf-8 -*-
"""
天气精灵 - Weather Sprite
一款优雅轻量的Windows桌面养成游戏
完全透明，融入桌面
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QMenu,
                             QSystemTrayIcon, QDialog, QVBoxLayout,
                             QHBoxLayout, QPushButton, QGridLayout, QWidget,
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QAction, QCursor, QColor, QPainter, QBrush, QPainterPath, QFontMetrics

from weather_api import WeatherManager
from sprite import Sprite
from config import Config


class WeatherForecastDialog(QDialog):
    """天气预告面板 - 显示未来几小时天气预报"""

    def __init__(self, weather_manager, parent=None):
        super().__init__(parent)
        self.weather_manager = weather_manager
        self.setFixedSize(260, 320)
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_ui()
        QTimer.singleShot(100, self.load_forecast)

    def setup_ui(self):
        """设置UI"""
        # 主容器
        self.container = QWidget(self)
        self.container.setFixedSize(260, 320)
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(28, 28, 30, 0.95);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 标题栏
        header = QHBoxLayout()
        self.title = QLabel("⏳ 加载中...")
        self.title.setStyleSheet("""
            font-size: 15px;
            color: white;
            font-weight: 600;
        """)
        header.addWidget(self.title)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 13px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 0.8);
                color: white;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        header.addWidget(close_btn)
        layout.addLayout(header)

        # 预报内容区域 - 使用简单的垂直布局
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        self.content_layout.addStretch()
        layout.addLayout(self.content_layout)

    def load_forecast(self):
        """加载天气预报"""
        # 清空现有内容
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        forecast = self.weather_manager.get_hourly_forecast()

        if not forecast:
            self.title.setText("天气预告")
            label = QLabel("获取预报失败，请检查网络")
            label.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 13px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.insertWidget(0, label)
            return

        self.title.setText("📅 未来天气预报")

        times = forecast.get('time', [])
        temps = forecast.get('temperature_2m', [])
        codes = forecast.get('weather_code', [])

        from weather_api import WeatherManager

        # 找到当前小时索引
        now = datetime.now()
        current_hour = now.hour

        items_added = 0
        for i in range(len(times)):
            if items_added >= 6:
                break

            try:
                # 解析时间字符串 (格式: "2024-03-13T14:00")
                time_str = times[i]
                if 'T' in time_str:
                    hour = int(time_str.split('T')[1].split(':')[0])
                else:
                    continue

                # 只显示当前及之后的时间
                if hour < current_hour:
                    continue

                condition, desc = WeatherManager.WEATHER_CODES.get(codes[i], ('unknown', '未知'))
                emoji_map = {
                    'sunny': '☀️', 'cloudy': '☁️', 'rainy': '🌧️',
                    'snowy': '❄️', 'thunder': '⚡', 'foggy': '🌫️', 'unknown': '🌡️'
                }
                emoji = emoji_map.get(condition, '🌡️')

                hour_text = "现在" if hour == current_hour else f"{hour}:00"

                # 创建预报项
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(10, 6, 10, 6)
                item_layout.setSpacing(8)

                time_lbl = QLabel(hour_text)
                time_lbl.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 13px;")
                time_lbl.setFixedWidth(45)

                emoji_lbl = QLabel(emoji)
                emoji_lbl.setStyleSheet("font-size: 20px;")
                emoji_lbl.setFixedWidth(30)

                temp_lbl = QLabel(f"{temps[i]:.0f}°")
                temp_lbl.setStyleSheet("color: #4FC3F7; font-size: 14px; font-weight: bold;")
                temp_lbl.setFixedWidth(35)

                desc_lbl = QLabel(desc)
                desc_lbl.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px;")
                desc_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

                item_layout.addWidget(time_lbl)
                item_layout.addWidget(emoji_lbl)
                item_layout.addWidget(temp_lbl)
                item_layout.addWidget(desc_lbl, 1)

                item_widget.setStyleSheet("""
                    QWidget {
                        background-color: rgba(255, 255, 255, 0.06);
                        border-radius: 8px;
                    }
                """)

                self.content_layout.insertWidget(self.content_layout.count() - 1, item_widget)
                items_added += 1

            except Exception as e:
                print(f"预报项解析错误: {e}")
                continue

        if items_added == 0:
            label = QLabel("暂无预报数据")
            label.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 13px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.insertWidget(0, label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


class StatusIcon(QWidget):
    """状态图标 - 透明度展示进度，悬浮显示数值，可点击"""
    clicked = pyqtSignal()

    def __init__(self, icon, name, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.name = name
        self.value = 5
        self.current_color = "#FF5252"
        self.setFixedSize(44, 50)
        self.setStyleSheet("background: transparent;")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # 图标容器（用于接收鼠标事件）
        self.icon_container = QWidget(self)
        self.icon_container.setFixedSize(44, 36)
        self.icon_container.setStyleSheet("background: transparent;")

        icon_layout = QVBoxLayout(self.icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)

        # 图标
        self.icon_label = QLabel(icon)
        self.icon_label.setFixedSize(44, 36)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 22px; background: transparent;")
        icon_layout.addWidget(self.icon_label)

        layout.addWidget(self.icon_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # 数值（默认隐藏，悬浮显示）
        self.value_label = QLabel("5%")
        self.value_label.setFixedSize(44, 12)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-size: 10px; color: rgba(255,255,255,200); background: transparent;")
        self.value_label.hide()
        layout.addWidget(self.value_label)

        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.3)  # 初始透明度

    def enterEvent(self, event):
        """鼠标进入显示数值"""
        self.value_label.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开隐藏数值"""
        self.value_label.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()

    def setValue(self, value):
        self.value = max(0, min(100, value))
        self.value_label.setText(f"{self.value}%")

        # 根据数值计算透明度（0.25 - 1.0）
        # 5% -> 0.25, 100% -> 1.0
        opacity = 0.25 + (self.value / 100) * 0.75
        self.opacity_effect.setOpacity(opacity)

        # 颜色根据数值变化
        if self.value < 30:
            color = "#FF5252"  # 红色警告
        elif self.value < 60:
            color = "#FFC107"  # 黄色警告
        else:
            color = "#FFFFFF"  # 白色正常

        self.current_color = color
        self.icon_label.setStyleSheet(f"font-size: 22px; background: transparent; color: {color};")

        # 数值颜色
        self.value_label.setStyleSheet(f"font-size: 10px; color: {color}; background: transparent;")


class FoodDialog(QDialog):
    """极简食物选择"""
    food_selected = pyqtSignal(str)

    def __init__(self, foods, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 180)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 主容器 - 毛玻璃效果
        container = QWidget(self)
        container.setFixedSize(240, 180)
        container.setStyleSheet("""
            QWidget {
                background: rgba(40, 40, 40, 220);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 50);
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

        title = QLabel("喂食")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 13px; color: rgba(255,255,255,200);")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(8)

        foods_list = list(foods.items())
        for i, (emoji, food) in enumerate(foods_list[:8]):
            btn = QPushButton(emoji)
            btn.setToolTip(food['name'])
            btn.setFixedSize(44, 44)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 22px;
                    background: rgba(255, 255, 255, 30);
                    border: none;
                    border-radius: 22px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 60);
                }
            """)
            btn.clicked.connect(lambda checked, e=emoji: self.select_food(e))
            grid.addWidget(btn, i // 4, i % 4)

        layout.addLayout(grid)
        layout.addStretch()

    def select_food(self, emoji):
        self.food_selected.emit(emoji)
        self.accept()


class WeatherSpriteWindow(QMainWindow):
    """天气精灵 - 完全透明悬浮窗"""

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.weather = WeatherManager(self.config)
        self.sprite = Sprite()
        self.drag_position = None
        self._breath_counter = 0

        self.init_ui()
        self.init_timer()
        self.init_tray()
        self.update_weather()

        # 启动时段问候（延迟显示，让用户先看到界面）
        QTimer.singleShot(1000, self.show_greeting)

    def init_ui(self):
        """初始化透明UI"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 窗口大小 - 增加高度确保所有元素显示
        self.setFixedSize(180, 270)
        self.move(self.config.get('position', {'x': 100, 'y': 100})['x'],
                  self.config.get('position', {'x': 100, 'y': 100})['y'])

        # === 顶部信息栏 ===
        self.top_bar = QWidget(self)
        self.top_bar.setFixedSize(160, 30)
        self.top_bar.move(10, 5)
        self.top_bar.setStyleSheet("background: transparent;")

        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        # 温度显示
        self.temp_label = QLabel("--°")
        self.temp_label.setFixedSize(50, 26)
        self.temp_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 300;
            color: rgba(255, 255, 255, 240);
            background: rgba(0, 0, 0, 50);
            border-radius: 13px;
            padding: 2px 8px;
        """)
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.temp_label.mousePressEvent = self.show_forecast_dialog
        top_layout.addWidget(self.temp_label)

        top_layout.addStretch()

        # 城市显示（可点击切换城市，点击温度显示预报）
        self.city_label = QLabel("定位中...")
        self.city_label.setFixedSize(70, 26)
        self.city_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: rgba(255, 255, 255, 240);
            background: rgba(0, 0, 0, 50);
            border-radius: 13px;
            padding: 2px 8px;
        """)
        self.city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.city_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.city_label.mousePressEvent = self.on_city_clicked
        top_layout.addWidget(self.city_label)

        # === 精灵主体 ===
        self.sprite_container = QWidget(self)
        self.sprite_container.setFixedSize(120, 120)
        self.sprite_container.move(30, 40)

        # 精灵表情 - 大字体，居中
        self.sprite_label = QLabel("🌱", self.sprite_container)
        self.sprite_label.setFixedSize(120, 120)
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_label.setStyleSheet("""
            font-size: 72px;
            background: transparent;
        """)

        # === 状态面板 ===
        self.status_panel = QWidget(self)
        self.status_panel.setFixedSize(160, 55)
        self.status_panel.move(10, 160)
        self.status_panel.setStyleSheet("background: transparent;")

        status_layout = QHBoxLayout(self.status_panel)
        status_layout.setContentsMargins(5, 0, 5, 0)
        status_layout.setSpacing(10)

        # 创建三个状态图标
        self.hunger_icon = StatusIcon("🍖", "饱食度", self)
        self.hunger_icon.clicked.connect(self.show_food_dialog)
        status_layout.addWidget(self.hunger_icon)

        self.mood_icon = StatusIcon("❤️", "心情值", self)
        self.mood_icon.clicked.connect(self.show_interact_menu)
        status_layout.addWidget(self.mood_icon)

        self.energy_icon = StatusIcon("⚡", "精力值", self)
        status_layout.addWidget(self.energy_icon)

        status_layout.addStretch()

        # 等级显示
        self.lv_label = QLabel("Lv.1")
        self.lv_label.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 180); background: transparent;")
        status_layout.addWidget(self.lv_label)

        # === 心情文字 ===
        self.mood_text = QLabel(self)
        self.mood_text.setFixedSize(180, 30)
        self.mood_text.move(0, 220)
        self.mood_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mood_text.setWordWrap(True)
        self.mood_text.setStyleSheet("""
            font-size: 11px;
            color: rgba(255, 255, 255, 200);
            background: transparent;
        """)

        # === 对话气泡（精灵上方显示）===
        self.bubble = QLabel(self)
        self.bubble.setFixedSize(170, 50)
        self.bubble.move(5, 38)  # 放在精灵上方，不在窗口外
        self.bubble.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.bubble.setWordWrap(True)
        self.bubble.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 220);
                border-radius: 12px;
                font-size: 12px;
                color: rgba(255, 255, 255, 250);
                padding: 4px 8px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        self.bubble.hide()
        # 让气泡显示在最上层
        self.bubble.raise_()

    def init_tray(self):
        """初始化托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("天气精灵")

        from PyQt6.QtWidgets import QStyle
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: rgba(40, 40, 40, 240);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
                padding: 8px;
                color: white;
            }
            QMenu::item {
                padding: 10px 24px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: rgba(255, 255, 255, 30);
            }
        """)

        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show_window)
        menu.addAction(show_action)

        menu.addSeparator()

        pet_action = QAction("❤️ 摸摸头", self)
        pet_action.triggered.connect(self.quick_pet)
        menu.addAction(pet_action)

        feed_action = QAction("🍎 喂食", self)
        feed_action.triggered.connect(self.show_food_dialog)
        menu.addAction(feed_action)

        menu.addSeparator()

        refresh_action = QAction("🌤️ 刷新天气", self)
        refresh_action.triggered.connect(lambda: self.update_weather(show_advice=True))
        menu.addAction(refresh_action)

        menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def update_weather(self, show_advice=False):
        """更新天气"""
        weather_data = self.weather.get_current_weather()
        if weather_data:
            old_weather = self.sprite.weather_type
            self.sprite.set_weather(weather_data)
            self.update_display()

            # 显示天气建议（如果是用户主动刷新或天气变化）
            if show_advice or old_weather != weather_data.get('condition', 'unknown'):
                advice = self.get_weather_advice(
                    weather_data.get('condition', 'unknown'),
                    weather_data.get('temperature', 20)
                )
                QTimer.singleShot(500, lambda: self.show_bubble(advice, 4000))

    def show_greeting(self):
        """显示时段问候"""
        greeting = self.get_time_greeting()
        self.show_bubble(greeting, 4000)

    def update_frame(self):
        """更新动画"""
        self.sprite.update()
        frame = self.sprite.get_next_frame()

        # 更新精灵表情
        self.sprite_label.setText(frame['emoji'])

        # 呼吸效果
        self._breath_counter += 1
        if self._breath_counter % 20 < 10:
            offset = (self._breath_counter % 10) * 0.3
        else:
            offset = (10 - self._breath_counter % 10) * 0.3
        self.sprite_label.move(0, int(offset))

        # 定期更新状态
        if self._breath_counter % 15 == 0:
            self.update_status()

    def update_display(self):
        """更新显示"""
        status = self.sprite.get_status()

        # 温度
        self.temp_label.setText(f"{status['temperature']}°")

        # 城市
        self.city_label.setText(status['city'])

        # 更新状态图标
        self.hunger_icon.setValue(status['hunger'])
        self.mood_icon.setValue(status['mood'])
        self.energy_icon.setValue(status['energy'])

        self.lv_label.setText(f"Lv.{status['level']}")

        self.update_status()

    def update_status(self):
        """更新状态"""
        self.mood_text.setText(self.sprite.get_mood_text())

        # 获取最新状态并更新图标
        status = self.sprite.get_status()
        self.hunger_icon.setValue(status['hunger'])
        self.mood_icon.setValue(status['mood'])
        self.energy_icon.setValue(status['energy'])
        self.lv_label.setText(f"Lv.{status['level']}")

    def show_bubble(self, text, duration=3000):
        """显示气泡"""
        # 限制文字长度，确保能显示
        if len(text) > 24:
            text = text[:22] + "..."

        self.bubble.setText(text)

        # 根据文字长度调整气泡大小
        fm = QFontMetrics(self.bubble.font())
        text_width = fm.horizontalAdvance(text)
        # 最小100，最大170，留padding
        width = min(170, max(100, text_width + 20))
        height = 45 if len(text) > 12 else 38

        self.bubble.setFixedSize(width, height)
        # 居中显示在精灵上方
        self.bubble.move((180 - width) // 2, 40)
        self.bubble.raise_()  # 确保在最上层

        self.bubble.show()
        self.bubble_timer.start(duration)

    def hide_bubble(self):
        """隐藏气泡"""
        self.bubble.hide()

    def show_forecast_dialog(self, event=None):
        """显示天气预告面板"""
        dialog = WeatherForecastDialog(self.weather, self)
        # 在精灵窗口下方显示
        pos = self.mapToGlobal(self.temp_label.pos())
        dialog.move(pos.x() - 50, pos.y() + 40)
        dialog.exec()

    def get_time_greeting(self):
        """获取时段问候语"""
        hour = datetime.now().hour
        greetings = {
            'morning': ['早安！新的一天开始啦~', '早上好！今天也要元气满满！', '早安！准备好开始了吗？'],
            'noon': ['中午好！记得休息哦~', '午安！吃饱了吗？', '中午啦，休息一下~'],
            'afternoon': ['下午好！继续加油~', '午后时光，保持专注！', '下午好！喝杯茶休息下~'],
            'evening': ['晚上好！辛苦了一天~', '傍晚好！准备休息了吗？', '晚上好！今天过得如何？'],
            'night': ['夜深了，早点休息~', '晚安！好梦~', '该睡觉啦，明天见~']
        }

        if 5 <= hour < 11:
            return random.choice(greetings['morning'])
        elif 11 <= hour < 14:
            return random.choice(greetings['noon'])
        elif 14 <= hour < 18:
            return random.choice(greetings['afternoon'])
        elif 18 <= hour < 22:
            return random.choice(greetings['evening'])
        else:
            return random.choice(greetings['night'])

    def get_weather_advice(self, weather_type, temp):
        """获取天气建议"""
        advice_map = {
            'sunny': [
                '今天阳光明媚，记得涂防晒！',
                '晴天适合出门运动~',
                '阳光正好，出去走走吧！'
            ],
            'rainy': [
                '下雨了，出门记得带伞！',
                '雨天路滑，注意安全~',
                '听着雨声，心情会平静下来~'
            ],
            'cloudy': [
                '多云天气，适合散步~',
                '天气凉爽，不冷不热~',
                '云很多，可能要下雨哦~'
            ],
            'snowy': [
                '下雪了！注意保暖！',
                '雪天路滑，小心行走~',
                '堆雪人去吧！⛄'
            ],
            'thunder': [
                '雷雨天，尽量待在室内~',
                '打雷了，别站在树下！',
                '雷雨天气，注意安全！'
            ],
            'foggy': [
                '雾很大，开车要小心！',
                '能见度低，注意安全~',
                '雾蒙蒙的，像仙境一样~'
            ],
            'unknown': ['今天天气有点神秘~']
        }

        temp_advice = []
        if temp > 30:
            temp_advice = '好热啊，多喝水！'
        elif temp < 5:
            temp_advice = '好冷，多穿点衣服！'
        elif temp < 15:
            temp_advice = '有点凉，带件外套~'

        weather_tips = advice_map.get(weather_type, advice_map['unknown'])
        advice = random.choice(weather_tips)

        if temp_advice:
            advice += ' ' + temp_advice

        return advice

    def init_timer(self):
        """初始化定时器"""
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_frame)
        self.anim_timer.start(150)

        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(30 * 60 * 1000)

        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.save_state)
        self.save_timer.start(5 * 60 * 1000)

        self.bubble_timer = QTimer(self)
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.hide_bubble)

        # 单击延迟定时器（用于区分单击和双击）
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.on_click_timeout)
        self.pending_click_pos = None

    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.click_start_pos = event.pos()
            self.is_dragging = False
            event.accept()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.quick_pet()

    def mouseMoveEvent(self, event):
        """拖拽"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.is_dragging = True
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """释放 - 区分点击和拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.pos()
            self.config.set('position', {'x': pos.x(), 'y': pos.y()})
            self.drag_position = None

            # 判断是否点击（不是拖拽）
            if not self.is_dragging and self.click_start_pos:
                move_distance = (event.pos() - self.click_start_pos).manhattanLength()
                if move_distance < 5:
                    # 延迟处理单击，等待可能的双击
                    self.pending_click_pos = event.pos()
                    self.click_timer.start(200)  # 200ms延迟

            self.click_start_pos = None
            self.is_dragging = False

    def on_click_timeout(self):
        """单击超时 - 执行单击操作（喂食）"""
        if self.pending_click_pos:
            sprite_rect = self.sprite_container.geometry()
            if sprite_rect.contains(self.pending_click_pos):
                # 快速喂食
                weather_food_map = {
                    'sunny': '☀️',
                    'rainy': '💧',
                    'cloudy': '☁️',
                    'snowy': '❄️',
                    'thunder': '⚡',
                    'foggy': '🌫️',
                }
                food = weather_food_map.get(self.sprite.weather_type, '🍎')
                food_emoji, message = self.sprite.feed(food)
                self.show_bubble(message)
                self.update_status()
            self.pending_click_pos = None

    def mouseDoubleClickEvent(self, event):
        """双击精灵 - 玩耍"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 取消待处理的单击
            self.click_timer.stop()
            self.pending_click_pos = None

            # 执行双击操作（玩耍）
            sprite_rect = self.sprite_container.geometry()
            if sprite_rect.contains(event.pos()):
                self.do_interact('play')

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(40, 40, 40, 240);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
                padding: 6px;
                color: white;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: rgba(255, 255, 255, 25);
            }
        """)

        menu.addSeparator()

        refresh = QAction("🌤️ 刷新天气", self)
        refresh.triggered.connect(self.update_weather)
        menu.addAction(refresh)

        menu.addSeparator()

        hide = QAction("🙈 隐藏", self)
        hide.triggered.connect(self.hide)
        menu.addAction(hide)

        quit_a = QAction("退出", self)
        quit_a.triggered.connect(self.quit_app)
        menu.addAction(quit_a)

        menu.exec(event.globalPos())

    def quick_pet(self):
        """摸头"""
        text = self.sprite.interact('pet')
        self.show_bubble(text)
        self.update_status()

    def do_interact(self, interaction_type):
        """互动"""
        text = self.sprite.interact(interaction_type)
        self.show_bubble(text)
        self.update_status()

    def show_food_dialog(self):
        """显示食物对话框"""
        dialog = FoodDialog(self.sprite.FOODS, self)
        dialog.food_selected.connect(self.on_food_selected)
        dialog.exec()

    def on_food_selected(self, emoji):
        """喂食"""
        food_emoji, message = self.sprite.feed(emoji)
        self.show_bubble(message)
        self.update_status()

    def show_interact_menu(self):
        """显示互动菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(40, 40, 40, 240);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
                padding: 8px;
                color: white;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: rgba(255, 255, 255, 30);
            }
        """)

        pet = QAction("❤️ 摸摸头", self)
        pet.triggered.connect(self.quick_pet)
        menu.addAction(pet)

        play = QAction("🎵 玩耍", self)
        play.triggered.connect(lambda: self.do_interact('play'))
        menu.addAction(play)

        talk = QAction("💬 聊天", self)
        talk.triggered.connect(lambda: self.do_interact('talk'))
        menu.addAction(talk)

        # 在心情图标位置显示菜单
        pos = self.mood_icon.mapToGlobal(self.mood_icon.rect().bottomLeft())
        pos.setY(pos.y() + 5)
        menu.exec(pos)

    def show_settings(self):
        """设置"""
        from settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            self.update_weather()

    def on_city_clicked(self, event):
        """点击城市 - 切换城市"""
        self.show_city_dialog()

    def show_city_dialog(self):
        """显示城市选择对话框"""
        from city_dialog import CityDialog
        current = self.config.get('city', '北京')
        dialog = CityDialog(self, current_city=current)
        dialog.city_selected.connect(self.on_city_changed)
        dialog.exec()

    def on_city_changed(self, city):
        """城市切换 - 立即响应，异步获取天气"""
        self.config.set('city', city)
        self.config.save()

        # 立即显示加载状态
        self.city_label.setText("加载中...")
        self.temp_label.setText("--°")
        self.sprite_label.setText("⏳")
        self.show_bubble(f"正在获取 {city} 的天气...")

        # 延迟执行天气获取（让UI先更新）
        QTimer.singleShot(100, self._do_update_weather)

    def _do_update_weather(self):
        """异步获取天气"""
        try:
            weather_data = self.weather.get_current_weather()
            if weather_data and weather_data.get('weather_code') != -1:
                self.sprite.set_weather(weather_data)
                self.update_display()
                self.show_bubble(f"已切换到 {weather_data.get('city', '未知')}")
            else:
                self.city_label.setText("获取失败")
                self.show_bubble("天气获取失败，请检查网络")
        except Exception as e:
            print(f"获取天气失败: {e}")
            self.city_label.setText("获取失败")
            self.show_bubble("天气获取失败")

    def on_tray_activated(self, reason):
        """托盘点击"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def show_window(self):
        """显示窗口"""
        self.show()
        self.raise_()
        self.activateWindow()

    def save_state(self):
        """保存"""
        self.sprite.save_state()
        self.config.save()

    def quit_app(self):
        """退出"""
        self.save_state()
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """关闭"""
        self.quit_app()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = WeatherSpriteWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
