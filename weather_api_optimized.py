import time
from functools import lru_cache
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
澶╂皵API妯″潡 - 鑾峰彇瀹炴椂澶╂皵鏁版嵁
浣跨敤 Open-Meteo API (鍏嶈垂锛屾棤闇€API Key)
"""

import requests
import json
from pathlib import Path
from config import Config


class WeatherManager:
    """澶╂皵绠＄悊鍣?""

    # WMO 澶╂皵浠ｇ爜鏄犲皠
    WEATHER_CODES = {
        0: ('sunny', '鏅存湕'),
        1: ('sunny', ' mainly clear'),  # 涓昏鏅存湕
        2: ('cloudy', '澶氫簯'),
        3: ('cloudy', '闃村ぉ'),
        45: ('foggy', '闆?),
        48: ('foggy', '闆惧噰'),
        51: ('rainy', '姣涙瘺闆?),
        53: ('rainy', '涓洦'),
        55: ('rainy', '澶ч洦'),
        56: ('rainy', '鍐婚洦'),
        57: ('rainy', '寮哄喕闆?),
        61: ('rainy', '灏忛洦'),
        63: ('rainy', '涓洦'),
        65: ('rainy', '鏆撮洦'),
        66: ('rainy', '鍐婚洦'),
        67: ('rainy', '寮哄喕闆?),
        71: ('snowy', '灏忛洩'),
        73: ('snowy', '涓洩'),
        75: ('snowy', '澶ч洩'),
        77: ('snowy', '闆矑'),
        80: ('rainy', '闃甸洦'),
        81: ('rainy', '寮洪樀闆?),
        82: ('rainy', '鏆撮洦'),
        85: ('snowy', '闃甸洩'),
        86: ('snowy', '寮洪樀闆?),
        95: ('thunder', '闆烽洦'),
        96: ('thunder', '闆烽洦浼村啺闆?),
        99: ('thunder', '寮洪浄闆ㄤ即鍐伴浌'),
    }

    # 鍩庡競鍧愭爣鏁版嵁搴擄紙閮ㄥ垎甯歌鍩庡競锛?
    CITY_COORDS = {
        '鍖椾含': {'lat': 39.9042, 'lon': 116.4074},
        '涓婃捣': {'lat': 31.2304, 'lon': 121.4737},
        '骞垮窞': {'lat': 23.1291, 'lon': 113.2644},
        '娣卞湷': {'lat': 22.5431, 'lon': 114.0579},
        '鏉窞': {'lat': 30.2741, 'lon': 120.1551},
        '鍗椾含': {'lat': 32.0603, 'lon': 118.7969},
        '鎴愰兘': {'lat': 30.5728, 'lon': 104.0668},
        '姝︽眽': {'lat': 30.5928, 'lon': 114.3055},
        '瑗垮畨': {'lat': 34.3416, 'lon': 108.9398},
        '閲嶅簡': {'lat': 29.5630, 'lon': 106.5516},
        '澶╂触': {'lat': 39.1252, 'lon': 117.1904},
        '鑻忓窞': {'lat': 31.2989, 'lon': 120.5853},
        '闀挎矙': {'lat': 28.2282, 'lon': 112.9388},
        '閮戝窞': {'lat': 34.7466, 'lon': 113.6253},
        '娌堥槼': {'lat': 41.8057, 'lon': 123.4315},
        '闈掑矝': {'lat': 36.0671, 'lon': 120.3826},
        '瀹佹尝': {'lat': 29.8683, 'lon': 121.5440},
        '涓滆帪': {'lat': 23.0489, 'lon': 113.7447},
        '浣涘北': {'lat': 23.0218, 'lon': 113.1219},
        '鍚堣偉': {'lat': 31.8206, 'lon': 117.2272},
        '鍘﹂棬': {'lat': 24.4798, 'lon': 118.0894},
        '澶ц繛': {'lat': 38.9140, 'lon': 121.6147},
        '鍝堝皵婊?: {'lat': 45.8038, 'lon': 126.5350},
        '娴庡崡': {'lat': 36.6512, 'lon': 117.1201},
        '闀挎槬': {'lat': 43.8171, 'lon': 125.3235},
        '鏄嗘槑': {'lat': 25.0389, 'lon': 102.7183},
        '鍗楀畞': {'lat': 22.8170, 'lon': 108.3665},
        '璐甸槼': {'lat': 26.6470, 'lon': 106.6302},
        '绂忓窞': {'lat': 26.0745, 'lon': 119.2965},
        '澶師': {'lat': 37.8706, 'lon': 112.5489},
        '鐭冲搴?: {'lat': 38.0428, 'lon': 114.5149},
        '鍗楁槍': {'lat': 28.6820, 'lon': 115.8579},
        '鍏板窞': {'lat': 36.0611, 'lon': 103.8343},
        '娴峰彛': {'lat': 20.0440, 'lon': 110.1999},
        '涔岄瞾鏈ㄩ綈': {'lat': 43.8256, 'lon': 87.6168},
        '鍛煎拰娴╃壒': {'lat': 40.8414, 'lon': 111.7519},
        '閾跺窛': {'lat': 38.4872, 'lon': 106.2309},
        '瑗垮畞': {'lat': 36.6171, 'lon': 101.7782},
        '鎷夎惃': {'lat': 29.6500, 'lon': 91.1000},
        '棣欐腐': {'lat': 22.3193, 'lon': 114.1694},
        '婢抽棬': {'lat': 22.1987, 'lon': 113.5439},
        '鍙板寳': {'lat': 25.0330, 'lon': 121.5654},
    }

    def __init__(self, config=None):
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WeatherSprite/1.0'
        })

    def get_city_coords(self, city_name):
        """鑾峰彇鍩庡競鍧愭爣"""
        # 鍏堟煡鍐呯疆鏁版嵁搴?
        if city_name in self.CITY_COORDS:
            return self.CITY_COORDS[city_name]

        # 鍚﹀垯鐢ㄥ湴鐞嗙紪鐮丄PI鏌ヨ
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
            print(f"鑾峰彇鍩庡競鍧愭爣澶辫触: {e}")

        # 榛樿杩斿洖鍖椾含
        return self.CITY_COORDS['鍖椾含']

    def get_current_weather(self):
        """鑾峰彇褰撳墠澶╂皵"""
        city = self.config.get('city', '鍖椾含')

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

                # 瑙ｆ瀽澶╂皵浠ｇ爜
                condition, description = self.WEATHER_CODES.get(
                    weather_code, ('unknown', '鏈煡')
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
            print(f"鑾峰彇澶╂皵澶辫触: {e}")

        # 杩斿洖榛樿澶╂皵
        return {
            'condition': 'unknown',
            'description': '鑾峰彇澶辫触',
            'temperature': 0,
            'weather_code': -1,
            'humidity': 0,
            'city': city
        }

    def get_hourly_forecast(self):
        """鑾峰彇灏忔椂棰勬姤"""
        city = self.config.get('city', '鍖椾含')

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
            print(f"鑾峰彇棰勬姤澶辫触: {e}")

        return None

