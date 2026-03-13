#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气API模块 - 获取实时天气数据
使用 Open-Meteo API (免费，无需API Key)
"""

import requests
import json
from pathlib import Path
from config import Config


class WeatherManager:
    """天气管理器"""

    # WMO 天气代码映射
    WEATHER_CODES = {
        0: ('sunny', '晴朗'),
        1: ('sunny', ' mainly clear'),  # 主要晴朗
        2: ('cloudy', '多云'),
        3: ('cloudy', '阴天'),
        45: ('foggy', '雾'),
        48: ('foggy', '雾凇'),
        51: ('rainy', '毛毛雨'),
        53: ('rainy', '中雨'),
        55: ('rainy', '大雨'),
        56: ('rainy', '冻雨'),
        57: ('rainy', '强冻雨'),
        61: ('rainy', '小雨'),
        63: ('rainy', '中雨'),
        65: ('rainy', '暴雨'),
        66: ('rainy', '冻雨'),
        67: ('rainy', '强冻雨'),
        71: ('snowy', '小雪'),
        73: ('snowy', '中雪'),
        75: ('snowy', '大雪'),
        77: ('snowy', '雪粒'),
        80: ('rainy', '阵雨'),
        81: ('rainy', '强阵雨'),
        82: ('rainy', '暴雨'),
        85: ('snowy', '阵雪'),
        86: ('snowy', '强阵雪'),
        95: ('thunder', '雷雨'),
        96: ('thunder', '雷雨伴冰雹'),
        99: ('thunder', '强雷雨伴冰雹'),
    }

    # 城市坐标数据库（部分常见城市）
    CITY_COORDS = {
        '北京': {'lat': 39.9042, 'lon': 116.4074},
        '上海': {'lat': 31.2304, 'lon': 121.4737},
        '广州': {'lat': 23.1291, 'lon': 113.2644},
        '深圳': {'lat': 22.5431, 'lon': 114.0579},
        '杭州': {'lat': 30.2741, 'lon': 120.1551},
        '南京': {'lat': 32.0603, 'lon': 118.7969},
        '成都': {'lat': 30.5728, 'lon': 104.0668},
        '武汉': {'lat': 30.5928, 'lon': 114.3055},
        '西安': {'lat': 34.3416, 'lon': 108.9398},
        '重庆': {'lat': 29.5630, 'lon': 106.5516},
        '天津': {'lat': 39.1252, 'lon': 117.1904},
        '苏州': {'lat': 31.2989, 'lon': 120.5853},
        '长沙': {'lat': 28.2282, 'lon': 112.9388},
        '郑州': {'lat': 34.7466, 'lon': 113.6253},
        '沈阳': {'lat': 41.8057, 'lon': 123.4315},
        '青岛': {'lat': 36.0671, 'lon': 120.3826},
        '宁波': {'lat': 29.8683, 'lon': 121.5440},
        '东莞': {'lat': 23.0489, 'lon': 113.7447},
        '佛山': {'lat': 23.0218, 'lon': 113.1219},
        '合肥': {'lat': 31.8206, 'lon': 117.2272},
        '厦门': {'lat': 24.4798, 'lon': 118.0894},
        '大连': {'lat': 38.9140, 'lon': 121.6147},
        '哈尔滨': {'lat': 45.8038, 'lon': 126.5350},
        '济南': {'lat': 36.6512, 'lon': 117.1201},
        '长春': {'lat': 43.8171, 'lon': 125.3235},
        '昆明': {'lat': 25.0389, 'lon': 102.7183},
        '南宁': {'lat': 22.8170, 'lon': 108.3665},
        '贵阳': {'lat': 26.6470, 'lon': 106.6302},
        '福州': {'lat': 26.0745, 'lon': 119.2965},
        '太原': {'lat': 37.8706, 'lon': 112.5489},
        '石家庄': {'lat': 38.0428, 'lon': 114.5149},
        '南昌': {'lat': 28.6820, 'lon': 115.8579},
        '兰州': {'lat': 36.0611, 'lon': 103.8343},
        '海口': {'lat': 20.0440, 'lon': 110.1999},
        '乌鲁木齐': {'lat': 43.8256, 'lon': 87.6168},
        '呼和浩特': {'lat': 40.8414, 'lon': 111.7519},
        '银川': {'lat': 38.4872, 'lon': 106.2309},
        '西宁': {'lat': 36.6171, 'lon': 101.7782},
        '拉萨': {'lat': 29.6500, 'lon': 91.1000},
        '香港': {'lat': 22.3193, 'lon': 114.1694},
        '澳门': {'lat': 22.1987, 'lon': 113.5439},
        '台北': {'lat': 25.0330, 'lon': 121.5654},
    }

    def __init__(self, config=None):
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WeatherSprite/1.0'
        })

    def get_city_coords(self, city_name):
        """获取城市坐标"""
        # 先查内置数据库
        if city_name in self.CITY_COORDS:
            return self.CITY_COORDS[city_name]

        # 否则用地理编码API查询
        try:
            url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {
                'name': city_name,
                'count': 1,
                'language': 'zh',
                'format': 'json'
            }
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()

            if 'results' in data and data['results']:
                result = data['results'][0]
                return {
                    'lat': result['latitude'],
                    'lon': result['longitude'],
                    'name': result.get('name', city_name)
                }
        except Exception as e:
            print(f"获取城市坐标失败: {e}")

        # 默认返回北京
        return self.CITY_COORDS['北京']

    def get_current_weather(self):
        """获取当前天气"""
        city = self.config.get('city', '北京')

        try:
            coords = self.get_city_coords(city)
            lat = coords['lat']
            lon = coords['lon']

            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,weather_code,relative_humidity_2m',
                'timezone': 'auto'
            }

            response = self.session.get(url, params=params, timeout=10)
            data = response.json()

            if 'current' in data:
                current = data['current']
                weather_code = current.get('weather_code', 0)
                temperature = current.get('temperature_2m', 0)

                # 解析天气代码
                condition, description = self.WEATHER_CODES.get(
                    weather_code, ('unknown', '未知')
                )

                return {
                    'condition': condition,
                    'description': description,
                    'temperature': temperature,
                    'weather_code': weather_code,
                    'humidity': current.get('relative_humidity_2m', 0),
                    'city': city
                }

        except Exception as e:
            print(f"获取天气失败: {e}")

        # 返回默认天气
        return {
            'condition': 'unknown',
            'description': '获取失败',
            'temperature': 0,
            'weather_code': -1,
            'humidity': 0,
            'city': city
        }

    def get_hourly_forecast(self):
        """获取小时预报"""
        city = self.config.get('city', '北京')

        try:
            coords = self.get_city_coords(city)

            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'hourly': ['temperature_2m', 'weather_code'],
                'forecast_days': 1,
                'timezone': 'auto'
            }

            response = self.session.get(url, params=params, timeout=10)
            data = response.json()

            if 'hourly' in data:
                return data['hourly']

        except Exception as e:
            print(f"获取预报失败: {e}")

        return None
