import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from beauty.skin_beauty import SkinBeauty
from beauty.face_beauty import FaceBeauty
from editors.base_editor import BaseEditor

class BeautyEditor(BaseEditor):
    def __init__(self, parent):
        super().__init__(parent)  # 调用父类初始化
        self.skin_beauty = SkinBeauty()
        self.face_beauty = FaceBeauty()
        
    def setup_variables(self):
        """初始化变量"""
        self.skin_smoothing_var = tk.IntVar(value=0)  # 磨皮
        self.skin_whitening_var = tk.IntVar(value=0)  # 美白
        self.face_slimming_var = tk.IntVar(value=0)   # 瘦脸
        self.eye_enlarging_var = tk.IntVar(value=0)   # 大眼
        
    def create_widgets(self, notebook):
        """创建编辑器控件"""
        beauty_frame = ttk.Frame(notebook, padding=5)
        notebook.add(beauty_frame, text="本地美颜")
        
        # 创建滑动条容器
        sliders_frame = ttk.Frame(beauty_frame)
        sliders_frame.pack(fill=tk.X, expand=True)
        
        # 磨皮调节 - 更自然的范围
        self.create_slider(
            sliders_frame,
            "磨皮:",
            self.skin_smoothing_var,
            0, 50,  # 调整范围
            self.on_param_change
        )
        
        # 美白调节 - 更合理的范围
        self.create_slider(
            sliders_frame,
            "美白:",
            self.skin_whitening_var,
            0, 30,  # 调整范围
            self.on_param_change
        )
        
        # 瘦脸调节 - 避免过度变形
        self.create_slider(
            sliders_frame,
            "瘦脸:",
            self.face_slimming_var,
            0, 20,  # 调整范围
            self.on_param_change
        )
        
        # 大眼调节 - 保持自然
        self.create_slider(
            sliders_frame,
            "大眼:",
            self.eye_enlarging_var,
            0, 15,  # 调整范围
            self.on_param_change
        )
        
        # 添加重置按钮容器
        reset_frame = ttk.Frame(beauty_frame)
        reset_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 添加重置按钮（右对齐）
        ttk.Button(
            reset_frame,
            text="重置美颜参数",
            command=self.reset_beauty_params,
            style='Small.TButton',
            width=12
        ).pack(side=tk.RIGHT)
        
    def reset_beauty_params(self):
        """重置美颜参数"""
        # 保存当前滑动状态
        old_sliding = self.is_sliding
        self.is_sliding = False
        
        try:
            # 重置所有参数
            self.skin_smoothing_var.set(0)
            self.skin_whitening_var.set(0)
            self.face_slimming_var.set(0)
            self.eye_enlarging_var.set(0)
            
            # 恢复原始图像
            if hasattr(self, 'original_image'):
                self.parent.current_image = self.original_image.copy()
                self.parent.update_preview()
                
        finally:
            # 恢复滑动状态
            self.is_sliding = old_sliding
            
    def on_param_change(self, *args):
        """参数改变时的处理"""
        if self.is_sliding:
            # 滑动时使用低质量预览
            self.update_preview(quality='low')
            return
            
        # 停止滑动后使用高质量预览
        self.update_preview(quality='high')
        
    def update_preview(self, quality='high'):
        """更新预览"""
        # 保存原始图像
        if not hasattr(self, 'original_image'):
            self.original_image = self.parent.current_image.copy()
            
        # 获取基准图像
        image = self.original_image.copy()
        
        # 根据质量选择不同的处理方式
        if quality == 'low':
            # 低质量模式 - 缩小图像处理以提高性能
            scale = 0.5
            small_image = cv2.resize(image, None, fx=scale, fy=scale)
            processed = self.process_beauty(small_image)
            image = cv2.resize(processed, (image.shape[1], image.shape[0]))
        else:
            # 高质量模式 - 直接处理原图
            image = self.process_beauty(image)
            
        # 更新预览
        self.parent.current_image = image
        self.parent.update_preview()
        
    def process_beauty(self, image):
        """处理美颜效果"""
        # 应用磨皮
        if self.skin_smoothing_var.get() > 0:
            image = self.skin_beauty.smooth_skin(
                image, 
                self.skin_smoothing_var.get()
            )
        
        # 应用美白
        if self.skin_whitening_var.get() > 0:
            image = self.skin_beauty.whiten_skin(
                image,
                self.skin_whitening_var.get()
            )
        
        # 应用瘦脸
        if self.face_slimming_var.get() > 0:
            image = self.face_beauty.slim_face(
                image,
                self.face_slimming_var.get()
            )
        
        # 应用大眼
        if self.eye_enlarging_var.get() > 0:
            image = self.face_beauty.enlarge_eyes(
                image,
                self.eye_enlarging_var.get()
            )
            
        return image