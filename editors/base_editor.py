import tkinter as tk
from tkinter import ttk

class BaseEditor:
    def __init__(self, parent):
        self.parent = parent
        self.is_sliding = False
        self.update_timer = None
        self.original_image = None  # 保存原始图像
        self.setup_variables()
        
    def setup_variables(self):
        """初始化变量 - 由子类实现"""
        pass
        
    def create_slider(self, parent, label_text, variable, from_, to, command):
        """创建统一样式的滑动条"""
        # 主容器
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        # 第一行：标签、数值和重置按钮
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X)
        
        # 标签
        label = ttk.Label(
            header_frame, 
            text=label_text, 
            style='SliderLabel.TLabel'
        )
        label.pack(side=tk.LEFT)
        
        # 重置按钮
        reset_btn = ttk.Button(
            header_frame, 
            text="↺",
            width=2,
            style='Reset.TButton',
            command=lambda: self.reset_slider(variable, value_label, command)
        )
        reset_btn.pack(side=tk.RIGHT)
        
        # 数值显示
        value_label = ttk.Label(
            header_frame,
            text="0.00",
            width=6,
            anchor='e',
            style='Value.TLabel'
        )
        value_label.pack(side=tk.RIGHT, padx=5)
        
        # 第二行：滑动条和刻度
        slider_frame = ttk.Frame(frame)
        slider_frame.pack(fill=tk.X, pady=(2, 0))
        
        # 创建刻度容器
        scale_frame = ttk.Frame(slider_frame)
        scale_frame.pack(fill=tk.X)
        
        # 添加刻度标签
        for i in range(5):
            value = from_ + (to - from_) * i / 4
            pos = i / 4
            ttk.Label(
                scale_frame, 
                text=f"{int(value)}",
                style='Scale.TLabel'
            ).place(relx=pos, rely=1, anchor='s')
        
        # 创建滑动条
        scale = ttk.Scale(
            scale_frame,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            variable=variable,
            command=lambda e: self.on_scale_change(command),
            style='Editor.Horizontal.TScale'
        )
        scale.pack(fill=tk.X, pady=(0, 15))  # 底部留空显示刻度
        
        # 初始化数值显示
        self.update_value_label(variable, value_label)
        
        # 绑定事件
        scale.bind("<ButtonPress-1>", self.start_sliding)
        scale.bind("<ButtonRelease-1>", lambda e: self.stop_sliding(command))
        scale.bind("<B1-Motion>", lambda e: self.update_value_label(variable, value_label))
        
        return scale, value_label
        
    def reset_slider(self, variable, value_label, callback):
        """重置单个滑动条"""
        variable.set(0)
        self.update_value_label(variable, value_label)
        callback()
        
    def start_sliding(self, event):
        """开始滑动"""
        if self.original_image is None:
            self.original_image = self.parent.current_image.copy()
        self.is_sliding = True
        if self.update_timer:
            self.parent.dialog.after_cancel(self.update_timer)
        
    def stop_sliding(self, callback):
        """停止滑动"""
        self.is_sliding = False
        if self.update_timer:
            self.parent.dialog.after_cancel(self.update_timer)
        callback()
        
    def on_scale_change(self, callback):
        """滑动条值改变时的处理"""
        if not self.is_sliding:
            if self.update_timer:
                self.parent.dialog.after_cancel(self.update_timer)
            self.update_timer = self.parent.dialog.after(100, callback)
        
    def update_value_label(self, variable, label):
        """更新数值显示"""
        label.configure(text=f"{variable.get():.2f}")
        
    def on_param_change(self, *args):
        """参数改变时的处理 - 由子类实现"""
        pass
        
    def reset(self):
        """重置所有参数"""
        if self.original_image is not None:
            self.parent.current_image = self.original_image.copy()
            self.parent.update_preview()
            self.original_image = None 