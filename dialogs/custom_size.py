import tkinter as tk
from tkinter import ttk, messagebox

class CustomSizeDialog:
    def __init__(self, parent, title, default_name="", default_width="", default_height=""):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        
        # 初始化结果
        self.result = None
        
        # 设置UI
        self.setup_ui(default_name, default_width, default_height)
        
        # 设置模态和居中
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_window(parent)
        
        parent.wait_window(self.dialog)
        
    def center_window(self, parent):
        """使窗口居中显示"""
        self.dialog.update_idletasks()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent.winfo_x() + (parent_width - dialog_width) // 2
        y = parent.winfo_y() + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        
    def setup_ui(self, default_name, default_width, default_height):
        """设置对话框UI"""
        # 名称输入
        name_frame = ttk.Frame(self.dialog, padding=5)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="名称:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=default_name)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        self.name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 宽度输入
        width_frame = ttk.Frame(self.dialog, padding=5)
        width_frame.pack(fill=tk.X, pady=5)
        ttk.Label(width_frame, text="宽度:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value=default_width)
        self.width_entry = ttk.Entry(width_frame, textvariable=self.width_var)
        self.width_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(width_frame, text="mm").pack(side=tk.LEFT)
        
        # 高度输入
        height_frame = ttk.Frame(self.dialog, padding=5)
        height_frame.pack(fill=tk.X, pady=5)
        ttk.Label(height_frame, text="高度:").pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value=default_height)
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var)
        self.height_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(height_frame, text="mm").pack(side=tk.LEFT)
        
        # 按钮
        btn_frame = ttk.Frame(self.dialog, padding=5)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5, expand=True)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.confirm())
        
    def confirm(self):
        """确认输入"""
        # 获取输入值
        name = self.name_var.get().strip()
        width = self.width_var.get().strip()
        height = self.height_var.get().strip()
        
        # 验证输入
        if not name:
            messagebox.showwarning("提示", "请输入名称")
            self.name_entry.focus()
            return
            
        if not width:
            messagebox.showwarning("提示", "请输入宽度")
            self.width_entry.focus()
            return
            
        if not height:
            messagebox.showwarning("提示", "请输入高度")
            self.height_entry.focus()
            return
            
        try:
            width = float(width)
            height = float(height)
        except ValueError:
            messagebox.showwarning("提示", "宽度和高度必须是数字")
            return
            
        if width <= 0 or height <= 0:
            messagebox.showwarning("提示", "宽度和高度必须大于0")
            return
            
        # 保存结果
        self.result = (name, width, height)
        self.dialog.destroy() 