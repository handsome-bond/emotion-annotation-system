import queue
import threading
from .exporter import JSONExporter
class AnnotationManager:
    def __init__(self, settings, db_manager, media_processor):
        self.settings = settings
        self.db = db_manager
        self.media = media_processor
        self.task_queue = queue.Queue()

    def add_task(self, file_path):
        duration = self.media.get_duration(file_path)
        with self.db._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO annotation_tasks (media_path, total_duration) VALUES (?, ?)",
                (file_path, duration)
            )
            return cursor.lastrowid