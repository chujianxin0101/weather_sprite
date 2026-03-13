#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市选择对话框 - 毛玻璃极简设计
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QScrollArea,
                             QGridLayout, QLineEdit, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class CityDialog(QDialog):
    """城市选择对话框 - 毛玻璃风格"""
    city_selected = pyqtSignal(str)

    CITIES = [
        '北京', '上海', '广州', '深圳', '成都', '杭州',
        '武汉', '西安', '重庆', '苏州', '南京', '天津',
        '郑州', '长沙', '东莞', '佛山', '宁波', '青岛',
        '沈阳', '昆明', '合肥', '福州', '厦门', '哈尔滨',
        '济南', '长春', '石家庄', '南宁', '贵阳', '兰州',
        '太原', '乌鲁木齐', '呼和浩特', '海口', '银川', '西宁',
        '拉萨', '香港', '澳门'
    ]

    def __init__(self, parent=None, current_city='北京'):
        super().__init__(parent)
        self.current_city = current_city
        self.setFixedSize(300, 420)

        # 无边框窗口，但保留输入法支持
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)

        self.setup_ui()

    def setup_ui(self):
        """设置UI - 毛玻璃风格"""
        # 主容器
        container = QWidget(self)
        container.setFixedSize(300, 420)
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(28, 28, 30, 0.85);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 顶部标题
        header = QHBoxLayout()

        title = QLabel("选择城市")
        title.setStyleSheet("""
            font-size: 18px;
            color: white;
            font-weight: 600;
            letter-spacing: 1px;
        """)
        header.addWidget(title)
        header.addStretch()

        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 14px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 0.8);
                color: white;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)

        layout.addLayout(header)

        # 输入框 - 毛玻璃风格
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("搜索城市...")
        self.input_field.setFixedHeight(44)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 0 16px;
                color: white;
                font-size: 15px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.35);
            }
        """)
        self.input_field.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.input_field.returnPressed.connect(self.on_input_confirmed)
        layout.addWidget(self.input_field)

        # 城市网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.cities_widget = QWidget()
        self.cities_widget.setStyleSheet("background: transparent;")
        self.cities_layout = QGridLayout(self.cities_widget)
        self.cities_layout.setContentsMargins(0, 0, 8, 0)
        self.cities_layout.setSpacing(10)
        self.cities_layout.setColumnStretch(0, 1)
        self.cities_layout.setColumnStretch(1, 1)
        self.cities_layout.setColumnStretch(2, 1)

        self.create_city_buttons()

        scroll.setWidget(self.cities_widget)
        layout.addWidget(scroll)

    def create_city_buttons(self):
        """创建城市按钮 - 悬浮卡片风格"""
        row = 0
        col = 0
        for city in self.CITIES:
            btn = QPushButton(city)
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            is_current = (city == self.current_city)

            if is_current:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(10, 132, 255, 0.9);
                        border: none;
                        border-radius: 10px;
                        color: white;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: rgba(10, 132, 255, 1.0);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.06);
                        border: none;
                        border-radius: 10px;
                        color: rgba(255, 255, 255, 0.85);
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.12);
                        color: white;
                    }
                """)

            btn.clicked.connect(lambda checked, c=city: self.select_city(c))
            self.cities_layout.addWidget(btn, row, col)

            col += 1
            if col >= 3:
                col = 0
                row += 1

        self.cities_layout.setRowStretch(row + 1, 1)

    def on_input_confirmed(self):
        """输入确认"""
        text = self.input_field.text().strip()
        if text:
            self.select_city(text)

    def select_city(self, city):
        """选择城市"""
        self.city_selected.emit(city)
        self.accept()

    def showEvent(self, event):
        """显示时聚焦输入框"""
        super().showEvent(event)
        self.input_field.setFocus()

    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """拖拽移动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """拖拽移动"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
