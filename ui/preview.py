import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import tkinter.messagebox as messagebox

class PreviewManager:
    def __init__(self, app):
        self.app = app
        if not hasattr(self.app, 'image_processor'):
            raise AttributeError("IDPhotoProcessor must have image_processor before creating PreviewManager")
        
        self.preview_style = {
            'width': 400,
            'height': 360,
            'padding': 10
        }
        self.setup_preview_areas()
        
    def setup_preview_areas(self):
        """设置预览区域"""
        # 创建左侧预览区容器
        preview_container = ttk.Frame(self.app.left_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 上传和透明照片预览区（第一行）
        top_row = ttk.Frame(preview_container)
        top_row.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 背景色照片和排版照预览（第二行）
        bottom_row = ttk.Frame(preview_container)
        bottom_row.pack(fill=tk.BOTH, expand=True)
        
        # 先创建所有框架
        self.setup_frames(top_row, bottom_row)
        
        # 再设置按钮和预览
        self.setup_buttons_and_preview()
        
    def setup_frames(self, top_row, bottom_row):
        """创建所有框架"""
        # 上传区域框架
        self.upload_frame = ttk.LabelFrame(top_row, text="上传照片", padding=10)
        self.upload_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.upload_frame.configure(width=self.preview_style['width'], 
                                  height=self.preview_style['height'])
        self.upload_frame.pack_propagate(False)
        
        # 透明照片框架
        self.transparent_frame = ttk.LabelFrame(top_row, text="透明照片", padding=10)
        self.transparent_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.transparent_frame.configure(width=self.preview_style['width'], 
                                 height=self.preview_style['height'])
        self.transparent_frame.pack_propagate(False)
        
        # 背景色照片框架
        self.colored_frame = ttk.LabelFrame(bottom_row, text="背景色照片", padding=10)
        self.colored_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.colored_frame.configure(width=self.preview_style['width'], 
                             height=self.preview_style['height'])
        self.colored_frame.pack_propagate(False)
        
        # 排版照片框架
        self.layout_frame = ttk.LabelFrame(bottom_row, text="排版照片", padding=10)
        self.layout_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.layout_frame.configure(width=self.preview_style['width'], 
                            height=self.preview_style['height'])
        self.layout_frame.pack_propagate(False)
        
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
        # 上传预览区（使用Frame包装Label以实现居中）
        self.upload_preview_frame = ttk.Frame(self.upload_frame)
        self.upload_preview_frame.pack(fill=tk.BOTH, expand=True)
        self.upload_preview_frame.grid_rowconfigure(0, weight=1)
        self.upload_preview_frame.grid_columnconfigure(0, weight=1)
        
        # 创建预览标签
        self.upload_label = ttk.Label(self.upload_preview_frame)
        self.upload_label.grid(row=0, column=0)  # 使用grid布局实现居中
        
        # 添加工具按钮
        self.setup_preview_buttons(self.upload_frame, is_upload=True)
        
        # 初始化上传预览
        self.setup_upload_preview()

    def setup_transparent_preview(self):
        """设置透明照片预览区"""
        # 创建预览容器（使用Frame包装Label以实现居中）
        preview_container = ttk.Frame(self.transparent_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        # 创建预览标签
        self.transparent_label = ttk.Label(preview_container, style='Transparent.TLabel')
        self.transparent_label.grid(row=0, column=0)
        
        # 创建抠图按钮容器
        self.matting_btn_container = ttk.Frame(self.transparent_frame)
        self.matting_btn_container.pack()  # 先pack，后place
        self.setup_matting_button()
        
        # 添加工具按钮
        self.setup_preview_buttons(self.transparent_frame)

    def setup_colored_preview(self):
        """设置背景色照片预览区"""
        # 创建预览容器（水平排列）
        self.colored_container = ttk.Frame(self.colored_frame)
        self.colored_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建多个预览标签
        self.colored_labels = []
        for i in range(3):  # 最多3张照片
            preview_frame = ttk.Frame(self.colored_container)
            preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
            preview_frame.grid_rowconfigure(0, weight=1)
            preview_frame.grid_columnconfigure(0, weight=1)
            
            label = ttk.Label(preview_frame)
            label.grid(row=0, column=0)
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
        
        # 如果已经有照片，隐藏按钮
        if hasattr(self.app, 'processed_images') and any(img is not None for img in self.app.processed_images):
            self.background_btn_container.place_forget()
        else:
            self.background_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 添加工具按钮
        self.setup_preview_buttons(self.colored_frame)
        
        # 初始化选中状态
        self.selected_label_index = 0

    def setup_layout_preview(self):
        """设置排版照片预览区"""
        # 创建预览容器（使用Frame包装Label以实现居中）
        preview_container = ttk.Frame(self.layout_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        # 创建预览标签
        self.layout_label = ttk.Label(preview_container)
        self.layout_label.grid(row=0, column=0)  # 使用grid布局实现居中
        
        # 创建排版按钮容器
        self.layout_btn_container = ttk.Frame(self.layout_frame)
        self.setup_layout_button()
        
        # 添加工具按钮
        self.setup_preview_buttons(self.layout_frame)

    def update_preview(self, label, image):
        """更新预览图片"""
        if image is None:
            label.configure(image='')
            return
            
        # 获取标签大小
        width = self.preview_style['width'] - 2 * self.preview_style['padding']
        height = self.preview_style['height'] - 2 * self.preview_style['padding']
        
        # 如果是背景色照片区域，根据照片数量调整宽度
        if label in self.colored_labels:
            # 计算有多少张非空照片
            valid_photos = [i for i, l in enumerate(self.colored_labels) 
                          if hasattr(self.app, 'processed_images') and 
                          self.app.processed_images[i] is not None]
            photo_count = len(valid_photos)
            
            if photo_count > 1:
                # 多张照片时，计算每张照片的最大宽度
                padding_between = 2  # 照片间距改为2
                total_padding = padding_between * (photo_count - 1)
                max_width = (width - total_padding) // photo_count
                
                # 计算统一的高度
                target_height = height * 0.95  # 留出一些边距
                
                # 计算所有照片按统一高度缩放后的宽度
                scaled_widths = []
                for idx in valid_photos:
                    img = self.app.processed_images[idx]
                    img_height, img_width = img.shape[:2]
                    aspect_ratio = img_width / img_height
                    scaled_width = target_height * aspect_ratio
                    scaled_widths.append(scaled_width)
                
                # 如果任何照片的缩放宽度超过最大宽度，需要按宽度重新计算高度
                if any(w > max_width for w in scaled_widths):
                    # 按最宽的照片计算统一的高度
                    max_aspect_ratio = max(scaled_widths) / target_height
                    target_height = max_width / max_aspect_ratio
                
                # 更新所有照片的显示
                for idx in valid_photos:
                    img = self.app.processed_images[idx]
                    if img is not None:
                        self._resize_and_display(
                            self.colored_labels[idx],
                            img,
                            max_width,  # 使用最大宽度
                            target_height  # 使用统一高度
                        )
                return
            
        # 单张照片的处理
        if isinstance(image, Image.Image):
            image = np.array(image)
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
        self._resize_and_display(label, image, width, height)
        
        # 如果是背景色照片预览区，隐藏换背景按钮
        if label in self.colored_labels and hasattr(self, 'background_btn_container'):
            self.background_btn_container.place_forget()

    def _resize_and_display(self, label, image, width, height):
        """调整大小并显示图片"""
        # 计算缩放比例，留出一些边距
        img_height, img_width = image.shape[:2]
        scale = min(width/img_width, height/img_height) * 0.95
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # 缩放图片
        resized = cv2.resize(image, (new_width, new_height))
        
        # 转换为PhotoImage
        if len(resized.shape) == 3:
            if resized.shape[2] == 4:  # RGBA图像
                b, g, r, a = cv2.split(resized)
                rgba = cv2.merge([r, g, b, a])
                photo = ImageTk.PhotoImage(Image.fromarray(rgba))
            else:  # BGR图像
                rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(Image.fromarray(rgb_image))
        else:  # 灰度图像
            photo = ImageTk.PhotoImage(Image.fromarray(resized))
            
        # 更新标签
        label.configure(image=photo)
        label.image = photo  # 保持引用

    def setup_upload_preview(self):
        """设置上传预览区域"""
        # 清除现有内容
        for widget in self.upload_preview_frame.winfo_children():
            widget.destroy()
            
        if hasattr(self.app, 'current_image'):
            # 创建预览标签
            self.upload_label = ttk.Label(self.upload_preview_frame)
            self.upload_label.grid(row=0, column=0)  # 使用grid布局实现居中
            
            # 显示预览图片
            image = self.app.current_image
            # 转换为numpy数组并更新预览
            self.update_preview(self.upload_label, image)
        else:
            # 显示上传按钮
            self.upload_btn = ttk.Button(
                self.upload_preview_frame,
                text="点击上传照片\n支持jpg、png格式",
                command=self.app.image_processor.upload_image,
                style='Upload.TButton'
            )
            self.upload_btn.grid(row=0, column=0)  # 使用grid布局实现居中
    
    def setup_matting_button(self):
        """设置抠图按钮"""
        # 清除现有按钮
        for widget in self.matting_btn_container.winfo_children():
            widget.destroy()
        
        self.matting_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Button(
            self.matting_btn_container,
            text="点击抠图",
            command=self.app.image_processor.process_matting,
            style='Primary.TButton'
        ).pack()

    def setup_background_button(self):
        """显示换背景按钮"""
        if hasattr(self, 'background_btn_container'):
            # 只在没有照片时显示按钮
            if not hasattr(self.app, 'processed_images') or all(img is None for img in self.app.processed_images):
                # 清除现有按钮
                for widget in self.background_btn_container.winfo_children():
                    widget.destroy()
                    
                # 创建换背景按钮
                ttk.Button(
                    self.background_btn_container,
                    text="换背景",
                    command=lambda: self.change_background_and_select(),
                    style='Upload.TButton'
                ).pack()
                
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
        
        self.layout_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Button(
            self.layout_btn_container,
            text="点击排版",
            command=self.app.image_processor.process_layout,
            style='Primary.TButton'
        ).pack()

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
            # 如果是上传窗口，清除所有相关状态
            if hasattr(self.app, 'current_image'):
                delattr(self.app, 'current_image')
            if hasattr(self.app, 'current_image_path'):
                delattr(self.app, 'current_image_path')
            if hasattr(self.app, 'transparent_image'):
                delattr(self.app, 'transparent_image')
            if hasattr(self.app, 'transparent_image_hd'):
                delattr(self.app, 'transparent_image_hd')
            if hasattr(self.app, 'processed_image'):
                delattr(self.app, 'processed_image')
            if hasattr(self.app, 'processed_images'):
                delattr(self.app, 'processed_images')
                
            # 清除所有预览
            self.upload_label.configure(image='')
            self.transparent_label.configure(image='')
            for label in self.colored_labels:
                label.configure(image='')
            
            # 显示所有按钮
            self.setup_upload_preview()
            self.setup_matting_button()
            self.setup_background_button()
            
        else:
            # 清除对应预览图片
            if frame == self.transparent_frame:
                if hasattr(self.app, 'transparent_image'):
                    delattr(self.app, 'transparent_image')
                self.transparent_label.configure(image='')
                self.setup_matting_button()
                
            elif frame == self.colored_frame:
                # 只清除选中的照片
                if hasattr(self.app, 'processed_images'):
                    # 记住当前选中的索引
                    current_index = self.selected_label_index
                    self.app.processed_images[current_index] = None
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
                        # 显示换背景按钮
                        self.setup_background_button()
                    
                    # 更新排版预览
                    if hasattr(self.app.params_manager.layout_params, 'update_layout'):
                        self.app.params_manager.layout_params.update_layout()
                    
            elif frame == self.layout_frame:
                if hasattr(self.app, 'layout_image'):
                    delattr(self.app, 'layout_image')
                self.layout_label.configure(image='')
                self.setup_layout_button()

    def upload_additional_photo(self):
        """上传额外的照片"""
        # 检查是否已有两张照片
        photo_count = sum(1 for i in range(1, 3) 
                         if hasattr(self.app, 'processed_images') 
                         and self.app.processed_images[i] is not None)
        if photo_count >= 2:
            messagebox.showwarning("提示", "最多只能上传两张额外照片")
            return
            
        self.app.image_processor.upload_additional_image()
        
        # 找到新上传照片的索引并选中
        if hasattr(self.app, 'processed_images'):
            for i in range(1, 3):
                if self.app.processed_images[i] is not None:
                    # 检查是否是新上传的照片（之前没有选中的照片）
                    if not hasattr(self, 'selected_label_index') or i != self.selected_label_index:
                        # 选中新上传的照片
                        self.select_photo(i)
                        break

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
            
            # 如果有透明图像，清除它以便重新抠图
            if hasattr(self.app, 'transparent_image'):
                delattr(self.app, 'transparent_image')
            if hasattr(self.app, 'transparent_image_hd'):
                delattr(self.app, 'transparent_image_hd')
            if hasattr(self.app, 'processed_image'):
                delattr(self.app, 'processed_image')
            if hasattr(self.app, 'processed_images'):
                delattr(self.app, 'processed_images')
                
            # 重置其他预览区域
            self.transparent_label.configure(image='')
            for label in self.colored_labels:
                label.configure(image='')
            
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

    def select_photo(self, index):
        """选择照片"""
        self.selected_label_index = index
        # 可以添加选中效果
        for i, label in enumerate(self.colored_labels):
            if i == index:
                label.configure(style='Selected.TLabel')
            else:
                label.configure(style='TLabel')