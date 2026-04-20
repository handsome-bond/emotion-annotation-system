import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            # 标注任务表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS annotation_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    media_path TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    total_duration REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # 标注结果表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS annotation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    segment_index INTEGER,
                    start_time REAL,
                    end_time REAL,
                    emotion_label TEXT,
                    intensity INTEGER,
                    notes TEXT,
                    FOREIGN KEY (task_id) REFERENCES annotation_tasks (id)
                )
            ''')

    def save_result(self, data):
        """保存单条标注结果"""
        query = '''INSERT INTO annotation_results 
                   (task_id, segment_index, start_time, end_time, emotion_label, intensity, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)'''
        with self._get_connection() as conn:
            conn.execute(query, (
                data['task_id'], data['segment_index'], data['start_time'],
                data['end_time'], data['emotion_label'], data['intensity'], data['notes']
            ))