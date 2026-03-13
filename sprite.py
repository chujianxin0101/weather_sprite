#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气精灵 - 天气本身的元素化身
每种天气都是一个独特的精灵形态
"""

import json
import random
from datetime import datetime
from pathlib import Path


class WeatherElement:
    """天气元素基类"""

    def __init__(self, weather_type):
        self.type = weather_type
        self.animation_frame = 0
        self.animation_timer = 0

    def get_frame(self):
        """获取当前动画帧"""
        self.animation_timer += 1
        return self._animate()

    def _animate(self):
        """子类实现动画"""
        raise NotImplementedError

    def interact(self, interaction_type):
        """互动反应"""
        raise NotImplementedError


class SunnySprite(WeatherElement):
    """☀️ 太阳精灵 - 活泼、温暖、发光"""

    FRAMES = ['☀️', '🌞', '☀️', '✨']
    RAYS = ['✨', '💫', '⭐', '🌟']

    def __init__(self):
        super().__init__('sunny')
        self.name = '太阳精灵'
        self.energy = 100
        self.brightness = 1.0

    def _animate(self):
        """太阳发光动画"""
        if self.animation_timer % 8 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.FRAMES)

        # 偶尔发射光芒
        if random.random() < 0.1:
            return {'emoji': random.choice(self.RAYS), 'effect': 'sparkle'}

        return {
            'emoji': self.FRAMES[self.animation_frame],
            'effect': 'glow',
            'glow_intensity': 0.8 + (self.animation_timer % 10) * 0.02
        }

    def interact(self, interaction_type):
        reactions = {
            'pet': '好暖和~ ☀️',
            'play': '光芒四射！✨',
            'talk': '今天是个好日子！',
            'feed': '太阳喜欢光合作用！🌻'
        }
        return reactions.get(interaction_type, '☀️')


class RainSprite(WeatherElement):
    """🌧️ 雨滴精灵 - 清新、流动、滋润"""

    FRAMES = ['💧', '💦', '🌧️', '💧']
    SPLASHES = ['🌊', '💦', '💧', '🫧']

    def __init__(self):
        super().__init__('rainy')
        self.name = '雨滴精灵'
        self.intensity = 0.5

    def _animate(self):
        """雨滴下落动画"""
        if self.animation_timer % 6 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.FRAMES)

        # 雨滴溅起水花
        if random.random() < 0.15:
            return {'emoji': random.choice(self.SPLASHES), 'effect': 'splash'}

        return {
            'emoji': self.FRAMES[self.animation_frame],
            'effect': 'fall',
            'offset_y': (self.animation_timer % 5) * 2
        }

    def interact(self, interaction_type):
        reactions = {
            'pet': '湿漉漉的~ 💧',
            'play': '踩水坑！💦',
            'talk': '雨声很治愈呢~',
            'feed': '雨滴汇成小溪流~ 🌊'
        }
        return reactions.get(interaction_type, '🌧️')


class CloudSprite(WeatherElement):
    """☁️ 云朵精灵 - 柔软、飘浮、变化"""

    FRAMES = ['☁️', '🌥️', '☁️', '🌤️']
    SHAPES = ['☁️', '🌫️', '💨', '🌥️']

    def __init__(self):
        super().__init__('cloudy')
        self.name = '云朵精灵'
        self.density = 0.6

    def _animate(self):
        """云朵飘浮动画"""
        if self.animation_timer % 10 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.FRAMES)

        # 云朵变形
        if random.random() < 0.08:
            return {'emoji': random.choice(self.SHAPES), 'effect': 'morph'}

        # 飘浮效果
        drift = ((self.animation_timer % 20) - 10) * 0.5

        return {
            'emoji': self.FRAMES[self.animation_frame],
            'effect': 'float',
            'offset_x': drift
        }

    def interact(self, interaction_type):
        reactions = {
            'pet': '软绵绵的~ ☁️',
            'play': '躲猫猫！我在云里~',
            'talk': '云朵像棉花糖一样~',
            'feed': '云朵喝水变大了！'
        }
        return reactions.get(interaction_type, '☁️')


class SnowSprite(WeatherElement):
    """❄️ 雪花精灵 - 晶莹、飘落、寒冷"""

    FRAMES = ['❄️', '❅', '❆', '❄️']
    FLAKES = ['❄️', '❅', '✦', '✧', '❆']

    def __init__(self):
        super().__init__('snowy')
        self.name = '雪花精灵'
        self.coldness = 0.8

    def _animate(self):
        """雪花飘落动画"""
        if self.animation_timer % 7 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.FRAMES)

        # 不同形状的雪花
        if random.random() < 0.12:
            return {'emoji': random.choice(self.FLAKES), 'effect': 'flutter'}

        # 旋转飘落
        rotation = (self.animation_timer % 8) * 45

        return {
            'emoji': self.FRAMES[self.animation_frame],
            'effect': 'snow_fall',
            'rotation': rotation,
            'offset_y': (self.animation_timer % 6) * 1.5
        }

    def interact(self, interaction_type):
        reactions = {
            'pet': '冰冰凉凉的~ ❄️',
            'play': '堆雪人啦！⛄',
            'talk': '每片雪花都是独一无二的~',
            'feed': '雪花融化成水滴~ 💧'
        }
        return reactions.get(interaction_type, '❄️')


class ThunderSprite(WeatherElement):
    """⚡ 雷电精灵 - 强烈、爆发、能量"""

    FRAMES = ['⚡', '⛈️', '🌩️', '⚡']
    SPARKS = ['⚡', '✦', '💥', '🌟', '⚡']

    def __init__(self):
        super().__init__('thunder')
        self.name = '雷电精灵'
        self.power = 1.0

    def _animate(self):
        """雷电闪烁动画"""
        # 雷电快速闪烁
        if self.animation_timer % 3 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.FRAMES)

        # 随机放电
        if random.random() < 0.2:
            return {'emoji': random.choice(self.SPARKS), 'effect': 'flash'}

        # 能量波动
        intensity = 1.0 if self.animation_timer % 4 < 2 else 0.7

        return {
            'emoji': self.FRAMES[self.animation_frame],
            'effect': 'thunder',
            'flash': intensity > 0.9
        }

    def interact(self, interaction_type):
        reactions = {
            'pet': '噼里啪啦！⚡',
            'play': '释放能量！💥',
            'talk': '轰隆隆！好大的声音！',
            'feed': '充电中！⚡🔋'
        }
        return reactions.get(interaction_type, '⚡')


class FogSprite(WeatherElement):
    """🌫️ 雾精灵 - 朦胧、流动、神秘"""

    FRAMES = ['🌫️', '🌁', '🌫️', '😶\u200d🌫️']
    MISTS = ['🌫️', '😶\u200d🌫️', '🌁', '👻']

    def __init__(self):
        super().__init__('foggy')
        self.name = '雾精灵'
        self.thickness = 0.7

    def _animate(self):
        """雾气流动动画"""
        if self.animation_timer % 12 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.FRAMES)

        # 雾气聚散
        if random.random() < 0.1:
            return {'emoji': random.choice(self.MISTS), 'effect': 'swirl'}

        # 透明度变化
        opacity = 0.5 + (self.animation_timer % 10) * 0.05

        return {
            'emoji': self.FRAMES[self.animation_frame],
            'effect': 'mist',
            'opacity': opacity
        }

    def interact(self, interaction_type):
        reactions = {
            'pet': '雾蒙蒙的~ 🌫️',
            'play': '捉迷藏！找不到我了吧~',
            'talk': '雾里看花，水中望月~',
            'feed': '雾气凝结成露珠~ 💧'
        }
        return reactions.get(interaction_type, '🌫️')


class UnknownSprite(WeatherElement):
    """❓ 未知天气精灵 - 神秘、变化"""

    FRAMES = ['❓', '🌈', '✨', '❓']

    def __init__(self):
        super().__init__('unknown')
        self.name = '神秘精灵'

    def _animate(self):
        if self.animation_timer % 10 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.FRAMES)
        return {'emoji': self.FRAMES[self.animation_frame], 'effect': 'mystery'}

    def interact(self, interaction_type):
        return '神秘的天气... 🌈'


class Sprite:
    """天气精灵主类 - 当前天气的化身"""

    # 天气类型映射
    WEATHER_ELEMENTS = {
        'sunny': SunnySprite,
        'rainy': RainSprite,
        'cloudy': CloudSprite,
        'snowy': SnowSprite,
        'thunder': ThunderSprite,
        'foggy': FogSprite,
        'unknown': UnknownSprite,
    }

    # 天气属性
    WEATHER_ATTRS = {
        'sunny': {'name': '太阳精灵', 'color': '#FFD54F', 'nature': '温暖活泼'},
        'rainy': {'name': '雨滴精灵', 'color': '#4FC3F7', 'nature': '清新治愈'},
        'cloudy': {'name': '云朵精灵', 'color': '#B0BEC5', 'nature': '柔软飘浮'},
        'snowy': {'name': '雪花精灵', 'color': '#E1F5FE', 'nature': '晶莹纯洁'},
        'thunder': {'name': '雷电精灵', 'color': '#7E57C2', 'nature': '强烈能量'},
        'foggy': {'name': '雾精灵', 'color': '#CFD8DC', 'nature': '神秘朦胧'},
        'unknown': {'name': '神秘精灵', 'color': '#B39DDB', 'nature': '未知变化'},
    }

    def __init__(self):
        self.state_file = Path('sprite_state.json')
        self.weather_type = 'unknown'
        self.current_element = UnknownSprite()

        # 天气数据
        self.temperature = 20
        self.humidity = 50
        self.city = '北京'

        # 养成属性 - 初始为最低值
        self.hunger = 5
        self.mood = 5
        self.energy = 5
        self.level = 1
        self.exp = 0

        # 统计
        self.feed_count = 0
        self.interact_count = 0
        self.created_at = datetime.now().isoformat()
        self.collected_weathers = set()

        self.load_state()

    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.collected_weathers = set(data.get('collected_weathers', []))
                    self.level = data.get('level', 1)
                    self.exp = data.get('exp', 0)
                    self.feed_count = data.get('feed_count', 0)
                    self.interact_count = data.get('interact_count', 0)
            except Exception as e:
                print(f"加载状态失败: {e}")

    def save_state(self):
        """保存状态"""
        data = {
            'collected_weathers': list(self.collected_weathers),
            'level': self.level,
            'exp': self.exp,
            'feed_count': self.feed_count,
            'interact_count': self.interact_count,
            'last_saved': datetime.now().isoformat(),
        }
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")

    def set_weather(self, weather_data):
        """切换天气形态 - 变身！"""
        old_type = self.weather_type
        new_type = weather_data.get('condition', 'unknown')

        if new_type != old_type:
            # 变身！
            self.weather_type = new_type
            self.current_element = self.WEATHER_ELEMENTS.get(
                new_type, UnknownSprite
            )()
            self.collected_weathers.add(new_type)

            # 新天气 bonus
            self.mood = min(100, self.mood + 10)
            self.energy = min(100, self.energy + 5)

            # 首次收集奖励
            if new_type not in self.collected_weathers:
                self.add_exp(20)

        # 更新数据
        self.temperature = weather_data.get('temperature', 20)
        self.humidity = weather_data.get('humidity', 50)
        self.city = weather_data.get('city', '北京')

    def get_next_frame(self):
        """获取当前帧"""
        return self.current_element.get_frame()

    def get_current_emoji(self):
        """当前表情"""
        return self.current_element.get_frame()['emoji']

    def interact(self, interaction_type='general'):
        """互动"""
        self.interact_count += 1

        # 天气元素特有的反应
        reaction = self.current_element.interact(interaction_type)

        # 属性变化
        self.mood = min(100, self.mood + 15)
        self.energy = max(0, self.energy - 5)
        self.add_exp(5)

        return reaction

    # 食物定义
    FOODS = {
        '☀️': {'name': '阳光能量', 'hunger': 25, 'mood': 10, 'energy': 15},
        '💧': {'name': '雨露精华', 'hunger': 25, 'mood': 10, 'energy': 15},
        '☁️': {'name': '云气', 'hunger': 25, 'mood': 10, 'energy': 15},
        '❄️': {'name': '冰雪精华', 'hunger': 25, 'mood': 10, 'energy': 15},
        '⚡': {'name': '电能', 'hunger': 25, 'mood': 10, 'energy': 15},
        '🌫️': {'name': '雾气', 'hunger': 25, 'mood': 10, 'energy': 15},
        '🍎': {'name': '苹果', 'hunger': 15, 'mood': 5, 'energy': 5},
        '🍰': {'name': '蛋糕', 'hunger': 20, 'mood': 15, 'energy': 10},
    }

    def feed(self, food_type=None):
        """喂食 - 吸收自然能量"""
        if self.hunger >= 95:
            return None, '已经充满能量了！'

        self.feed_count += 1

        # 获取食物信息
        food = self.FOODS.get(food_type, {'name': '自然能量', 'hunger': 20, 'mood': 8, 'energy': 10})

        # 应用食物效果
        self.hunger = min(100, self.hunger + food['hunger'])
        self.mood = min(100, self.mood + food['mood'])
        self.energy = min(100, self.energy + food['energy'])
        self.add_exp(5)

        # 根据天气返回不同的描述
        weather_desc = {
            'sunny': '吸收阳光，活力满满！',
            'rainy': '滋润万物，生机勃勃！',
            'cloudy': '飘飘欲仙，悠然自得~',
            'snowy': '晶莹剔透，纯净无暇！',
            'thunder': '充满力量，能量爆发！',
            'foggy': '神秘莫测，若隐若现~',
        }
        desc = weather_desc.get(self.weather_type, '补充元气！')

        return food_type or '✨', f"吃了{food['name']}，{desc}"

    def add_exp(self, amount):
        """增加经验"""
        self.exp += amount
        needed = self.level * 50
        if self.exp >= needed:
            self.level_up()
            return True
        return False

    def level_up(self):
        """升级"""
        self.level += 1
        self.exp = 0
        self.mood = 100
        self.energy = 100
        self.hunger = 80

    def get_mood_text(self):
        """心情描述"""
        attrs = self.WEATHER_ATTRS.get(self.weather_type, self.WEATHER_ATTRS['unknown'])

        if self.energy < 20:
            return f"{attrs['name']}累了，需要休息..."
        if self.mood > 80:
            return f"{attrs['name']}心情很好，{attrs['nature']}~"
        if self.mood < 30:
            return f"{attrs['name']}有点低落..."

        weather_desc = {
            'sunny': '散发着温暖的光芒',
            'rainy': '淅淅沥沥地下着',
            'cloudy': '慢悠悠地飘浮着',
            'snowy': '轻盈地飘落',
            'thunder': '轰隆隆地释放能量',
            'foggy': '朦胧地流动着',
        }

        return f"{attrs['name']}{weather_desc.get(self.weather_type, '在变化')}"

    def get_status_bar(self):
        """状态条"""
        def bar(value, full='●', empty='○'):
            filled = int(value / 100 * 4)
            return full * filled + empty * (4 - filled)

        return f"能量:{bar(self.hunger)} 活力:{bar(self.mood)}"

    def get_status(self):
        """完整状态"""
        attrs = self.WEATHER_ATTRS.get(self.weather_type, self.WEATHER_ATTRS['unknown'])
        return {
            'weather': self.weather_type,
            'weather_name': attrs['name'],
            'nature': attrs['nature'],
            'temperature': self.temperature,
            'city': self.city,
            'hunger': int(self.hunger),
            'mood': int(self.mood),
            'energy': int(self.energy),
            'level': self.level,
            'exp': self.exp,
            'exp_needed': self.level * 50,
            'collected': len(self.collected_weathers),
        }

    def update(self):
        """每帧更新"""
        # 能量自然衰减
        self.hunger = max(0, self.hunger - 0.2)
        self.energy = max(0, self.energy - 0.1)

        # 天气特性影响
        if self.weather_type == 'sunny':
            self.energy = min(100, self.energy + 0.1)  # 太阳恢复能量
        elif self.weather_type == 'rainy':
            self.hunger = min(100, self.hunger + 0.05)  # 雨水滋润

        if random.random() < 0.002:
            self.save_state()
