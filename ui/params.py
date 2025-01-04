import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
from dialogs.size_manager import SizeManagerDialog
from .matting_params import MattingParams
from .background_params import BackgroundParams
from .layout_params import LayoutParams

class ParamsManager:
    def __init__(self, app):
        self.app = app
        self.last_update_time = 0
        self.update_delay = 0.3
        self.is_sliding = False
        
        # 使用HEX格式定义颜色
        self.color_map = {
            "红色": "#FF0000",    # 标准证件照红色
            "蓝色": "#0047BB",    # 标准证件照蓝色
            "白色": "#FFFFFF",    # 纯白色
            "深蓝": "#004B97",    # 深蓝色
            "浅灰": "#F0F0F0",    # 浅灰色
            "自定义": None        # 自定义颜色，初始为None
        }
        
        # 预设颜色列表
        self.preset_colors = list(self.color_map.keys())
        
        # 初始化各个参数页
        self.matting_params = MattingParams(self.app, self.app.params_notebook)
        self.background_params = BackgroundParams(self.app, self.app.params_notebook)
        self.layout_params = LayoutParams(self.app, self.app.params_notebook)
        
    def start_sliding(self):
        """开始滑动"""
        self.is_sliding = True
        
    def stop_sliding(self):
        """停止滑动"""
        self.is_sliding = False
        if hasattr(self.app, 'transparent_image'):
            self.app.image_processor.process_matting()
            
    def manage_sizes(self):
        """管理尺寸"""
        SizeManagerDialog(self.app.window, self.refresh_sizes)
        
    def refresh_sizes(self):
        """刷新尺寸列表"""
        # 加载照片尺寸
        try:
            with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                photo_sizes = json.load(f)
                photo_size_list = list(photo_sizes.keys())
        except Exception as e:
            print(f"加载照片尺寸失败: {str(e)}")
            photo_size_list = []
            
        # 加载纸张尺寸
        try:
            with open('paper_sizes.json', 'r', encoding='utf-8') as f:
                paper_sizes = json.load(f)
                paper_size_list = list(paper_sizes.keys())
        except Exception as e:
            print(f"加载纸张尺寸失败: {str(e)}")
            paper_size_list = []
            
        # 更新下拉列表
        if hasattr(self.layout_params, 'photo_combobox'):
            self.layout_params.photo_combobox['values'] = photo_size_list
            if photo_size_list:
                self.layout_params.photo_combobox.set(photo_size_list[0])
                
        if hasattr(self.layout_params, 'paper_combobox'):
            self.layout_params.paper_combobox['values'] = paper_size_list
            if paper_size_list:
                self.layout_params.paper_combobox.set(paper_size_list[0])
        
    def load_sizes(self, filename):
        """加载尺寸数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}