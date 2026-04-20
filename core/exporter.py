import json
from datetime import datetime

class JSONExporter:
    def __init__(self, db_manager):
        self.db = db_manager

    def export_task(self, task_id, output_path):
        """导出指定任务的标注结果为 JSON"""
        with self.db._get_connection() as conn:
            # 获取任务信息
            task = conn.execute("SELECT * FROM annotation_tasks WHERE id=?", (task_id,)).fetchone()
            # 获取标注记录
            results = conn.execute("SELECT * FROM annotation_results WHERE task_id=?", (task_id,)).fetchall()
            
        data = {
            "task_id": task_id,
            "export_time": datetime.now().isoformat(),
            "annotations": [
                {
                    "segment_index": r[2],
                    "start_time": r[3],
                    "end_time": r[4],
                    "emotion": r[5],
                    "intensity": r[6]
                } for r in results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)