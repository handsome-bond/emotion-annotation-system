import subprocess
import json

class MediaProcessor:
    def __init__(self, settings):
        self.settings = settings

    def get_media_info(self, file_path):
        """使用 ffprobe 获取媒体文件信息"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout)
        except Exception as e:
            return None

    def get_duration(self, file_path):
        info = self.get_media_info(file_path)
        if info:
            return float(info['format']['duration'])
        return 0