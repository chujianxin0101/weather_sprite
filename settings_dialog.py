#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QSpinBox,
                             QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt

from weather_api import WeatherManager


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("天气精灵设置")
        self.setFixedSize(350, 300)

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 城市设置
        city_group = QGroupBox("城市设置")
        city_layout = QVBoxLayout(city_group)

        city_input_layout = QHBoxLayout()
        city_input_layout.addWidget(QLabel("所在城市:"))
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("输入城市名，如：北京、上海")
        city_input_layout.addWidget(self.city_input)
        city_layout.addLayout(city_input_layout)

        # 快速选择常用城市
        city_layout.addWidget(QLabel("快速选择:"))
        self.city_combo = QComboBox()
        self.city_combo.addItems([
            '北京', '上海', '广州', '深圳', '杭州', '南京',
            '成都', '武汉', '西安', '重庆', '天津', '苏州',
            '长沙', '郑州', '沈阳', '青岛', '宁波', '东莞',
            '厦门', '大连', '哈尔滨', '济南', '昆明', '香港'
        ])
        self.city_combo.currentTextChanged.connect(self.city_input.setText)
        city_layout.addWidget(self.city_combo)

        layout.addWidget(city_group)

        # 更新设置
        update_group = QGroupBox("更新设置")
        update_layout = QVBoxLayout(update_group)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("天气更新间隔:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setSuffix(" 分钟")
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        update_layout.addLayout(interval_layout)

        self.auto_start_check = QCheckBox("开机自动启动")
        update_layout.addWidget(self.auto_start_check)

        layout.addWidget(update_group)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(self.test_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setDefault(True)
        btn_layout.addWidget(self.save_btn)

        layout.addStretch()
        layout.addLayout(btn_layout)

    def load_settings(self):
        """加载当前设置"""
        self.city_input.setText(self.config.get('city', '北京'))
        self.interval_spin.setValue(self.config.get('update_interval', 30))
        self.auto_start_check.setChecked(self.config.get('auto_start', False))

    def save_settings(self):
        """保存设置"""
        city = self.city_input.text().strip()
        if city:
            self.config.set('city', city)

        self.config.set('update_interval', self.interval_spin.value())
        self.config.set('auto_start', self.auto_start_check.isChecked())

        self.accept()

    def test_connection(self):
        """测试天气API连接"""
        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")

        # 临时修改配置测试
        old_city = self.config.get('city')
        test_city = self.city_input.text().strip() or old_city

        # 临时设置测试城市
        self.config.set('city', test_city)
        weather = WeatherManager(self.config)
        result = weather.get_current_weather()

        # 恢复原城市（如果用户没点保存）
        self.config.set('city', old_city)

        if result and result.get('weather_code') != -1:
            self.test_btn.setText("✓ 连接成功")
        else:
            self.test_btn.setText("✗ 连接失败")

        # 恢复按钮
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: (
            self.test_btn.setText("测试连接"),
            self.test_btn.setEnabled(True)
        ))
