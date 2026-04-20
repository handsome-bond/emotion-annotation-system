import yaml
from pathlib import Path

class Settings:
    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self.data = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @property
    def db_path(self): return self.data['database']['path']
    
    @property
    def emotion_labels(self): return self.data['annotation']['emotion_labels']
    
    @property
    def segment_duration(self): return self.data['annotation']['segment_duration_sec']
    
    @property
    def supported_formats(self): return self.data['media']['supported_formats']