import tkinter as tk
from tkinter import ttk
import json

class MattingParams:
    def __init__(self, app, parent_notebook):
        self.app = app
        
        # 添加抠图模型映射
        self.matting_model_map = {
            "MODNet（抠图效果好，速度中等）": "modnet_photographic_portrait_matting",
            "birefnet-v1-lite（抠图效果好，速度慢）": "birefnet-v1-lite",
            "hivision_modnet（纯色换底好，速度快）": "hivision_modnet",
            "rmbg-1.4（背景复杂换底好，速度快）": "rmbg-1.4"
        }
        
        self.face_model_map = {
            "Face++ (精度高，需要联网和API Key)": "face++",
            "mtcnn（速度快，精度低）": "mtcnn",
            "retinaface-resnet50（速度慢，精度高）": "retinaface-resnet50"
        }
        
        self.setup_matting_params(parent_notebook)
        
    def setup_matting_params(self, parent_notebook):
        """设置抠图参数标签页"""
        matting_frame = ttk.Frame(parent_notebook, padding=5)
        parent_notebook.add(matting_frame, text="抠图参数")
        
        # 抠图模型选择
        model_frame = ttk.LabelFrame(matting_frame, text="抠图模型", padding=2)
        model_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 模型选择下拉框
        display_name = "MODNet（抠图效果好，速度中等）"
        self.matting_model_var = tk.StringVar(value=display_name)
        self.model_combobox = ttk.Combobox(
            model_frame, 
            textvariable=self.matting_model_var,
            values=list(self.matting_model_map.keys()),
            state="readonly"
        )
        self.model_combobox.pack(fill=tk.X)
        
        # 人脸检测模型选择
        face_frame = ttk.LabelFrame(matting_frame, text="人脸检测", padding=2)
        face_frame.pack(fill=tk.X, pady=(0, 2))
        
        display_name = "retinaface-resnet50（速度慢，精度高）"
        self.face_model_var = tk.StringVar(value=display_name)
        self.face_combobox = ttk.Combobox(
            face_frame,
            textvariable=self.face_model_var,
            values=list(self.face_model_map.keys()),
            state="readonly"
        )
        self.face_combobox.pack(fill=tk.X)
        
        # 抠图尺寸选择
        size_frame = ttk.LabelFrame(matting_frame, text="抠图尺寸", padding=2)
        size_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 加载证件照尺寸数据
        try:
            with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                self.photo_sizes = json.load(f)
        except:
            self.photo_sizes = {}
            
        photo_size_list = list(self.photo_sizes.keys())
        
        # 抠图尺寸下拉框
        self.matting_size_var = tk.StringVar(value="一寸 (25×35mm)")
        self.matting_size_combobox = ttk.Combobox(
            size_frame,
            textvariable=self.matting_size_var,
            values=photo_size_list,
            state="readonly"
        )
        self.matting_size_combobox.pack(fill=tk.X)
        
        # 基本参数设置
        basic_frame = ttk.LabelFrame(matting_frame, text="基本参数", padding=2)
        basic_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 面部比例
        ratio_frame = ttk.Frame(basic_frame)
        ratio_frame.pack(fill=tk.X, pady=0)
        
        # 标签和数值显示容器
        ratio_label_frame = ttk.Frame(ratio_frame)
        ratio_label_frame.pack(fill=tk.X)
        
        ttk.Label(ratio_label_frame, text="面部比例:").pack(side=tk.LEFT)
        
        # 数值显示和重置按钮容器
        ratio_value_container = ttk.Frame(ratio_label_frame)
        ratio_value_container.pack(side=tk.RIGHT)
        
        ratio_value_label = ttk.Label(ratio_value_container, textvariable=self.app.ratio_value)
        ratio_value_label.pack(side=tk.LEFT)
        
        # 面部比例重置按钮
        ratio_reset_label = ttk.Label(
            ratio_value_container,
            text="↺",
            cursor="hand2",
            foreground='#666666'
        )
        ratio_reset_label.pack(side=tk.LEFT, padx=(5, 0))
        ratio_reset_label.bind('<Button-1>', lambda e: self.reset_ratio())
        
        # 滑动条容器
        ratio_scale_frame = ttk.Frame(ratio_frame)
        ratio_scale_frame.pack(fill=tk.X)
        
        # 最小值标签
        ttk.Label(ratio_scale_frame, text="0.1").pack(side=tk.LEFT)
        
        # 滑动条
        ratio_scale = tk.Scale(
            ratio_scale_frame,
            from_=0.1,
            to=0.5,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.app.ratio_value,
            command=self.update_ratio,
            length=200,
            relief=tk.FLAT,
            sliderlength=20,
            troughcolor='#e0e0e0',
            activebackground='#1890ff',
            showvalue=False
        )
        ratio_scale.bind("<ButtonPress-1>", lambda e: self.app.params_manager.start_sliding())
        ratio_scale.bind("<ButtonRelease-1>", lambda e: self.app.params_manager.stop_sliding())
        ratio_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 最大值标签
        ttk.Label(ratio_scale_frame, text="0.5").pack(side=tk.RIGHT)
        
        # 头顶距离
        top_frame = ttk.Frame(basic_frame)
        top_frame.pack(fill=tk.X, pady=0)
        
        # 标签和数值显示容器
        top_label_frame = ttk.Frame(top_frame)
        top_label_frame.pack(fill=tk.X)
        
        ttk.Label(top_label_frame, text="头顶距离:").pack(side=tk.LEFT)
        
        # 数值显示和重置按钮容器
        top_value_container = ttk.Frame(top_label_frame)
        top_value_container.pack(side=tk.RIGHT)
        
        top_value_label = ttk.Label(top_value_container, textvariable=self.app.top_value)
        top_value_label.pack(side=tk.LEFT)
        
        # 头顶距离重置按钮
        top_reset_label = ttk.Label(
            top_value_container,
            text="↺",
            cursor="hand2",
            foreground='#666666'
        )
        top_reset_label.pack(side=tk.LEFT, padx=(5, 0))
        top_reset_label.bind('<Button-1>', lambda e: self.reset_top())
        
        # 滑动条容器
        top_scale_frame = ttk.Frame(top_frame)
        top_scale_frame.pack(fill=tk.X)
        
        # 最小值标签
        ttk.Label(top_scale_frame, text="0.05").pack(side=tk.LEFT)
        
        # 滑动条
        top_scale = tk.Scale(
            top_scale_frame,
            from_=0.05,
            to=0.3,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.app.top_value,
            command=self.update_top,
            length=200,
            relief=tk.FLAT,
            sliderlength=20,
            troughcolor='#e0e0e0',
            activebackground='#1890ff'
        )
        top_scale.bind("<ButtonPress-1>", lambda e: self.app.params_manager.start_sliding())
        top_scale.bind("<ButtonRelease-1>", lambda e: self.app.params_manager.stop_sliding())
        top_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 最大值标签
        ttk.Label(top_scale_frame, text="0.3").pack(side=tk.RIGHT)
        
        # 在基本参数后添加美颜参数
        beauty_frame = ttk.LabelFrame(matting_frame, text="美颜参数", padding=2)
        beauty_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 亮度调节
        brightness_frame = ttk.Frame(beauty_frame)
        brightness_frame.pack(fill=tk.X, pady=0)
        
        # 标签和数值显示容器
        brightness_label_frame = ttk.Frame(brightness_frame)
        brightness_label_frame.pack(fill=tk.X)
        
        ttk.Label(brightness_label_frame, text="亮度:").pack(side=tk.LEFT)
        
        # 数值显示和重置按钮容器
        brightness_value_container = ttk.Frame(brightness_label_frame)
        brightness_value_container.pack(side=tk.RIGHT)
        
        brightness_value = ttk.Label(brightness_value_container, textvariable=self.app.brightness_var)
        brightness_value.pack(side=tk.LEFT)
        
        # 亮度重置按钮
        brightness_reset_label = ttk.Label(
            brightness_value_container,
            text="↺",
            cursor="hand2",
            foreground='#666666'
        )
        brightness_reset_label.pack(side=tk.LEFT, padx=(5, 0))
        brightness_reset_label.bind('<Button-1>', lambda e: self.reset_beauty_param(self.app.brightness_var, 0))
        
        # 滑动条容器
        brightness_scale_frame = ttk.Frame(brightness_frame)
        brightness_scale_frame.pack(fill=tk.X)
        
        # 最小值标签
        ttk.Label(brightness_scale_frame, text="-5").pack(side=tk.LEFT)
        
        # 滑动条
        brightness_scale = tk.Scale(
            brightness_scale_frame,
            from_=-5,
            to=25,
            orient=tk.HORIZONTAL,
            variable=self.app.brightness_var,
            command=self.update_beauty,
            length=200,
            relief=tk.FLAT,
            sliderlength=20,
            troughcolor='#e0e0e0',
            activebackground='#1890ff',
            showvalue=False
        )
        brightness_scale.bind("<ButtonPress-1>", lambda e: self.app.params_manager.start_sliding())
        brightness_scale.bind("<ButtonRelease-1>", lambda e: self.app.params_manager.stop_sliding())
        brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 最大值标签
        ttk.Label(brightness_scale_frame, text="25").pack(side=tk.RIGHT)
        
        # 对比度调节（与亮度类似）
        contrast_frame = ttk.Frame(beauty_frame)
        contrast_frame.pack(fill=tk.X, pady=0)
        
        contrast_label_frame = ttk.Frame(contrast_frame)
        contrast_label_frame.pack(fill=tk.X)
        
        ttk.Label(contrast_label_frame, text="对比度:").pack(side=tk.LEFT)
        
        contrast_value_container = ttk.Frame(contrast_label_frame)
        contrast_value_container.pack(side=tk.RIGHT)
        
        contrast_value = ttk.Label(contrast_value_container, textvariable=self.app.contrast_var)
        contrast_value.pack(side=tk.LEFT)
        
        contrast_reset_label = ttk.Label(
            contrast_value_container,
            text="↺",
            cursor="hand2",
            foreground='#666666'
        )
        contrast_reset_label.pack(side=tk.LEFT, padx=(5, 0))
        contrast_reset_label.bind('<Button-1>', lambda e: self.reset_beauty_param(self.app.contrast_var, 0))
        
        contrast_scale_frame = ttk.Frame(contrast_frame)
        contrast_scale_frame.pack(fill=tk.X)
        
        ttk.Label(contrast_scale_frame, text="-10").pack(side=tk.LEFT)
        
        contrast_scale = tk.Scale(
            contrast_scale_frame,
            from_=-10,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.app.contrast_var,
            command=self.update_beauty,
            length=200,
            relief=tk.FLAT,
            sliderlength=20,
            troughcolor='#e0e0e0',
            activebackground='#1890ff',
            showvalue=False
        )
        contrast_scale.bind("<ButtonPress-1>", lambda e: self.app.params_manager.start_sliding())
        contrast_scale.bind("<ButtonRelease-1>", lambda e: self.app.params_manager.stop_sliding())
        contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(contrast_scale_frame, text="50").pack(side=tk.RIGHT)
        
        # 锐化调节（与亮度类似）
        sharpen_frame = ttk.Frame(beauty_frame)
        sharpen_frame.pack(fill=tk.X, pady=0)
        
        sharpen_label_frame = ttk.Frame(sharpen_frame)
        sharpen_label_frame.pack(fill=tk.X)
        
        ttk.Label(sharpen_label_frame, text="锐化:").pack(side=tk.LEFT)
        
        sharpen_value_container = ttk.Frame(sharpen_label_frame)
        sharpen_value_container.pack(side=tk.RIGHT)
        
        sharpen_value = ttk.Label(sharpen_value_container, textvariable=self.app.sharpen_var)
        sharpen_value.pack(side=tk.LEFT)
        
        sharpen_reset_label = ttk.Label(
            sharpen_value_container,
            text="↺",
            cursor="hand2",
            foreground='#666666'
        )
        sharpen_reset_label.pack(side=tk.LEFT, padx=(5, 0))
        sharpen_reset_label.bind('<Button-1>', lambda e: self.reset_beauty_param(self.app.sharpen_var, 0))
        
        sharpen_scale_frame = ttk.Frame(sharpen_frame)
        sharpen_scale_frame.pack(fill=tk.X)
        
        ttk.Label(sharpen_scale_frame, text="0").pack(side=tk.LEFT)
        
        sharpen_scale = tk.Scale(
            sharpen_scale_frame,
            from_=0,
            to=5,
            orient=tk.HORIZONTAL,
            variable=self.app.sharpen_var,
            command=self.update_beauty,
            length=200,
            relief=tk.FLAT,
            sliderlength=20,
            troughcolor='#e0e0e0',
            activebackground='#1890ff',
            showvalue=False
        )
        sharpen_scale.bind("<ButtonPress-1>", lambda e: self.app.params_manager.start_sliding())
        sharpen_scale.bind("<ButtonRelease-1>", lambda e: self.app.params_manager.stop_sliding())
        sharpen_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(sharpen_scale_frame, text="5").pack(side=tk.RIGHT)
        
        # 饱和度调节（与亮度类似）
        saturation_frame = ttk.Frame(beauty_frame)
        saturation_frame.pack(fill=tk.X, pady=0)
        
        saturation_label_frame = ttk.Frame(saturation_frame)
        saturation_label_frame.pack(fill=tk.X)
        
        ttk.Label(saturation_label_frame, text="饱和度:").pack(side=tk.LEFT)
        
        saturation_value_container = ttk.Frame(saturation_label_frame)
        saturation_value_container.pack(side=tk.RIGHT)
        
        saturation_value = ttk.Label(saturation_value_container, textvariable=self.app.saturation_var)
        saturation_value.pack(side=tk.LEFT)
        
        saturation_reset_label = ttk.Label(
            saturation_value_container,
            text="↺",
            cursor="hand2",
            foreground='#666666'
        )
        saturation_reset_label.pack(side=tk.LEFT, padx=(5, 0))
        saturation_reset_label.bind('<Button-1>', lambda e: self.reset_beauty_param(self.app.saturation_var, 0))
        
        saturation_scale_frame = ttk.Frame(saturation_frame)
        saturation_scale_frame.pack(fill=tk.X)
        
        ttk.Label(saturation_scale_frame, text="-10").pack(side=tk.LEFT)
        
        saturation_scale = tk.Scale(
            saturation_scale_frame,
            from_=-10,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.app.saturation_var,
            command=self.update_beauty,
            length=200,
            relief=tk.FLAT,
            sliderlength=20,
            troughcolor='#e0e0e0',
            activebackground='#1890ff',
            showvalue=False
        )
        saturation_scale.bind("<ButtonPress-1>", lambda e: self.app.params_manager.start_sliding())
        saturation_scale.bind("<ButtonRelease-1>", lambda e: self.app.params_manager.stop_sliding())
        saturation_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(saturation_scale_frame, text="50").pack(side=tk.RIGHT)
        
        # 其他选项
        options_frame = ttk.LabelFrame(matting_frame, text="其他选项", padding=2)
        options_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 人脸矫正选项
        ttk.Checkbutton(
            options_frame,
            text="人脸矫正",
            variable=self.app.align_var,
            command=lambda: self.update_beauty(None)
        ).pack(side=tk.LEFT, padx=5)
        
        # 高清照片选项
        ttk.Checkbutton(
            options_frame,
            text="高清照片",
            variable=self.app.hd_var,
            command=self.update_hd_preview
        ).pack(side=tk.LEFT, padx=5)
        
    def reset_ratio(self):
        """重置面部比例"""
        self.app.ratio_value.set("0.20")
        if hasattr(self.app, 'transparent_image'):
            self.app.image_processor.process_matting()
            
    def update_ratio(self, value):
        """更新面部比例"""
        self.app.ratio_value.set(f"{float(value):.2f}")
        if not self.app.params_manager.is_sliding:
            if hasattr(self.app, 'transparent_image'):
                self.app.image_processor.process_matting()
                
    def reset_top(self):
        """重置头顶距离"""
        self.app.top_value.set("0.12")
        if hasattr(self.app, 'transparent_image'):
            self.app.image_processor.process_matting()
            
    def update_top(self, value):
        """更新头顶距离"""
        self.app.top_value.set(f"{float(value):.2f}")
        if not self.app.params_manager.is_sliding:
            if hasattr(self.app, 'transparent_image'):
                self.app.image_processor.process_matting()
                
    def get_matting_model(self):
        """获取实际的抠图模型名称"""
        display_name = self.matting_model_var.get()
        return self.matting_model_map.get(display_name)
        
    def get_face_model(self):
        """获取实际的人脸检测模型名称"""
        display_name = self.face_model_var.get()
        return self.face_model_map.get(display_name)
        
    def update_beauty(self, value):
        """更新美颜效果"""
        if not self.app.params_manager.is_sliding:
            if hasattr(self.app, 'transparent_image'):
                self.app.image_processor.process_matting()
        
    def reset_beauty_param(self, var, default):
        """重置美颜参数"""
        var.set(default)
        self.update_beauty(None)
        
    def update_hd_preview(self):
        """更新高清预览"""
        if hasattr(self.app, 'transparent_image'):
            # 重新进行抠图处理
            self.app.image_processor.process_matting()