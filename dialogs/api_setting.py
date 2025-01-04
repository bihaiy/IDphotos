import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class APISettingDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("API设置")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # 加载当前API配置
        self.load_api_config()
        
        # 设置对话框UI
        self.setup_ui()
        
        # 设置模态和居中
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 窗口居中
        self.center_window(parent)
        
        parent.wait_window(self.dialog)
        
    def center_window(self, parent):
        """使窗口居中显示"""
        self.dialog.update_idletasks()
        
        # 获取父窗口和对话框的尺寸
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 计算居中位置
        x = parent.winfo_x() + (parent_width - dialog_width) // 2
        y = parent.winfo_y() + (parent_height - dialog_height) // 2
        
        # 设置窗口位置
        self.dialog.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        """设置对话框UI"""
        # API Key输入
        key_frame = ttk.Frame(self.dialog, padding=5)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="API Key:").pack(side=tk.LEFT)
        self.key_var = tk.StringVar(value=self.api_key)
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var)
        self.key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # API Secret输入
        secret_frame = ttk.Frame(self.dialog, padding=5)
        secret_frame.pack(fill=tk.X, pady=5)
        ttk.Label(secret_frame, text="API Secret:").pack(side=tk.LEFT)
        self.secret_var = tk.StringVar(value=self.api_secret)
        self.secret_entry = ttk.Entry(secret_frame, textvariable=self.secret_var, show="*")
        self.secret_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 显示/隐藏API Secret按钮
        self.show_secret = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            secret_frame, 
            text="显示", 
            variable=self.show_secret,
            command=lambda: self.secret_entry.configure(show="" if self.show_secret.get() else "*")
        ).pack(side=tk.LEFT)
        
        # 按钮
        btn_frame = ttk.Frame(self.dialog, padding=5)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5, expand=True)
        
    def load_api_config(self):
        """从配置文件加载API信息"""
        self.api_key = ""
        self.api_secret = ""
        
        try:
            if os.path.exists('api_config.json'):
                with open('api_config.json', 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key', '')
                    self.api_secret = config.get('api_secret', '')
        except:
            pass
            
    def save(self):
        """保存API设置"""
        # 获取输入值
        api_key = self.key_var.get().strip()
        api_secret = self.secret_var.get().strip()
        
        # 保存到配置文件
        if api_key and api_secret:
            config = {
                'api_key': api_key,
                'api_secret': api_secret
            }
            
            with open('api_config.json', 'w') as f:
                json.dump(config, f)
        
        self.dialog.destroy() 