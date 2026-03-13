# 🌤️ 天气精灵 (Weather Sprite)

一款轻量级 Windows 桌面养成游戏，屏幕角落的小精灵会根据现实天气变化穿着和行为。

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ 功能特点

- 🌈 **实时天气同步** - 根据你所在城市的真实天气变换外观
- 🎮 **互动养成** - 喂食、抚摸、换装，看着它慢慢成长
- 💤 **智能行为** - 饿了会叫，困了会睡，天气好会开心
- 📌 **桌面悬浮** - 永远置顶，陪伴你工作学习
- 🎨 **天气装扮** - 晴天戴墨镜，雨天撑伞，下雪穿棉袄
- 🔔 **系统托盘** - 最小化到托盘，不占任务栏

## 🌦️ 天气对应外观

| 天气 | 精灵外观 | 心情 |
|------|---------|------|
| ☀️ 晴天 | 😎 🌻 | 超级开心！ |
| ☁️ 多云 | 😌 🌤️ | 适合发呆~ |
| 🌧️ 雨天 | ☂️ 🐸 | 记得带伞哦 |
| ❄️ 下雪 | ⛄ 🧣 | 好冷但开心 |
| ⚡ 雷雨 | 😱 🏠 | 有点害怕... |
| 🌫️ 大雾 | 🫥 👻 | 看不清路 |

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行游戏

```bash
python main.py
```

## 🎮 操作指南

| 操作 | 说明 |
|------|------|
| **左键拖拽** | 移动精灵位置 |
| **右键菜单** | 打开功能菜单 |
| **喂食** | 增加饱腹度 |
| **互动** | 摸摸头，增加心情 |
| **换装** | 切换天气主题装扮 |
| **双击托盘** | 显示/隐藏窗口 |

## 🏗️ 项目结构

```
weather_sprite/
├── main.py              # 主程序入口
├── sprite.py            # 精灵核心类
├── weather_api.py       # 天气API模块
├── config.py            # 配置管理
├── settings_dialog.py   # 设置对话框
├── requirements.txt     # 依赖列表
└── README.md           # 说明文档
```

## ⚙️ 配置说明

首次运行会自动创建 `config.json`：

```json
{
  "city": "北京",
  "position": {"x": 100, "y": 100},
  "update_interval": 30,
  "auto_start": false
}
```

## 📝 后续可扩展功能

- [ ] 添加更多精灵皮肤主题
- [ ] 小游戏系统（猜天气、接雨滴等）
- [ ] 成就系统
- [ ] 多语言支持
- [ ] 打包成独立 exe

## 📄 开源协议

MIT License
"# weather_sprite" 
