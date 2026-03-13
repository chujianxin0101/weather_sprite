#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import json
import threading
from pathlib import Path


class Config:
    """配置管理器"""

    DEFAULT_CONFIG = {
        'city': '北京',
        'position': {'x': 100, 'y': 100},
        'auto_start': False,
        'update_interval': 30,  # 天气更新间隔（分钟）
        'window_opacity': 0.95,
    }

    def __init__(self, config_file='config.json'):
        self.config_file = Path(config_file)
        self._data = {}
        self._pending_save = False
        self._save_delay_ms = 500
        self._save_timer = None
        self.load()

    def load(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
                self._data = self.DEFAULT_CONFIG.copy()
        else:
            self._data = self.DEFAULT_CONFIG.copy()
            self.save()

    def save(self):
        """保存配置"""
        self._pending_save = False
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _delayed_save(self):
        """延迟保存配置"""
        self.save()

    def get(self, key, default=None):
        """获取配置项"""
        return self._data.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self._data[key] = value
        self._pending_save = True
        if self._save_timer is not None:
            self._save_timer.cancel()
        self._save_timer = threading.Timer(self._save_delay_ms / 1000.0, self._delayed_save)
        self._save_timer.start()

    def get_all(self):
        """获取所有配置"""
        return self._data.copy()
