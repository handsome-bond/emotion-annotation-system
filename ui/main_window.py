import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
from core.exporter import JSONExporter # 导入我们在 core 里写的导出器

class MainWindow:
    def __init__(self, manager, settings):
        self.manager = manager
        self.settings = settings
        self.root = tk.Tk()
        self.root.title("情感标注系统 v2.0 - 完整联机版")
        self.root.geometry("800x650")  
        self.root.minsize(700, 550)    
        
        self.current_file_path = tk.StringVar()
        
        # === 核心状态变量 ===
        self.current_task_id = None
        self.current_segment = 0
        self.total_segments = 0
        self.current_duration = 0.0
        self.segment_duration = self.settings.segment_duration
        self.current_emotion = None
        
        self._setup_ui()

    def _setup_ui(self):
        # ================= 顶部：文件选择区 =================
        frame_file = ttk.LabelFrame(self.root, text="文件选择", padding=10)
        frame_file.pack(padx=20, pady=10, fill="x")
        
        file_sub_frame = ttk.Frame(frame_file)
        file_sub_frame.pack(fill="x", pady=5)
        
        ttk.Label(file_sub_frame, text="媒体文件：").pack(side="left")
        self.entry_path = ttk.Entry(file_sub_frame, textvariable=self.current_file_path, width=60)
        self.entry_path.pack(side="left", padx=5, fill="x", expand=True)
        
        ttk.Button(file_sub_frame, text="浏览...", command=self._browse_file).pack(side="left")
        ttk.Button(frame_file, text="添加并初始化任务", command=self._add_task).pack(pady=10)

        # ================= 中部：情感标注区 =================
        frame_annotation = ttk.LabelFrame(self.root, text="情感标注", padding=10)
        frame_annotation.pack(padx=20, pady=5, fill="both", expand=True)
        
        # 1. 状态信息
        info_frame = ttk.Frame(frame_annotation)
        info_frame.pack(fill="x", pady=5)
        self.lbl_segment = ttk.Label(info_frame, text="当前片段: 0/0", font=("微软雅黑", 10, "bold"))
        self.lbl_segment.pack(side="left", padx=20)
        self.lbl_time = ttk.Label(info_frame, text="时间范围: 0.0s - 0.0s")
        self.lbl_time.pack(side="left")
        
        # 2. 情感按钮网格
        ttk.Label(frame_annotation, text="选择情感：").pack(pady=(10, 0))
        btn_frame = ttk.Frame(frame_annotation)
        btn_frame.pack(pady=10)
        
        emotions = self.settings.emotion_labels
        for i, emotion in enumerate(emotions):
            row = i // 4
            col = i % 4
            btn = ttk.Button(btn_frame, text=emotion, width=12, 
                             command=lambda e=emotion: self._select_emotion(e))
            btn.grid(row=row, column=col, padx=5, pady=5)
            
        self.lbl_selected_emotion = ttk.Label(frame_annotation, text="当前已选情感: 无", foreground="blue")
        self.lbl_selected_emotion.pack()
            
        # 3. 情感强度滑块
        intensity_frame = ttk.Frame(frame_annotation)
        intensity_frame.pack(pady=10)
        ttk.Label(intensity_frame, text="情感强度:").pack(side="left", padx=5)
        
        self.intensity_var = tk.IntVar(value=3)
        # 【修复小数问题】：强制转换为整数
        self.scale_intensity = ttk.Scale(intensity_frame, from_=1, to=self.settings.data['annotation']['intensity_levels'], 
                                         orient="horizontal", variable=self.intensity_var, length=200,
                                         command=lambda s: self.intensity_var.set(int(float(s))))
        self.scale_intensity.pack(side="left", padx=5)
        self.lbl_intensity_val = ttk.Label(intensity_frame, textvariable=self.intensity_var)
        self.lbl_intensity_val.pack(side="left")

        # 4. 备注文本框
        ttk.Label(frame_annotation, text="备注:").pack(anchor="w", padx=20)
        self.text_notes = tk.Text(frame_annotation, height=3, width=60)
        self.text_notes.pack(padx=20, pady=5, fill="x")

        # 5. 底部控制按钮
        ctrl_frame = ttk.Frame(frame_annotation)
        ctrl_frame.pack(pady=15)
        ttk.Button(ctrl_frame, text="◀ 上一片段", command=self._prev_segment).pack(side="left", padx=10)
        ttk.Button(ctrl_frame, text="保存当前标注", command=self._save_annotation).pack(side="left", padx=10)
        ttk.Button(ctrl_frame, text="下一片段 ▶", command=self._next_segment).pack(side="left", padx=10)
        
        ttk.Separator(ctrl_frame, orient="vertical").pack(side="left", padx=15, fill="y")
        ttk.Button(ctrl_frame, text="💾 导出 JSON 结果", command=self._export_json).pack(side="left", padx=10)

        # ================= 底部：状态栏 =================
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

    def _browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.current_file_path.set(file_path)
            self.status_var.set(f"已选择文件: {file_path}")

    def _add_task(self):
        path = self.current_file_path.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("警告", "请先选择一个有效文件！")
            return
            
        self.status_var.set("正在调用 FFmpeg 获取音频时长...")
        self.root.update()
        
        try:
            # 1. 创建任务并存入数据库
            self.current_task_id = self.manager.add_task(path)
            
            # 2. 获取文件时长 (如果没装FFmpeg或失败，默认给个预估值防止崩溃)
            self.current_duration = self.manager.media.get_duration(path)
            if self.current_duration <= 0:
                # 容错机制：假设文件是60秒
                self.current_duration = 60.0 
                messagebox.showwarning("警告", "无法准确读取音频时长（可能未安装 FFmpeg）。已默认按 60 秒处理。")
            
            # 3. 计算切片总数
            self.total_segments = int(self.current_duration // self.segment_duration)
            if self.current_duration % self.segment_duration > 0:
                self.total_segments += 1
                
            # 4. 初始化到第一段
            self.current_segment = 1
            self.current_emotion = None
            self.lbl_selected_emotion.config(text="当前已选情感: 无")
            self.text_notes.delete("1.0", tk.END)
            
            self._update_display()
            self.status_var.set(f"任务 {self.current_task_id} 初始化成功！总时长: {self.current_duration:.1f}s")
            messagebox.showinfo("成功", f"任务加载完成！共分成了 {self.total_segments} 个片段。")
            
        except Exception as e:
            messagebox.showerror("错误", f"添加任务失败: {str(e)}")

    def _update_display(self):
        """刷新时间轴和片段号"""
        if self.total_segments == 0:
            return
            
        start_time = (self.current_segment - 1) * self.segment_duration
        end_time = min(start_time + self.segment_duration, self.current_duration)
        
        self.lbl_segment.config(text=f"当前片段: {self.current_segment} / {self.total_segments}")
        self.lbl_time.config(text=f"时间范围: {start_time:.1f}s - {end_time:.1f}s")

    def _select_emotion(self, emotion):
        self.current_emotion = emotion
        self.lbl_selected_emotion.config(text=f"当前已选情感: {emotion}")

    def _prev_segment(self):
        if self.current_segment > 1:
            self.current_segment -= 1
            self._update_display()
            self.status_var.set("已切换至上一片段")

    def _next_segment(self):
        if self.current_segment < self.total_segments:
            self.current_segment += 1
            self._update_display()
            self.status_var.set("已切换至下一片段")
            
            # 切换时清空当前选择，防止误标
            self.current_emotion = None
            self.lbl_selected_emotion.config(text="当前已选情感: 无")
            self.text_notes.delete("1.0", tk.END)
            self.intensity_var.set(3)

    def _save_annotation(self):
        if not self.current_task_id:
            messagebox.showwarning("提示", "请先添加任务！")
            return
        if not self.current_emotion:
            messagebox.showwarning("提示", "请选择一个情感标签！")
            return
            
        start_time = (self.current_segment - 1) * self.segment_duration
        end_time = min(start_time + self.segment_duration, self.current_duration)
        
        # 组装数据，写入数据库
        data = {
            'task_id': self.current_task_id,
            'segment_index': self.current_segment,
            'start_time': start_time,
            'end_time': end_time,
            'emotion_label': self.current_emotion,
            'intensity': self.intensity_var.get(),
            'notes': self.text_notes.get("1.0", tk.END).strip()
        }
        
        try:
            self.manager.db.save_result(data) # 真实写入数据库
            self.status_var.set(f"✅ 第 {self.current_segment} 段标注已存入数据库！")
            
            # 自动跳到下一段
            if self.current_segment < self.total_segments:
                self._next_segment()
            else:
                messagebox.showinfo("完成", "恭喜！这已经是最后一个片段了，您可以点击导出JSON。")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _export_json(self):
        if not self.current_task_id:
            messagebox.showwarning("提示", "没有正在进行的任务！")
            return
            
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"result_task_{self.current_task_id}.json"
        
        try:
            exporter = JSONExporter(self.manager.db)
            exporter.export_task(self.current_task_id, str(output_file))
            messagebox.showinfo("导出成功", f"JSON 文件已成功导出至：\n\n{output_file.absolute()}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def run(self):
        self.root.mainloop()