import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from editors.base_editor import BaseEditor

class CollapsibleFrame(ttk.Frame):
    """可折叠的Frame"""
    # 保存所有折叠菜单的引用
    frames = []
    
    def __init__(self, parent, text="", default_expanded=False, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        # 将自己添加到frames列表中
        CollapsibleFrame.frames.append(self)
        
        # 绑定销毁事件
        self.bind('<Destroy>', self.on_destroy)
        
        # 创建标题栏
        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill=tk.X)
        
        self.toggle_button = ttk.Label(
            self.title_frame, 
            text="▼ " + text if default_expanded else "▶ " + text,
            cursor="hand2"
        )
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.title_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 创建内容区域
        self.content_frame = ttk.Frame(self, padding=5)
        if default_expanded:
            self.content_frame.pack(fill=tk.X, expand=True)
        
        # 绑定点击事件
        self.toggle_button.bind('<Button-1>', self.toggle)
        self.is_expanded = default_expanded
        
    def on_destroy(self, event):
        """处理销毁事件"""
        # 从frames列表中移除自己
        if self in CollapsibleFrame.frames:
            CollapsibleFrame.frames.remove(self)
            
    def toggle(self, event=None):
        """切换折叠状态"""
        # 折叠其他所有菜单
        for frame in CollapsibleFrame.frames[:]:  # 使用列表副本进行迭代
            if frame != self and frame.is_expanded and frame.winfo_exists():  # 检查窗口是否还存在
                try:
                    frame.content_frame.pack_forget()
                    frame.toggle_button.configure(text="▶ " + frame.toggle_button.cget("text")[2:])
                    frame.is_expanded = False
                except tk.TclError:
                    # 如果窗口已经被销毁，从列表中移除
                    if frame in CollapsibleFrame.frames:
                        CollapsibleFrame.frames.remove(frame)
        
        # 切换当前菜单状态
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.toggle_button.configure(text="▶ " + self.toggle_button.cget("text")[2:])
        else:
            self.content_frame.pack(fill=tk.X, expand=True)
            self.toggle_button.configure(text="▼ " + self.toggle_button.cget("text")[2:])
            # 如果是色阶菜单，更新直方图
            if self.toggle_button.cget("text").endswith("色阶"):
                # 获取 BasicEditor 实例
                for widget in self.winfo_children():
                    if hasattr(widget, 'update_histogram'):
                        widget.update_histogram()
                        break
                
        self.is_expanded = not self.is_expanded

    @classmethod
    def clear_frames(cls):
        """清除所有折叠菜单引用"""
        cls.frames.clear()


