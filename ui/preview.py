import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import tkinter.messagebox as messagebox
import time

class PreviewManager:
    def __init__(self, app):
        self.app = app
        if not hasattr(self.app, 'image_processor'):
            raise AttributeError("IDPhotoProcessor must have image_processor before creating PreviewManager")
        
        # 移除固定尺寸限制，改为最小尺寸
        self.preview_style = {
            'min_width': 400,
            'min_height': 360,
            'padding': 10
        }
        
        # 添加更新锁和状态标记
        self.is_updating = False
        self.resize_timer = None
        self.last_frame_sizes = None
        self.is_maximized = False
        self.update_pending = False
        self.last_update_time = 0
        self.normalize_timer = None
        self.last_window_state = None
        
        # 添加双缓冲变量
        self.buffer_images = {}
        self.current_size = None
        
        # 绑定窗口大小变化事件到主窗口
        self.app.window.bind('<Configure>', self.on_window_resize)
        self.last_width = self.app.window.winfo_width()
        self.last_height = self.app.window.winfo_height()
        
        self.setup_preview_areas()
        
    def on_window_resize(self, event):
        """处理窗口大小变化"""
        # 避免处理非主窗口的大小变化
        if event.widget != self.app.window:
            return
            
        # 获取当前窗口状态
        current_state = str(self.app.window.state())
        
        # 检测窗口状态变化
        if current_state != self.last_window_state:
            self.last_window_state = current_state
            # 如果是从最大化恢复，等待窗口完全恢复后再更新
            if current_state == 'normal' and self.is_maximized:
                self.is_maximized = False
                if self.normalize_timer:
                    self.app.window.after_cancel(self.normalize_timer)
                self.normalize_timer = self.app.window.after(300, self.handle_normalize)
                return
            elif current_state == 'zoomed':
                self.is_maximized = True
                if self.resize_timer:
                    self.app.window.after_cancel(self.resize_timer)
                self.resize_timer = self.app.window.after(300, self.delayed_update)
                return
        
        # 对于普通的大小调整，使用节流处理
        current_time = time.time()
        if current_time - self.last_update_time < 0.1:  # 100ms内不重复处理
            if self.resize_timer:
                self.app.window.after_cancel(self.resize_timer)
            self.resize_timer = self.app.window.after(100, self.delayed_update)
            return
            
        self.last_update_time = current_time
        self.last_width = event.width
        self.last_height = event.height
        
        # 仅更新框架大小，不更新内容
        self.update_frame_sizes()

    def delayed_update(self):
        """延迟执行更新"""
        if self.is_updating:
            self.update_pending = True
            return
            
        try:
            self.is_updating = True
            self.update_pending = False
            
            # 更新所有预览
            self.update_all_previews()
            
        finally:
            self.is_updating = False
            self.resize_timer = None
            
            # 如果在更新过程中又收到了更新请求，延迟处理
            if self.update_pending:
                self.app.window.after(100, self.delayed_update)

    def handle_normalize(self):
        """处理窗口标准化"""
        self.normalize_timer = None
        
        # 获取当前预览区域的大小
        container_width = self.app.left_frame.winfo_width()
        container_height = self.app.left_frame.winfo_height()
        
        # 计算标准化后的尺寸
        frame_width = (container_width - 20) // 2
        frame_height = (container_height - 20) // 2
        
        # 确保最小尺寸
        frame_width = max(frame_width, self.preview_style['min_width'])
        frame_height = max(frame_height, self.preview_style['min_height'])
        
        # 更新框架大小
        for frame in [self.upload_frame, self.transparent_frame, self.colored_frame, self.layout_frame]:
            frame.configure(width=frame_width, height=frame_height)
            frame.grid_propagate(False)  # 确保框架大小不会自动调整
            
        # 更新最后的尺寸记录
        self.last_frame_sizes = (frame_width, frame_height)
        
        # 只有在有图片时才更新预览
        has_images = (
            hasattr(self.app, 'current_image') or
            hasattr(self.app, 'transparent_image') or
            (hasattr(self.app, 'processed_images') and any(img is not None for img in self.app.processed_images)) or
            hasattr(self.app, 'layout_image')
        )
        
        if has_images:
            # 使用固定尺寸更新所有预览
            self.update_all_previews()

    def update_all_previews_with_size(self, width, height):
        """使用指定尺寸更新所有预览图片"""
        if self.is_updating:
            return
            
        try:
            self.is_updating = True
            # 清除旧的缓存
            self.clear_buffer()
            
            # 更新所有预览，传入固定尺寸
            if hasattr(self.app, 'current_image'):
                self._resize_and_display(self.upload_label, self.app.current_image, width, height)
                
            if hasattr(self.app, 'transparent_image'):
                self._resize_and_display(self.transparent_label, self.app.transparent_image, width, height)
                
            if hasattr(self.app, 'processed_images'):
                valid_photos = [i for i, img in enumerate(self.app.processed_images) if img is not None]
                if len(valid_photos) > 1:
                    # 多张照片时的特殊处理
                    padding_between = 2
                    total_padding = padding_between * (len(valid_photos) - 1)
                    max_width = (width - total_padding) // len(valid_photos)
                    target_height = height * 0.95
                    
                    for idx in valid_photos:
                        self._resize_and_display(
                            self.colored_labels[idx],
                            self.app.processed_images[idx],
                            max_width,
                            target_height
                        )
                else:
                    # 单张照片时的处理
                    for idx in valid_photos:
                        self._resize_and_display(
                            self.colored_labels[idx],
                            self.app.processed_images[idx],
                            width,
                            height
                        )
                    
            if hasattr(self.app, 'layout_image'):
                self._resize_and_display(self.layout_label, self.app.layout_image, width, height)
                
        finally:
            self.is_updating = False
            self.resize_timer = None

    def update_frame_sizes(self):
        """只更新框架大小，不更新预览内容"""
        # 计算新的预览区域大小
        container_width = self.app.left_frame.winfo_width()
        container_height = self.app.left_frame.winfo_height()
        frame_width = (container_width - 20) // 2  # 减去间距后平分宽度
        frame_height = (container_height - 20) // 2  # 减去间距后平分高度
        
        # 确保最小尺寸
        frame_width = max(frame_width, self.preview_style['min_width'])
        frame_height = max(frame_height, self.preview_style['min_height'])
        
        # 检查框架尺寸是否真的需要更新
        current_sizes = (frame_width, frame_height)
        if self.last_frame_sizes == current_sizes:
            return
            
        # 更新框架大小
        for frame in [self.upload_frame, self.transparent_frame, self.colored_frame, self.layout_frame]:
            frame.configure(width=frame_width, height=frame_height)
            frame.grid_propagate(False)  # 确保框架大小不会自动调整
            
        self.last_frame_sizes = current_sizes
        
        # 只有在有图片时才更新预览
        has_images = (
            hasattr(self.app, 'current_image') or
            hasattr(self.app, 'transparent_image') or
            (hasattr(self.app, 'processed_images') and any(img is not None for img in self.app.processed_images)) or
            hasattr(self.app, 'layout_image')
        )
        
        if has_images:
            self.update_all_previews()

    def update_all_previews(self):
        """更新所有预览图片"""
        if self.is_updating:
            return
            
        try:
            self.is_updating = True
            # 清除旧的缓存
            self.clear_buffer()
            
            # 更新所有预览
            if hasattr(self.app, 'current_image'):
                self.update_preview(self.upload_label, self.app.current_image)
                
            if hasattr(self.app, 'transparent_image'):
                self.update_preview(self.transparent_label, self.app.transparent_image)
                
            if hasattr(self.app, 'processed_images'):
                valid_photos = [i for i, img in enumerate(self.app.processed_images) if img is not None]
                for idx in valid_photos:
                    self.update_preview(self.colored_labels[idx], self.app.processed_images[idx])
                    
            if hasattr(self.app, 'layout_image'):
                self.update_preview(self.layout_label, self.app.layout_image)
                
        finally:
            self.is_updating = False
            self.resize_timer = None
            
            # 如果在更新过程中又收到了更新请求，再次更新
            if self.update_pending:
                self.app.window.after(50, self.delayed_update)

    def setup_preview_areas(self):
        """设置预览区域"""
        # 创建左侧预览区容器
        preview_container = ttk.Frame(self.app.left_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 配置grid布局，使用权重确保每个区域大小相等
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_rowconfigure(1, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_columnconfigure(1, weight=1)
        
        # 使用grid布局替代pack布局
        self.setup_frames(preview_container)
        
        # 设置按钮和预览
        self.setup_buttons_and_preview()
        
    def setup_frames(self, preview_container):
        """创建所有框架"""
        # 上传区域框架 - 左上
        self.upload_frame = ttk.LabelFrame(preview_container, text="上传照片", padding=10)
        self.upload_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=(0, 5))
        self.upload_frame.grid_propagate(False)  # 禁止自动调整大小
        
        # 透明照片框架 - 右上
        self.transparent_frame = ttk.LabelFrame(preview_container, text="透明照片", padding=10)
        self.transparent_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=(0, 5))
        self.transparent_frame.grid_propagate(False)  # 禁止自动调整大小
        
        # 背景色照片框架 - 左下
        self.colored_frame = ttk.LabelFrame(preview_container, text="背景色照片", padding=10)
        self.colored_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=(5, 0))
        self.colored_frame.grid_propagate(False)  # 禁止自动调整大小
        
        # 排版照片框架 - 右下
        self.layout_frame = ttk.LabelFrame(preview_container, text="排版照片", padding=10)
        self.layout_frame.grid(row=1, column=1, sticky='nsew', padx=(5, 0), pady=(5, 0))
        self.layout_frame.grid_propagate(False)  # 禁止自动调整大小
        
        # 设置每个框架的最小大小
        for frame in [self.upload_frame, self.transparent_frame, self.colored_frame, self.layout_frame]:
            frame.configure(width=self.preview_style['min_width'], height=self.preview_style['min_height'])

    def setup_buttons_and_preview(self):
        """设置按钮和预览"""
        # 上传区域
        self.setup_upload_area()
        
        # 透明照片预览区
        self.setup_transparent_preview()
        
        # 背景色照片预览区
        self.setup_colored_preview()
        
        # 排版照片预览区
        self.setup_layout_preview()

    def setup_upload_area(self):
        """设置上传区域"""
        # 上传预览区容器
        self.upload_preview_frame = ttk.Frame(self.upload_frame)
        self.upload_preview_frame.pack(fill=tk.BOTH, expand=True)
        self.upload_preview_frame.pack_propagate(False)  # 禁止自动调整大小
        
        # 创建预览标签
        self.upload_label = ttk.Label(self.upload_preview_frame)
        self.upload_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # 添加工具按钮
        self.setup_preview_buttons(self.upload_frame, is_upload=True)
        
        # 初始化上传预览
        self.setup_upload_preview()

    def setup_transparent_preview(self):
        """设置透明照片预览区"""
        # 创建预览容器
        preview_container = ttk.Frame(self.transparent_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        preview_container.pack_propagate(False)  # 禁止自动调整大小
        
        # 创建预览标签
        self.transparent_label = ttk.Label(preview_container, style='Transparent.TLabel')
        self.transparent_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # 创建抠图按钮容器
        self.matting_btn_container = ttk.Frame(self.transparent_frame)
        self.setup_matting_button()
        
        # 添加工具按钮
        self.setup_preview_buttons(self.transparent_frame)

    def setup_colored_preview(self):
        """设置背景色照片预览区"""
        # 创建预览容器
        self.colored_container = ttk.Frame(self.colored_frame)
        self.colored_container.pack(fill=tk.BOTH, expand=True)
        self.colored_container.pack_propagate(False)  # 禁止自动调整大小
        
        # 创建用于居中显示照片的容器
        self.photos_center_container = ttk.Frame(self.colored_container)
        self.photos_center_container.pack(expand=True)
        
        # 创建多个预览标签
        self.colored_labels = []
        self.preview_frames = []  # 存储每个预览框架
        
        for i in range(3):  # 最多3张照片
            preview_frame = ttk.Frame(self.photos_center_container)
            preview_frame.pack_propagate(False)  # 禁止自动调整大小
            self.preview_frames.append(preview_frame)
            
            label = ttk.Label(preview_frame)
            label.pack(expand=True, fill=tk.BOTH)
            self.colored_labels.append(label)
            # 添加点击事件
            label.bind('<Button-1>', lambda e, idx=i: self.select_photo(idx))
        
        # 创建换背景按钮容器
        self.background_btn_container = ttk.Frame(self.colored_frame)
        self.background_btn_container.pack()  # 先pack，后place
        
        # 创建换背景按钮
        ttk.Button(
            self.background_btn_container,
            text="换背景",
            command=self.app.image_processor.process_background,
            style='Upload.TButton'
        ).pack()
        
        # 如果已经有照片（检查第2、3个位置），隐藏按钮
        if hasattr(self.app, 'processed_images') and any(img is not None for i, img in enumerate(self.app.processed_images) if i > 0):
            self.background_btn_container.place_forget()
        else:
            self.background_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 添加工具按钮
        self.setup_preview_buttons(self.colored_frame)
        
        # 初始化选中状态（默认选中第一个有照片的位置）
        if hasattr(self.app, 'processed_images'):
            for i in range(1, 3):  # 从第2个位置开始查找
                if self.app.processed_images[i] is not None:
                    self.selected_label_index = i
                    break
            else:
                self.selected_label_index = 0  # 如果没有找到，选中第一个位置

    def setup_layout_preview(self):
        """设置排版照片预览区"""
        # 创建预览容器
        preview_container = ttk.Frame(self.layout_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        preview_container.pack_propagate(False)  # 禁止自动调整大小
        
        # 创建预览标签
        self.layout_label = ttk.Label(preview_container)
        self.layout_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # 创建排版按钮容器
        self.layout_btn_container = ttk.Frame(self.layout_frame)
        self.setup_layout_button()
        
        # 添加工具按钮
        self.setup_preview_buttons(self.layout_frame)

    def update_preview(self, label, image):
        """更新预览图片"""
        if image is None:
            label.configure(image='')
            if label in self.colored_labels:
                idx = self.colored_labels.index(label)
                self.preview_frames[idx].pack_forget()
            return
            
        # 如果是背景色照片区域，使用特殊处理
        if label in self.colored_labels:
            # 获取所有非空照片的索引
            valid_photos = [i for i, l in enumerate(self.colored_labels) 
                          if hasattr(self.app, 'processed_images') and 
                          self.app.processed_images[i] is not None]
            photo_count = len(valid_photos)
            
            # 重新排列所有预览框架
            for frame in self.preview_frames:
                frame.pack_forget()
            
            if photo_count > 0:
                # 确保居中容器可见
                self.photos_center_container.pack(expand=True)
                
                # 获取容器尺寸
                container_width = self.colored_container.winfo_width()
                container_height = self.colored_container.winfo_height()
                
                # 减小照片间距
                padding = 2  # 每张照片之间只留2像素的间距
                total_padding = padding * (photo_count - 1)
                
                # 计算每个照片的最大可用宽度
                available_width = (container_width - total_padding) / photo_count
                
                # 获取所有照片的原始宽高比
                aspect_ratios = []
                for idx in valid_photos:
                    img = self.app.processed_images[idx]
                    if isinstance(img, np.ndarray):
                        h, w = img.shape[:2]
                    else:  # PIL Image
                        w, h = img.size
                    aspect_ratios.append(w / h)
                
                # 计算适合所有照片的统一高度
                target_height = int(container_height * 0.95)  # 使用95%的容器高度
                
                # 计算每张照片基于高度的宽度
                photo_widths = [int(target_height * ratio) for ratio in aspect_ratios]
                total_width = sum(photo_widths) + total_padding
                
                # 如果总宽度超过容器宽度，需要按比例缩小
                if total_width > container_width:
                    scale = container_width / total_width
                    target_height = int(target_height * scale)
                    photo_widths = [int(w * scale) for w in photo_widths]
                
                # 重新显示有照片的框架
                for i, idx in enumerate(valid_photos):
                    frame_width = photo_widths[i]
                    frame_height = target_height
                    
                    # 配置并显示框架
                    self.preview_frames[idx].configure(width=frame_width, height=frame_height)
                    # 将所有照片添加到居中容器中
                    self.preview_frames[idx].pack(side=tk.LEFT, padx=padding//2)
                    
                    # 调整照片大小并显示
                    self._resize_and_display(
                        self.colored_labels[idx],
                        self.app.processed_images[idx],
                        frame_width,
                        frame_height
                    )
                
                # 如果包含第一个位置的照片（换背景生成的照片），自动选中它
                if 0 in valid_photos:
                    self.select_photo(0)
            return
        
        # 单张照片的处理
        self._resize_and_display(label, image)
        
        # 如果是背景色照片预览区，处理按钮显示
        if label in self.colored_labels:
            if hasattr(self, 'background_btn_container'):
                self.background_btn_container.place_forget()
            # 如果是第一个位置的照片（换背景生成的照片），自动选中它
            if label == self.colored_labels[0]:
                self.select_photo(0)
            # 更新排版预览
            if hasattr(self.app.params_manager, 'layout_params'):
                self.app.window.after_idle(
                    self.app.params_manager.layout_params.update_layout
                )

    def update_colored_labels_position(self, valid_photos, frame_width, frame_height):
        """更新背景色照片标签的位置"""
        padding_between = 2  # 减小照片间距
        
        # 重置所有标签的位置
        for label in self.colored_labels:
            label.place_forget()
        
        if not valid_photos:
            return
            
        photo_count = len(valid_photos)
        
        if photo_count == 1:
            # 单张照片居中显示
            idx = valid_photos[0]
            self.colored_labels[idx].place(relx=0.5, rely=0.5, anchor='center')
        else:
            if 0 not in valid_photos:
                # 如果第一个位置没有照片，其他照片平均分配空间
                active_photos = [i for i in valid_photos if i > 0]
                active_count = len(active_photos)
                
                # 计算每张照片的宽度和起始位置
                total_padding = padding_between * (active_count - 1)
                photo_width = int((frame_width - total_padding) / active_count)
                
                # 计算起始位置
                start_x = 0
                
                for i, idx in enumerate(active_photos):
                    x = start_x + (photo_width + padding_between) * i
                    relx = x / frame_width
                    self.colored_labels[idx].place(relx=relx, rely=0.5, anchor='w')
            else:
                # 如果第一个位置有照片，所有照片平均分配空间
                total_padding = padding_between * (photo_count - 1)
                photo_width = int((frame_width - total_padding) / photo_count)
                
                # 计算起始位置
                start_x = 0
                
                for i, idx in enumerate(valid_photos):
                    x = start_x + (photo_width + padding_between) * i
                    relx = x / frame_width
                    self.colored_labels[idx].place(relx=relx, rely=0.5, anchor='w')

    def _resize_and_display(self, label, image, width=None, height=None):
        """调整图片大小并显示"""
        if image is None:
            return
            
        # 转换图像格式
        if isinstance(image, np.ndarray):
            if image.shape[2] == 4:  # BGRA
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            else:  # BGR
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
        elif not isinstance(image, Image.Image):
            return
            
        # 使用传入的尺寸或获取标签尺寸
        if width is not None and height is not None:
            target_width = width
            target_height = height
        else:
            frame = label.master
            target_width = frame.winfo_width() - 20
            target_height = frame.winfo_height() - 20
            
            # 确保最小尺寸
            target_width = max(target_width, self.preview_style['min_width'] - 20)
            target_height = max(target_height, self.preview_style['min_height'] - 20)
        
        # 计算缩放比例，确保图片完全适应框架
        img_ratio = image.width / image.height
        frame_ratio = target_width / target_height
        
        if img_ratio > frame_ratio:
            # 图片更宽，以高度为基准
            new_height = int(target_height)
            new_width = int(target_height * img_ratio)
            if new_width > target_width:
                # 如果宽度超出，则以宽度为基准重新计算
                new_width = int(target_width)
                new_height = int(target_width / img_ratio)
        else:
            # 图片更高，以宽度为基准
            new_width = int(target_width)
            new_height = int(target_width / img_ratio)
            if new_height > target_height:
                # 如果高度超出，则以高度为基准重新计算
                new_height = int(target_height)
                new_width = int(target_height * img_ratio)
        
        # 生成缓冲键
        buffer_key = (id(image), new_width, new_height)
        
        # 检查缓冲区
        if buffer_key in self.buffer_images:
            photo = self.buffer_images[buffer_key]
        else:
            # 创建新的缓冲图像
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            self.buffer_images[buffer_key] = photo
            
            # 清理旧的缓冲
            if len(self.buffer_images) > 20:  # 保持较小的缓冲区
                old_keys = list(self.buffer_images.keys())[:-20]
                for key in old_keys:
                    del self.buffer_images[key]
        
        # 直接更新界面，因为已经在主线程中
        if str(label.winfo_exists()) == "1":  # 确保标签仍然存在
            label.configure(image=photo)
            label.image = photo  # 保持引用

    def precache_image(self, image):
        """预缓存不同尺寸的图片"""
        if image is None:
            return
            
        if isinstance(image, np.ndarray):
            # 转换OpenCV图像为PIL图像
            if image.shape[2] == 4:  # BGRA
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            else:  # BGR
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
        elif not isinstance(image, Image.Image):
            return
            
        # 为每个预定义尺寸创建缓存
        for cache_width, cache_height in self.cache_sizes:
            # 计算保持比例的尺寸
            width_ratio = cache_width / image.width
            height_ratio = cache_height / image.height
            ratio = min(width_ratio, height_ratio) * 0.95
            
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            # 创建缓存
            cache_key = (id(image), cache_width, cache_height)
            if cache_key not in self.photo_cache:
                cached_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.photo_cache[cache_key] = cached_image

    def setup_upload_preview(self):
        """设置上传预览区域"""
        # 清除现有内容
        for widget in self.upload_preview_frame.winfo_children():
            widget.destroy()
            
        if hasattr(self.app, 'current_image'):
            # 创建预览标签
            self.upload_label = ttk.Label(self.upload_preview_frame)
            self.upload_label.place(relx=0.5, rely=0.5, anchor='center')
            
            # 显示预览图片
            image = self.app.current_image
            # 转换为numpy数组并更新预览
            self.update_preview(self.upload_label, image)
        else:
            # 创建一个固定大小的Frame来容纳上传按钮
            button_frame = ttk.Frame(self.upload_preview_frame, width=200, height=100)
            button_frame.place(relx=0.5, rely=0.5, anchor='center')
            button_frame.pack_propagate(False)  # 禁止自动调整大小
            
            # 显示上传按钮
            self.upload_btn = ttk.Button(
                button_frame,
                text="点击上传照片\n支持jpg、png格式",
                command=self.app.image_processor.upload_image,
                style='Upload.TButton'
            )
            self.upload_btn.pack(expand=True)

    def setup_matting_button(self):
        """设置抠图按钮"""
        # 清除现有按钮
        for widget in self.matting_btn_container.winfo_children():
            widget.destroy()
        
        # 创建一个固定大小的Frame来容纳抠图按钮
        button_frame = ttk.Frame(self.matting_btn_container, width=150, height=80)
        button_frame.pack(padx=20, pady=20)
        button_frame.pack_propagate(False)  # 禁止自动调整大小
        
        ttk.Button(
            button_frame,
            text="点击抠图",
            command=self.app.image_processor.process_matting,
            style='Primary.TButton'
        ).pack(expand=True)
        
        self.matting_btn_container.place(relx=0.5, rely=0.5, anchor='center')

    def setup_background_button(self):
        """显示换背景按钮"""
        if hasattr(self, 'background_btn_container'):
            # 只在没有照片时显示按钮
            if not hasattr(self.app, 'processed_images') or all(img is None for img in self.app.processed_images):
                # 清除现有按钮
                for widget in self.background_btn_container.winfo_children():
                    widget.destroy()
                    
                # 创建一个固定大小的Frame来容纳换背景按钮
                button_frame = ttk.Frame(self.background_btn_container, width=150, height=80)
                button_frame.pack(padx=20, pady=20)
                button_frame.pack_propagate(False)  # 禁止自动调整大小
                
                # 创建换背景按钮
                ttk.Button(
                    button_frame,
                    text="换背景",
                    command=lambda: self.change_background_and_select(),
                    style='Upload.TButton'
                ).pack(expand=True)
                
                self.background_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def change_background_and_select(self):
        """换背景并选择照片"""
        # 执行换背景操作
        self.app.image_processor.process_background()
        
        # 如果换背景成功，自动选择第一张照片
        if hasattr(self.app, 'processed_images') and self.app.processed_images[0] is not None:
            self.select_photo(0)

    def setup_layout_button(self):
        """设置排版按钮"""
        # 清除现有按钮
        for widget in self.layout_btn_container.winfo_children():
            widget.destroy()
        
        # 创建一个固定大小的Frame来容纳排版按钮
        button_frame = ttk.Frame(self.layout_btn_container, width=150, height=80)
        button_frame.pack(padx=20, pady=20)
        button_frame.pack_propagate(False)  # 禁止自动调整大小
        
        ttk.Button(
            button_frame,
            text="点击排版",
            command=self.app.image_processor.process_layout,
            style='Primary.TButton'
        ).pack(expand=True)
        
        self.layout_btn_container.place(relx=0.5, rely=0.5, anchor='center')

    def setup_preview_buttons(self, frame, is_upload=False):
        """设置预览窗口的工具按钮"""
        if frame == self.colored_frame:
            # 左上角按钮容器
            left_btn_frame = ttk.Frame(frame)
            left_btn_frame.place(relx=0.0, rely=0.0, anchor='nw')
            
            # 上传按钮
            upload_btn = ttk.Button(
                left_btn_frame,
                text="＋",
                width=3,
                style='IconUpload.TButton',
                command=self.upload_additional_photo
            )
            upload_btn.pack(side=tk.LEFT, padx=2)
            
            # 编辑按钮
            edit_btn = ttk.Button(
                left_btn_frame,
                text="✎",
                width=3,
                style='IconUpload.TButton',
                command=lambda: self.edit_selected_photo(is_upload=False)
            )
            edit_btn.pack(side=tk.LEFT, padx=2)
            
            # 右上角按钮容器
            right_btn_frame = ttk.Frame(frame)
            right_btn_frame.place(relx=1.0, rely=0.0, anchor='ne')
            
            # 下载按钮
            download_btn = ttk.Button(
                right_btn_frame,
                text="⭳",
                width=3,
                style='Tool.TButton',
                command=lambda: self.download_preview(frame)
            )
            download_btn.pack(side=tk.LEFT, padx=2)
            
            # 关闭按钮
            close_btn = ttk.Button(
                right_btn_frame,
                text="×",
                width=3,
                style='Tool.TButton',
                command=lambda: self.close_preview(frame, is_upload)
            )
            close_btn.pack(side=tk.LEFT)
            
        elif frame == self.upload_frame:
            # 上传照片区的左上角按钮容器
            left_btn_frame = ttk.Frame(frame)
            left_btn_frame.place(relx=0.0, rely=0.0, anchor='nw')
            
            # 编辑按钮
            edit_btn = ttk.Button(
                left_btn_frame,
                text="✎",
                width=3,
                style='IconUpload.TButton',
                command=lambda: self.edit_selected_photo(is_upload=True)
            )
            edit_btn.pack(side=tk.LEFT, padx=2)
            
            # 右上角按钮容器
            right_btn_frame = ttk.Frame(frame)
            right_btn_frame.place(relx=1.0, rely=0.0, anchor='ne')
            
            # 关闭按钮
            close_btn = ttk.Button(
                right_btn_frame,
                text="×",
                width=3,
                style='Tool.TButton',
                command=lambda: self.close_preview(frame, is_upload)
            )
            close_btn.pack(side=tk.LEFT)
            
        else:
            # 其他预览区域的按钮保持不变
            btn_frame = ttk.Frame(frame)
            btn_frame.place(relx=1.0, rely=0.0, anchor='ne')
            
            if not is_upload:
                # 下载按钮
                download_btn = ttk.Button(
                    btn_frame,
                    text="⭳",
                    width=3,
                    style='Tool.TButton',
                    command=lambda: self.download_preview(frame)
                )
                download_btn.pack(side=tk.LEFT, padx=2)
            
            # 关闭按钮
            close_btn = ttk.Button(
                btn_frame,
                text="×",
                width=3,
                style='Tool.TButton',
                command=lambda: self.close_preview(frame, is_upload)
            )
            close_btn.pack(side=tk.LEFT)

    def download_preview(self, frame):
        """下载预览图片"""
        if frame == self.transparent_frame:
            self.app.image_processor.download_image('transparent')
        elif frame == self.colored_frame:
            # 检查是否有选中的照片
            if hasattr(self, 'selected_label_index') and hasattr(self.app, 'processed_images'):
                # 获取选中的照片
                selected_image = self.app.processed_images[self.selected_label_index]
                if selected_image is not None:
                    # 临时设置 processed_image
                    if not hasattr(self.app, 'processed_image'):
                        self.app.processed_image = selected_image
                        # 下载选中的照片
                        self.app.image_processor.download_image('colored')
                        # 删除临时的 processed_image
                        delattr(self.app, 'processed_image')
                    else:
                        # 如果已存在，则使用临时替换的方式
                        temp_image = self.app.processed_image
                        self.app.processed_image = selected_image
                        # 下载选中的照片
                        self.app.image_processor.download_image('colored')
                        # 恢复原始照片
                        self.app.processed_image = temp_image
                else:
                    messagebox.showwarning("提示", "请先选择要下载的照片")
            else:
                messagebox.showwarning("提示", "请先选择要下载的照片")
        elif frame == self.layout_frame:
            self.app.image_processor.download_image('layout')

    def close_preview(self, frame, is_upload=False):
        """关闭预览图片"""
        if is_upload:
            # 如果是上传窗口，只清除上传相关状态
            if hasattr(self.app, 'current_image'):
                delattr(self.app, 'current_image')
            if hasattr(self.app, 'current_image_path'):
                delattr(self.app, 'current_image_path')
                
            # 只在标签存在且有图片时清除
            if hasattr(self, 'upload_label') and str(self.upload_label.winfo_exists()) == "1":
                self.upload_label.configure(image='')
            
            # 显示上传按钮
            self.setup_upload_preview()
            
        else:
            # 清除对应预览图片
            if frame == self.transparent_frame:
                if hasattr(self.app, 'transparent_image'):
                    delattr(self.app, 'transparent_image')
                if hasattr(self, 'transparent_label') and str(self.transparent_label.winfo_exists()) == "1":
                    self.transparent_label.configure(image='')
                self.setup_matting_button()
                
            elif frame == self.colored_frame:
                # 只清除选中的照片
                if hasattr(self.app, 'processed_images'):
                    # 记住当前选中的索引
                    current_index = self.selected_label_index
                    self.app.processed_images[current_index] = None
                    if hasattr(self, 'colored_labels') and len(self.colored_labels) > current_index:
                        if str(self.colored_labels[current_index].winfo_exists()) == "1":
                            self.colored_labels[current_index].configure(image='')
                    
                    # 清除相关状态
                    if current_index == 0 and hasattr(self.app, 'processed_image'):
                        delattr(self.app, 'processed_image')
                    
                    # 找到下一个有效的照片
                    valid_photos = [i for i in range(3) if self.app.processed_images[i] is not None]
                    if valid_photos:
                        # 选择下一张照片
                        next_index = valid_photos[0]
                        self.select_photo(next_index)
                        # 更新所有照片的显示
                        self.update_preview(
                            self.colored_labels[next_index],
                            self.app.processed_images[next_index]
                        )
                    else:
                        # 如果没有照片了，清除所有相关状态
                        if hasattr(self.app, 'processed_images'):
                            delattr(self.app, 'processed_images')
                        if hasattr(self.app, 'processed_image'):
                            delattr(self.app, 'processed_image')
                        # 隐藏所有预览框架
                        for frame in self.preview_frames:
                            frame.pack_forget()
                        # 隐藏居中容器
                        self.photos_center_container.pack_forget()
                        # 显示换背景按钮
                        self.setup_background_button()
                    
                    # 更新排版预览
                    if hasattr(self.app.params_manager.layout_params, 'update_layout'):
                        self.app.params_manager.layout_params.update_layout()
                    
            elif frame == self.layout_frame:
                if hasattr(self.app, 'layout_image'):
                    delattr(self.app, 'layout_image')
                if hasattr(self, 'layout_label') and str(self.layout_label.winfo_exists()) == "1":
                    self.layout_label.configure(image='')
                self.setup_layout_button()

    def upload_additional_photo(self):
        """上传额外的照片"""
        # 检查是否已有两张照片（不包括第一个位置）
        photo_count = sum(1 for i in range(1, 3)  # 从索引1开始计数
                         if hasattr(self.app, 'processed_images') 
                         and self.app.processed_images[i] is not None)
        if photo_count >= 2:
            messagebox.showwarning("提示", "最多只能上传两张额外照片")
            return
            
        # 打开文件对话框
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择照片",
            filetypes=[
                ("图片文件", "*.jpg;*.jpeg;*.png;*.bmp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 使用PIL读取图片以保持EXIF方向
                image = Image.open(file_path)
                
                # 获取EXIF信息
                try:
                    exif = image._getexif()
                    if exif is not None:
                        orientation = exif.get(274)  # 274是方向标签的ID
                        # 根据EXIF方向信息旋转图片
                        if orientation == 3:
                            image = image.rotate(180, expand=True)
                        elif orientation == 6:
                            image = image.rotate(270, expand=True)
                        elif orientation == 8:
                            image = image.rotate(90, expand=True)
                except:
                    pass  # 如果无法读取EXIF信息，使用原始图片
                
                # 转换为OpenCV格式
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # 初始化processed_images如果不存在
                if not hasattr(self.app, 'processed_images'):
                    self.app.processed_images = [None, None, None]
                
                # 找到第一个空位置（从索引1开始查找）
                for i in range(1, 3):
                    if self.app.processed_images[i] is None:
                        self.app.processed_images[i] = image
                        # 选中新上传的照片
                        self.select_photo(i)
                        # 更新预览
                        self.update_preview(
                            self.colored_labels[i],
                            image
                        )
                        # 隐藏换背景按钮
                        if hasattr(self, 'background_btn_container'):
                            self.background_btn_container.place_forget()
                        # 更新排版预览
                        if hasattr(self.app.params_manager, 'layout_params'):
                            self.app.params_manager.layout_params.update_layout()
                        break
                            
            except Exception as e:
                messagebox.showerror("错误", f"无法打开图片: {str(e)}")

    def edit_selected_photo(self, is_upload=False):
        """编辑选中的照片"""
        if is_upload:
            # 编辑上传区域的照片
            if not hasattr(self.app, 'current_image'):
                return
            image = self.app.current_image
            print("Editing uploaded image:", image)  # 调试输出
        else:
            # 编辑背景色区域的照片
            if not hasattr(self.app, 'processed_images'):
                return
            image = self.app.processed_images[self.selected_label_index]
            print("Editing processed image:", image)  # 调试输出
        
        from dialogs.photo_editor import PhotoEditorDialog
        
        # 确保图像是numpy数组格式
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 打开编辑器
        PhotoEditorDialog(
            self.app.window,
            image,
            lambda edited_image: self.update_edited_photo(edited_image, is_upload)
        )

    def update_edited_photo(self, edited_image, is_upload=False):
        """更新编辑后的照片"""
        if is_upload:
            # 更新上传区域的照片
            # 确保颜色空间是RGB
            if isinstance(edited_image, np.ndarray):
                edited_image = cv2.cvtColor(edited_image, cv2.COLOR_BGR2RGB)
                edited_image = Image.fromarray(edited_image)
            self.app.current_image = edited_image
            self.update_preview(self.upload_label, edited_image)
            
            # 只清除透明图像相关的状态，因为需要重新抠图
            if hasattr(self.app, 'transparent_image'):
                delattr(self.app, 'transparent_image')
            if hasattr(self.app, 'transparent_image_hd'):
                delattr(self.app, 'transparent_image_hd')
                
            # 重置透明照片预览区域
            self.transparent_label.configure(image='')
            
            # 显示抠图按钮
            self.setup_matting_button()
            
        else:
            # 更新背景色区域的照片
            if hasattr(self.app, 'processed_images'):
                # 确保颜色空间是BGR
                if isinstance(edited_image, Image.Image):
                    edited_image = cv2.cvtColor(np.array(edited_image), cv2.COLOR_RGB2BGR)
                self.app.processed_images[self.selected_label_index] = edited_image
                self.update_preview(
                    self.colored_labels[self.selected_label_index],
                    edited_image
                )
                
                # 如果存在排版照片，更新排版
                if hasattr(self.app, 'layout_image'):
                    self.app.params_manager.layout_params.update_layout()

    def select_photo(self, index):
        """选择照片"""
        self.selected_label_index = index
        # 可以添加选中效果
        for i, label in enumerate(self.colored_labels):
            if i == index:
                label.configure(style='Selected.TLabel')
            else:
                label.configure(style='TLabel')

    def edit_photo(self, index):
        """编辑照片"""
        if hasattr(self.app, 'processed_images') and index < len(self.app.processed_images):
            # 保存当前编辑的照片索引
            self.current_edit_index = index
            
            # 创建照片编辑器对话框
            from dialogs.photo_editor import PhotoEditor
            editor = PhotoEditor(
                self.app.window,
                self.app.processed_images[index],
                self.on_photo_edited
            )
            
    def on_photo_edited(self, edited_image):
        """照片编辑完成的回调"""
        if hasattr(self, 'current_edit_index') and hasattr(self.app, 'processed_images'):
            # 更新编辑后的照片
            self.app.processed_images[self.current_edit_index] = edited_image
            
            # 更新预览
            self.update_preview(self.current_edit_index, edited_image)
            
            # 如果存在排版照片，更新排版
            if hasattr(self.app, 'layout_image'):
                self.app.params_manager.layout_params.update_photos()

    def clear_cache(self):
        """清除图片缓存"""
        self.photo_cache.clear()

    def clear_buffer(self):
        """清除图像缓冲"""
        self.buffer_images.clear()