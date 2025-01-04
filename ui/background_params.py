import tkinter as tk
from tkinter import ttk

class BackgroundParams:
    def __init__(self, app, parent_notebook):
        self.app = app
        self.last_update_time = 0
        self.update_delay = 0.3
        self.is_sliding = False
        
        # 使用标准RGB格式定义颜色
        self.colors = {
            "红色": "#FF0000",    # RGB: (255, 0, 0)
            "蓝色": "#438EDB",    # RGB: (0, 0, 255)
            "白色": "#FFFFFF",    # RGB: (255, 255, 255)
            "深蓝": "#00047B",    # RGB: (0, 4, 123)
            "浅灰": "#F0F0F0",    # RGB: (240, 240, 240)
            "自定义": None        # 自定义颜色，初始为None
        }
        
        # 预设颜色列表
        self.preset_colors = list(self.colors.keys())
        
        self.setup_background_params(parent_notebook)
        
    def rgb_to_bgr(self, hex_color):
        """将RGB的HEX颜色转换为BGR的HEX颜色"""
        if not hex_color:
            return None
        hex_color = hex_color.lstrip('#')
        r = hex_color[0:2]
        g = hex_color[2:4]
        b = hex_color[4:6]
        return f"#{b}{g}{r}"

    def get_preview_color(self, color_name):
        """获取用于预览的RGB颜色"""
        return self.colors[color_name]

    def get_bgr_color(self, color_name):
        """获取用于OpenCV处理的BGR颜色"""
        rgb_color = self.colors[color_name]
        return self.rgb_to_bgr(rgb_color)

    def setup_background_params(self, parent_notebook):
        """设置换背景参数标签页"""
        background_frame = ttk.Frame(parent_notebook, padding=10)
        parent_notebook.add(background_frame, text="换背景参数")
        
        # 渲染模式选择（水平排列）
        render_frame = ttk.LabelFrame(background_frame, text="渲染模式", padding=2)
        render_frame.pack(fill=tk.X, pady=(0, 10))
        
        mode_container = ttk.Frame(render_frame)
        mode_container.pack(fill=tk.X, pady=2)
        
        render_modes = [
            ("纯色", 0),
            ("上下渐变", 1),
            ("中心渐变", 2)
        ]
        
        self.render_var = tk.IntVar(value=0)
        for text, value in render_modes:
            ttk.Radiobutton(
                mode_container,
                text=text,
                value=value,
                variable=self.render_var,
                command=self.on_render_mode_change
            ).pack(side=tk.LEFT, padx=10)
        
        # 渐变设置框架
        self.gradient_frame = ttk.LabelFrame(background_frame, text="渐变设置", padding=2)
        
        # 渐变颜色选择容器
        color_frame = ttk.Frame(self.gradient_frame)
        color_frame.pack(fill=tk.X, pady=2)
        
        # 起始颜色和结束颜色容器
        start_color_frame = ttk.LabelFrame(color_frame, text="起始颜色", padding=2)
        start_color_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 起始颜色选择网格
        start_grid = ttk.Frame(start_color_frame)
        start_grid.pack(fill=tk.X, pady=2)
        
        self.start_color_var = tk.StringVar(value="蓝色")
        row = 0
        col = 0
        for color_name in self.preset_colors:
            if color_name != "自定义":
                container = ttk.Frame(start_grid)
                container.grid(row=row, column=col, padx=5, pady=2)
                
                radio = ttk.Radiobutton(
                    container,
                    text=color_name,
                    value=color_name,
                    variable=self.start_color_var,
                    command=self.on_gradient_change
                )
                radio.pack(side=tk.LEFT)
                
                # 颜色预览
                preview = tk.Label(
                    container,
                    text=" ",
                    background=self.get_preview_color(color_name),  # 直接使用RGB
                    relief="solid",
                    borderwidth=1,
                    width=2
                )
                preview.pack(side=tk.LEFT, padx=(5, 0))
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
        
        # 结束颜色选择
        end_color_frame = ttk.LabelFrame(color_frame, text="结束颜色", padding=2)
        end_color_frame.pack(fill=tk.X)
        
        # 结束颜色选择网格
        end_grid = ttk.Frame(end_color_frame)
        end_grid.pack(fill=tk.X, pady=2)
        
        self.end_color_var = tk.StringVar(value="白色")
        row = 0
        col = 0
        for color_name in self.preset_colors:
            if color_name != "自定义":
                container = ttk.Frame(end_grid)
                container.grid(row=row, column=col, padx=5, pady=2)
                
                radio = ttk.Radiobutton(
                    container,
                    text=color_name,
                    value=color_name,
                    variable=self.end_color_var,
                    command=self.on_gradient_change
                )
                radio.pack(side=tk.LEFT)
                
                # 颜色预览
                preview = tk.Label(
                    container,
                    text=" ",
                    background=self.get_preview_color(color_name),  # 直接使用RGB
                    relief="solid",
                    borderwidth=1,
                    width=2
                )
                preview.pack(side=tk.LEFT, padx=(5, 0))
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
        
        # 渐变强度滑动条
        strength_frame = ttk.Frame(self.gradient_frame)
        strength_frame.pack(fill=tk.X, pady=0)
        
        # 标签和数值显示容器
        strength_label_frame = ttk.Frame(strength_frame)
        strength_label_frame.pack(fill=tk.X)
        
        ttk.Label(strength_label_frame, text="渐变强度:").pack(side=tk.LEFT)
        
        # 数值显示和重置按钮容器
        strength_value_container = ttk.Frame(strength_label_frame)
        strength_value_container.pack(side=tk.RIGHT)
        
        self.gradient_strength_var = tk.IntVar(value=100)
        strength_value_label = ttk.Label(strength_value_container, textvariable=self.gradient_strength_var)
        strength_value_label.pack(side=tk.LEFT)
        
        # 渐变强度重置按钮
        strength_reset_label = ttk.Label(
            strength_value_container,
            text="↺",
            cursor="hand2",
            foreground='#666666'
        )
        strength_reset_label.pack(side=tk.LEFT, padx=(5, 0))
        strength_reset_label.bind('<Button-1>', lambda e: self.reset_gradient_strength())
        
        # 滑动条容器
        strength_scale_frame = ttk.Frame(strength_frame)
        strength_scale_frame.pack(fill=tk.X)
        
        # 最小值标签
        ttk.Label(strength_scale_frame, text="-100").pack(side=tk.LEFT)
        
        # 滑动条
        strength_scale = tk.Scale(
            strength_scale_frame,
            from_=-100,
            to=100,
            resolution=1,
            orient=tk.HORIZONTAL,
            variable=self.gradient_strength_var,
            command=self.update_gradient,
            length=200,
            relief=tk.FLAT,
            sliderlength=20,
            troughcolor='#e0e0e0',
            activebackground='#1890ff',
            showvalue=False
        )
        strength_scale.bind("<ButtonPress-1>", lambda e: self.start_sliding())
        strength_scale.bind("<ButtonRelease-1>", lambda e: self.stop_sliding())
        strength_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 最大值标签
        ttk.Label(strength_scale_frame, text="100").pack(side=tk.RIGHT)
        
        # 背景色选择
        self.color_frame = ttk.LabelFrame(background_frame, text="背景颜色", padding=2)
        self.color_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 使用单选按钮组
        self.background_color_var = tk.StringVar(value="红色")
        
        # 背景色选择按钮网格
        color_grid = ttk.Frame(self.color_frame)
        color_grid.pack(fill=tk.X, pady=5)
        
        row = 0
        col = 0
        for color_name in self.preset_colors:
            if color_name != "自定义":
                container = ttk.Frame(color_grid)
                container.grid(row=row, column=col, padx=5, pady=2)
                
                radio = ttk.Radiobutton(
                    container,
                    text=color_name,
                    value=color_name,
                    variable=self.background_color_var,
                    command=self.on_color_change
                )
                radio.pack(side=tk.LEFT)
                
                # 颜色预览（使用RGB格式）
                preview = tk.Label(
                    container,
                    text=" ",
                    background=self.get_preview_color(color_name),  # 直接使用RGB
                    relief="solid",
                    borderwidth=1,
                    width=2
                )
                preview.pack(side=tk.LEFT, padx=(5, 0))
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
        
        # 自定义颜色按钮
        custom_container = ttk.Frame(color_grid)
        custom_container.grid(row=row, column=col, padx=5, pady=2)
        
        custom_radio = ttk.Radiobutton(
            custom_container,
            text="自定义",
            value="自定义",
            variable=self.background_color_var,
            command=self.on_custom_color
        )
        custom_radio.pack(side=tk.LEFT)
        
        self.custom_color_preview = tk.Label(
            custom_container,
            text=" ",
            background=self.colors.get("自定义", "#FFFFFF"),
            relief="solid",
            borderwidth=1,
            width=2
        )
        self.custom_color_preview.pack(side=tk.LEFT, padx=(5, 0))
        
        # 初始隐藏渐变设置
        self.gradient_frame.pack_forget()
        
    def on_render_mode_change(self):
        """渲染模式改变时的处理"""
        if self.render_var.get() in [1, 2]:  # 渐变模式
            self.gradient_frame.pack(fill=tk.X, pady=(0, 2))
            self.color_frame.pack_forget()
        else:  # 纯色模式
            self.gradient_frame.pack_forget()
            self.color_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 更新背景
        if hasattr(self.app, 'transparent_image'):
            self.app.image_processor.process_background()
            
    def reset_gradient_strength(self):
        """重置渐变强度"""
        self.gradient_strength_var.set(100)
        if hasattr(self.app, 'transparent_image'):
            self.app.image_processor.process_background()
            # 确保保持在换背景参数标签页
            self.app.params_notebook.select(1)
        
    def update_gradient(self, value):
        """更新渐变效果"""
        if not self.is_sliding:  # 使用自己的滑动状态
            if hasattr(self.app, 'transparent_image'):
                self.app.image_processor.process_background()
                # 确保保持在换背景参数标签页
                self.app.params_notebook.select(1)
        
    def on_custom_color(self):
        """处理自定义颜色选择"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="选择自定义颜色")
        if color[1]:  # 如果用户选择了颜色
            self.colors["自定义"] = color[1]  # 保存RGB格式
            self.custom_color_preview.configure(background=color[1])  # 使用RGB格式显示
            self.on_color_change()
        
    def on_color_change(self):
        """颜色改变时更新背景"""
        if hasattr(self.app, 'processed_image'):
            self.app.image_processor.process_background()
        
    def on_gradient_change(self):
        """渐变颜色改变时更新背景"""
        if hasattr(self.app, 'transparent_image'):
            self.app.image_processor.process_background()

    def start_sliding(self):
        """开始滑动"""
        self.is_sliding = True
        
    def stop_sliding(self):
        """停止滑动"""
        self.is_sliding = False
        if hasattr(self.app, 'transparent_image'):
            self.app.image_processor.process_background()
            # 确保保持在换背景参数标签页
            self.app.params_notebook.select(1)