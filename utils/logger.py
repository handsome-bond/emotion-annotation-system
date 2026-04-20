import sys
from pathlib import Path
from loguru import logger

def setup_logger(log_dir="logs", log_level="INFO"):
    """配置日志记录器"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 移除默认控制台输出
    logger.remove()
    
    # 添加彩色控制台输出
    logger.add(
        sys.stdout, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    # 添加文件记录
    logger.add(
        log_path / "annotation_{time:YYYYMMDD}.log",
        rotation="00:00",
        retention="10 days",
        level=log_level,
        encoding="utf-8"
    )
    
    return logger