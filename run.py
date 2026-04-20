#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 获取当前脚本所在的根目录
ROOT_DIR = Path(__file__).resolve().parent

# 【关键修正】将根目录添加到系统路径，确保所有包都能被找到
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 采用方案二后的简洁导入方式
try:
    from config import Settings
    from database import DatabaseManager
    from core import MediaProcessor, AnnotationManager
    from ui import MainWindow
    from utils import setup_logger
except ImportError as e:
    print(f"❌ 导入失败！请确保项目文件夹结构完整（需包含 config, core, ui 等文件夹）。\n错误信息: {e}")
    sys.exit(1)

def main():
    # 1. 初始化配置与日志
    settings = Settings("config.yaml")
    logger = setup_logger()
    logger.info("🚀 情感标注系统正在启动...")

    # 2. 实例化各个组件
    # 注意：data/ 文件夹不存在时会自动创建
    Path("data").mkdir(exist_ok=True)
    
    db = DatabaseManager(settings.db_path)
    media = MediaProcessor(settings)
    manager = AnnotationManager(settings, db, media)
    
    # 3. 启动主窗口
    logger.info("显示用户界面...")
    app = MainWindow(manager, settings)
    app.run()

if __name__ == "__main__":
    main()