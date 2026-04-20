# 情感标注系统 (Emotion Annotation System)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![FFmpeg](https://img.shields.io/badge/Dependency-FFmpeg-orange.svg)

这是一个基于 Python 的桌面端音视频情感标注工具，旨在帮助标注员对长媒体文件进行分段听辨、情感倾向打标及强度评估。系统支持自动化切片处理，并能输出符合数据分析标准的结构化 JSON 结果。

## ✨ 核心特性

- **跨格式支持**：兼容 MP3, WAV, MP4, AVI, MOV 等主流音视频格式。
- **自动时长解析**：集成 FFmpeg，自动计算媒体总时长并按设定间隔（默认 10s）生成标注片段。
- **多维度标注**：支持 8 种内置情感标签及 5 级情感强度调节，并提供备注功能。
- **数据本地持久化**：采用 SQLite 数据库实时保存标注进度，支持断点续标，防止数据丢失。
- **标准化 JSON 导出**：一键导出包含任务信息、时间戳和标注详情的 JSON 文件。

## 📂 项目结构描述

```text
emotion_annotation_system/       # 项目根目录
│
├── config/                      # 1. ⚙️ 配置模块：管理系统所有参数
│   ├── __init__.py
│   └── settings.py              # 读取解析 config.yaml，供全局调用
│
├── core/                        # 2. 🧠 核心逻辑层：处理业务，不碰UI
│   ├── __init__.py
│   ├── media_processor.py       # 音视频处理引擎（调用 FFmpeg 提取音频、切片等）
│   ├── annotation_manager.py    # 标注任务调度与状态管理
│   └── exporter.py              # 负责将标注结果格式化并导出为结构化 JSON
│
├── database/                    # 3. 💾 数据持久化层：管理数据库操作
│   ├── __init__.py
│   └── models.py                # 数据库表结构定义与读写逻辑（使用 SQLite）
│
├── ui/                          # 4. 🖥️ 用户界面层：只负责显示和接收点击
│   ├── __init__.py
│   ├── main_window.py           # 软件主窗口框架
│   └── components.py            # 可复用的UI小部件（如：视频播放器容器、标注按钮组）
│
├── utils/                       # 5. 🛠️ 通用工具箱
│   ├── __init__.py
│   └── logger.py                # 日志记录工具，方便排查报错
│
├── data/                        # 6. 📁 本地数据文件夹（程序运行时自动生成）
│   ├── input/                   # 建议存放待处理的原始音视频
│   ├── output/                  # 导出的 JSON 结果文件将保存在这里
│   └── temp/                    # 存放切片等临时文件（软件关闭时可自动清理）
│
├── logs/                        # 7. 📝 运行日志文件夹
│
├── config.yaml                  # 📝 暴露给用户的配置文件（定义情感标签、界面语言等）
├── requirements.txt             # 📦 Python 依赖包列表
├── README.md                    # 📖 项目说明文档
└── run.py                       # 🚀 系统的唯一启动入口
```

## 🚀 快速上手

### 1\. 环境准备

确保你的电脑已安装 Python 3.8+ 并且已将 **FFmpeg** 添加至系统环境变量（用于获取媒体时长）。

### 2\. 安装依赖

```bash
pip install -r requirements.txt
```

### 3\. 修改配置 (可选)

编辑 `config.yaml` 调整情感标签或分段时长：

```yaml
annotation:
  emotion_labels: ["高兴", "悲伤", "愤怒", "恐惧", "惊讶", "厌恶", "中性", "其他"]
  segment_duration_sec: 10
```

### 4\. 运行程序

```bash
python run.py
```

## 📝 标注流程说明

1.  **导入媒体**：点击“浏览”选择文件，点击“添加并初始化任务”。
2.  **情感标注**：选择情感标签，调节强度滑块（1-5），填写备注（可选）。
3.  **保存进度**：点击“保存当前标注”，系统将数据存入数据库并自动跳转至下一片段。
4.  **一键导出**：标注完成后，点击“导出 JSON 结果”，文件将生成在 `data/output/` 目录下。

## 📋 输出 JSON 示例

```json
{
  "task_id": 1,
  "export_time": "2026-04-20T21:05:17",
  "annotations": [
    {
      "segment_index": 1,
      "start_time": 0.0,
      "end_time": 10.0,
      "emotion": "悲伤",
      "intensity": 3
    }
  ]
}
```

## ⚖️ 开源协议

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 授权。