class BasicEditor(BaseEditor):
    def setup_variables(self):
        """初始化变量"""
        self.brightness_var = tk.IntVar(value=0)  # 亮度
        self.contrast_var = tk.IntVar(value=0)    # 对比度
        self.saturation_var = tk.IntVar(value=0)  # 饱和度
        self.hue_var = tk.IntVar(value=0)         # 色相
        self.sharpness_var = tk.IntVar(value=0)   # 锐化
        
    def create_widgets(self, notebook):
        """创建编辑器控件"""
        basic_frame = ttk.Frame(notebook, padding=5)
        notebook.add(basic_frame, text="调整")
        
        # 创建基本参数折叠菜单 - 默认展开
        basic_params = CollapsibleFrame(basic_frame, "基本参数", default_expanded=True)
        basic_params.pack(fill=tk.X, pady=2)
        
        # 创建滑动条容器
        sliders_frame = ttk.Frame(basic_params.content_frame)
        sliders_frame.pack(fill=tk.X, expand=True)
        
        # 亮度调节 - 范围调整为-50到50,更适合日常调
        self.create_slider(
            sliders_frame, 
            "亮度:", 
            self.brightness_var,
            -50, 50,  # 修改范围
            self.on_param_change
        )
        
        # 对比度调节 - 范围调整为-30到50,避免过度调整
        self.create_slider(
            sliders_frame,
            "对比度:",
            self.contrast_var,
            -30, 50,  # 修改范围
            self.on_param_change
        )
        
        # 饱和度调节 - 范围调整为-50到50,更合理
        self.create_slider(
            sliders_frame,
            "饱和度:",
            self.saturation_var,
            -50, 50,  # 修改范围
            self.on_param_change
        )
        
        # 色相调节 - 范围调整为-30到30,避免颜色过度偏移
        self.create_slider(
            sliders_frame,
            "色相:",
            self.hue_var,
            -30, 30,  # 修改范围
            self.on_param_change
        )
        
        # 锐化调节 - 范围调整为0到30,避免过度锐化
        self.create_slider(
            sliders_frame,
            "锐化:",
            self.sharpness_var,
            0, 30,  # 修改范围
            self.on_param_change
        )
        
        # 添加重置按钮容器
        reset_frame = ttk.Frame(basic_params.content_frame)
        reset_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 添加重置按钮（右对齐）
        ttk.Button(
            reset_frame,
            text="重置所有参数",
            command=self.reset_basic_params,
            style='Small.TButton',
            width=12
        ).pack(side=tk.RIGHT)
        
        # 创建色阶折叠菜单 - 默认折叠
        levels_params = CollapsibleFrame(basic_frame, "色阶", default_expanded=False)
        levels_params.pack(fill=tk.X, pady=2)
        
        # 创建色阶直方图和控制点
        self.setup_levels_controls(levels_params.content_frame)

    def setup_levels_controls(self, parent):
        """设置色阶控制"""
        # 创建直方图画布
        histogram_frame = ttk.Frame(parent)
        histogram_frame.pack(fill=tk.X, pady=5)
        
        self.histogram_canvas = tk.Canvas(
            histogram_frame,
            width=256,
            height=100,
            bg='white',
            highlightthickness=1,
            highlightbackground='#CCCCCC'
        )
        self.histogram_canvas.pack(fill=tk.X, pady=5)
        
        # 添加控制滑块
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X)
        
        # 输入色阶
        input_frame = ttk.LabelFrame(controls_frame, text="输入色阶", padding=2)
        input_frame.pack(fill=tk.X, pady=2)
        
        # 黑场(阴影)
        self.input_black = tk.IntVar(value=0)
        black_frame = ttk.Frame(input_frame)
        black_frame.pack(fill=tk.X)
        ttk.Label(black_frame, text="阴影:").pack(side=tk.LEFT)
        ttk.Label(black_frame, textvariable=self.input_black, width=4).pack(side=tk.RIGHT)
        black_scale = ttk.Scale(
            input_frame,
            from_=0,
            to=255,
            variable=self.input_black,
            orient=tk.HORIZONTAL,
            command=lambda v: self.on_level_change(v, self.input_black)
        )
        black_scale.pack(fill=tk.X)
        
        # 灰度系数(中间调)
        self.input_gamma = tk.DoubleVar(value=1.0)
        gamma_frame = ttk.Frame(input_frame)
        gamma_frame.pack(fill=tk.X)
        ttk.Label(gamma_frame, text="中间调:").pack(side=tk.LEFT)
        ttk.Label(gamma_frame, textvariable=self.input_gamma, width=4).pack(side=tk.RIGHT)
        gamma_scale = ttk.Scale(
            input_frame,
            from_=0.1,
            to=10.0,
            variable=self.input_gamma,
            orient=tk.HORIZONTAL,
            command=lambda v: self.on_level_change(v, self.input_gamma, format=".2f")
        )
        gamma_scale.pack(fill=tk.X)
        
        # 白场(高光)
        self.input_white = tk.IntVar(value=255)
        white_frame = ttk.Frame(input_frame)
        white_frame.pack(fill=tk.X)
        ttk.Label(white_frame, text="高光:").pack(side=tk.LEFT)
        ttk.Label(white_frame, textvariable=self.input_white, width=4).pack(side=tk.RIGHT)
        white_scale = ttk.Scale(
            input_frame,
            from_=0,
            to=255,
            variable=self.input_white,
            orient=tk.HORIZONTAL,
            command=lambda v: self.on_level_change(v, self.input_white)
        )
        white_scale.pack(fill=tk.X)
        
        # 输出色阶
        output_frame = ttk.LabelFrame(controls_frame, text="输出色阶", padding=2)
        output_frame.pack(fill=tk.X, pady=2)
        
        # 输出黑场
        self.output_black = tk.IntVar(value=0)
        out_black_frame = ttk.Frame(output_frame)
        out_black_frame.pack(fill=tk.X)
        ttk.Label(out_black_frame, text="黑场:").pack(side=tk.LEFT)
        ttk.Label(out_black_frame, textvariable=self.output_black, width=4).pack(side=tk.RIGHT)
        out_black_scale = ttk.Scale(
            output_frame,
            from_=0,
            to=255,
            variable=self.output_black,
            orient=tk.HORIZONTAL,
            command=lambda v: self.on_level_change(v, self.output_black)
        )
        out_black_scale.pack(fill=tk.X)
        
        # 输出白场
        self.output_white = tk.IntVar(value=255)
        out_white_frame = ttk.Frame(output_frame)
        out_white_frame.pack(fill=tk.X)
        ttk.Label(out_white_frame, text="白场:").pack(side=tk.LEFT)
        ttk.Label(out_white_frame, textvariable=self.output_white, width=4).pack(side=tk.RIGHT)
        out_white_scale = ttk.Scale(
            output_frame,
            from_=0,
            to=255,
            variable=self.output_white,
            orient=tk.HORIZONTAL,
            command=lambda v: self.on_level_change(v, self.output_white)
        )
        out_white_scale.pack(fill=tk.X)
        
        # 添加重置按钮
        reset_frame = ttk.Frame(parent)
        reset_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Button(
            reset_frame,
            text="重置色阶",
            command=self.reset_levels,
            style='Small.TButton',
            width=12
        ).pack(side=tk.RIGHT)
        
        # 初始化直方图显示
        self.update_histogram()
        
        # 为每个滑动条添加滑动事件绑定
        for widget in input_frame.winfo_children():
            if isinstance(widget, ttk.Scale):
                widget.bind("<ButtonPress-1>", self.start_levels_sliding)
                widget.bind("<ButtonRelease-1>", self.stop_levels_sliding)
                widget.bind("<B1-Motion>", lambda e: self.on_levels_sliding())
                
        for widget in output_frame.winfo_children():
            if isinstance(widget, ttk.Scale):
                widget.bind("<ButtonPress-1>", self.start_levels_sliding)
                widget.bind("<ButtonRelease-1>", self.stop_levels_sliding)
                widget.bind("<B1-Motion>", lambda e: self.on_levels_sliding())

    def start_levels_sliding(self, event):
        """开始滑动色阶"""
        if not hasattr(self, 'original_image') and hasattr(self.parent, 'current_image'):
            self.original_image = self.parent.current_image.copy()
        self.is_sliding = True

    def stop_levels_sliding(self, event):
        """停止滑动色阶"""
        self.is_sliding = False
        self.update_levels()

    def on_levels_sliding(self):
        """色阶滑动中"""
        if self.is_sliding:
            self.update_levels_preview(quality='low')

    def reset_levels(self):
        """重置色阶参数"""
        # 检查是否有图像
        if not hasattr(self.parent, 'current_image'):
            return
            
        # 保存当前图像作��原始图像（如果还没有）
        if not hasattr(self, 'original_image'):
            self.original_image = self.parent.current_image.copy()
            
        try:
            # 重置所有色阶参数
            self.input_black.set(0)
            self.input_gamma.set(1.0)
            self.input_white.set(255)
            self.output_black.set(0)
            self.output_white.set(255)
            
            # 恢复原始图像
            if self.original_image is not None:
                self.parent.current_image = self.original_image.copy()
                self.parent.update_preview()
                
            # 更新直方图显示
            self.update_histogram()
            
        except Exception as e:
            print(f"重置色阶时出错: {str(e)}")

    def update_histogram(self):
        """更新直方图显示"""
        if not hasattr(self.parent, 'current_image'):
            return
            
        # 清除画布
        self.histogram_canvas.delete("all")
        
        # 计算RGB各通道直方图
        image = self.parent.current_image
        b, g, r = cv2.split(image)
        hist_b = cv2.calcHist([b], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([g], [0], None, [256], [0, 256])
        hist_r = cv2.calcHist([r], [0], None, [256], [0, 256])
        
        # 归一化直方图
        max_value = max(hist_b.max(), hist_g.max(), hist_r.max())
        if max_value > 0:  # 避免除以零
            hist_b = hist_b.flatten() / max_value * 90
            hist_g = hist_g.flatten() / max_value * 90
            hist_r = hist_r.flatten() / max_value * 90
            
            # 绘制背景网格
            for i in range(0, 256, 32):
                # 垂直线
                self.histogram_canvas.create_line(
                    i, 0, i, 100,
                    fill='#EEEEEE'
                )
                # 水平线
                self.histogram_canvas.create_line(
                    0, i, 256, i,
                    fill='#EEEEEE'
                )
            
            # 绘制RGB直方图
            for i in range(255):
                # 红色通道
                self.histogram_canvas.create_line(
                    i, 100 - hist_r[i],
                    i+1, 100 - hist_r[i+1],
                    fill='#FF0000',
                    width=1,
                    stipple='gray50'  # 使用点画线实现半透明效果
                )
                # 绿色通道
                self.histogram_canvas.create_line(
                    i, 100 - hist_g[i],
                    i+1, 100 - hist_g[i+1],
                    fill='#00FF00',
                    width=1,
                    stipple='gray50'
                )
                # 蓝色通道
                self.histogram_canvas.create_line(
                    i, 100 - hist_b[i],
                    i+1, 100 - hist_b[i+1],
                    fill='#0000FF',
                    width=1,
                    stipple='gray50'
                )
        
        # 绘制色阶控制点
        self.draw_level_controls()
        
        # 绘制边框
        self.histogram_canvas.create_rectangle(
            0, 0, 256, 100,
            outline='#CCCCCC'
        )

    def draw_level_controls(self):
        """绘制色阶控制点"""
        # 绘制输入色阶控制线
        input_black = self.input_black.get()
        input_white = self.input_white.get()
        input_gamma = self.input_gamma.get()
        
        # 绘制黑场和白场控制线
        self.histogram_canvas.create_line(
            input_black, 0, input_black, 100,
            fill='#666666', dash=(2,2)
        )
        self.histogram_canvas.create_line(
            input_white, 0, input_white, 100,
            fill='#666666', dash=(2,2)
        )
        
        # 绘制中间调曲线
        points = []
        for x in range(input_black, input_white+1):
            if x <= input_black:
                y = 100
            elif x >= input_white:
                y = 0
            else:
                # 计算gamma曲线
                normalized_x = (x - input_black) / (input_white - input_black)
                y = 100 - (normalized_x ** input_gamma) * 100
            points.extend([x, y])
            
        if len(points) >= 4:  # 至少需要两个点才能画线
            self.histogram_canvas.create_line(
                points,
                fill='#666666',
                smooth=True,
                width=1
            )

    def update_levels(self, *args):
        """更新色阶"""
        if not hasattr(self.parent, 'current_image'):
            return
            
        # 确保有原始图像
        if not hasattr(self, 'original_image') or self.original_image is None:
            self.original_image = self.parent.current_image.copy()
            
        if self.is_sliding:
            # 滑动时使用低质量预览
            self.update_levels_preview(quality='low')
        else:
            # 停止滑动时使用高质量预览
            self.update_levels_preview(quality='high')

    def update_levels_preview(self, quality='high'):
        """更新色阶预览"""
        # 检查是否有图像
        if not hasattr(self.parent, 'current_image'):
            return
            
        # 确保有原始图像
        if not hasattr(self, 'original_image') or self.original_image is None:
            self.original_image = self.parent.current_image.copy()
            
        # 获取基准图像
        image = self.original_image.copy()
        
        # 根据质量选择不同的处理方式
        if quality == 'low':
            # 低质量模式 - 缩小图像处理以提高性能
            scale = 0.5
            small_image = cv2.resize(image, None, fx=scale, fy=scale)
            processed = self.process_levels(small_image)
            image = cv2.resize(processed, (image.shape[1], image.shape[0]))
        else:
            # 高质量模式 - 直接处理原图
            image = self.process_levels(image)
        
        # 更新预览
        self.parent.current_image = image
        self.parent.update_preview()
        
        # 更新直方图显示
        if quality == 'high':
            self.update_histogram()

    def process_levels(self, image):
        """处理色阶"""
        # 获取参数
        input_black = self.input_black.get()
        input_white = self.input_white.get()
        gamma = self.input_gamma.get()
        output_black = self.output_black.get()
        output_white = self.output_white.get()
        
        # 检查是否需要处理
        if (input_black == 0 and input_white == 255 and 
            gamma == 1.0 and output_black == 0 and 
            output_white == 255):
            return image
            
        # 创建查找表
        lookup_table = np.zeros((256,), dtype=np.uint8)
        for i in range(256):
            # 输入映射
            if i <= input_black:
                value = 0
            elif i >= input_white:
                value = 255
            else:
                # 使用更精确的伽马校正
                normalized = (i - input_black) / (input_white - input_black)
                value = np.power(normalized, gamma) * 255
            
            # 输出映射
            value = output_black + (value / 255.0) * (output_white - output_black)
            lookup_table[i] = np.clip(value, 0, 255)
        
        # 分别处理RGB通道
        b, g, r = cv2.split(image)
        b = cv2.LUT(b, lookup_table)
        g = cv2.LUT(g, lookup_table)
        r = cv2.LUT(r, lookup_table)
        
        return cv2.merge([b, g, r])

    def on_param_change(self, *args):
        """参数改变时的处理"""
        if self.is_sliding:
            # 滑动时使用低质量预览以提高性能
            self.update_preview(quality='low')
            return
            
        # 停止滑动后使用高质��预览
        self.update_preview(quality='high')

    def update_preview(self, quality='high'):
        """更新预览图像"""
        # 如果所有参数都为0，使用原始图像
        if (self.brightness_var.get() == 0 and 
            self.contrast_var.get() == 0 and
            self.saturation_var.get() == 0 and
            self.hue_var.get() == 0 and
            self.sharpness_var.get() == 0):
            if self.original_image is not None:
                self.parent.current_image = self.original_image.copy()
                self.parent.update_preview()
                return
                
        # 获取基准图像
        image = self.original_image.copy() if self.original_image is not None else self.parent.current_image.copy()
        
        # 根据质量选择不同的处理方式
        if quality == 'low':
            # 低质量模式 - 缩小图像处理以提高性能
            scale = 0.5
            small_image = cv2.resize(image, None, fx=scale, fy=scale)
            processed = self.process_image(small_image)
            image = cv2.resize(processed, (image.shape[1], image.shape[0]))
        else:
            # 高质量模式 - 直接处理原图
            image = self.process_image(image)
            
        # 更新预览
        self.parent.current_image = image
        self.parent.update_preview()

    def process_image(self, image):
        """处理图像"""
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        
        # 应用色相调整 - 添加平滑过渡
        if self.hue_var.get() != 0:
            hue_shift = self.hue_var.get() * 0.5  # 平滑系数
            h = np.mod(h + hue_shift, 180)
        
        # 应用饱和度 - 使用指数函数实现更自然的调整
        if self.saturation_var.get() != 0:
            factor = np.exp(self.saturation_var.get() / 50.0) - 1
            s = np.clip(s * (1 + factor), 0, 255)
        
        # 合并HSV通道
        hsv = cv2.merge([h, s, v])
        image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 应用亮度和对比度 - 使用S形曲线实现更自然的调整
        if self.brightness_var.get() != 0 or self.contrast_var.get() != 0:
            # 亮度调整
            beta = self.brightness_var.get() * 2.55
            # 对比度调整使用S形曲线
            alpha = np.tan((self.contrast_var.get() + 45) * np.pi / 180)
            image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        
        # 应用锐化 - 使用USM锐化算法
        if self.sharpness_var.get() > 0:
            blur = cv2.GaussianBlur(image, (0, 0), 3)
            image = cv2.addWeighted(
                image, 
                1.0 + self.sharpness_var.get()/30.0,
                blur,
                -self.sharpness_var.get()/30.0,
                0
            )
        
        return image

    def reset(self):
        """重置参数"""
        self.brightness_var.set(0)
        self.contrast_var.set(0)
        self.saturation_var.set(0)
        self.hue_var.set(0)
        self.sharpness_var.set(0)

    def reset_basic_params(self):
        """重置基本参数"""
        # 重置所有滑动条值
        self.brightness_var.set(0)
        self.contrast_var.set(0)
        self.saturation_var.set(0)
        self.hue_var.set(0)
        self.sharpness_var.set(0)
        
        # 更新预览
        if self.original_image is not None:
            self.parent.current_image = self.original_image.copy()
            self.parent.update_preview()

    def on_level_change(self, value, var, format=None):
        """处理色阶值变化"""
        try:
            # 转换值为适当的格式
            if format:
                var.set(f"{float(value):{format}}")
            else:
                var.set(int(float(value)))
                
            # 更新色阶
            if not self.is_sliding:
                self.update_levels()
                
        except ValueError:
            pass