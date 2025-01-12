import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image
from hivision import IDCreator, IDParams
from hivision.creator.choose_handler import choose_handler, HUMAN_MATTING_MODELS, FACE_DETECT_MODELS
from hivision.error import FaceError, APIError
from utils.image_utils import compress_image
import json
import os
from utils.layout_preview import LayoutPreviewGenerator

class ImageProcessor:
    def __init__(self, app):
        self.app = app
        self.creator = IDCreator()
        
        # 检查环境变量
        api_key = os.getenv('FACE_PLUS_API_KEY')
        api_secret = os.getenv('FACE_PLUS_API_SECRET')
        
        # 如果环境变量不存在，尝试从配置文件读取
        if not api_key or not api_secret:
            try:
                with open('api_config.json', 'r') as f:
                    config = json.load(f)
                    api_key = config.get('api_key', '')
                    api_secret = config.get('api_secret', '')
                    
                    if api_key and api_secret:
                        # 设置环境变量
                        os.environ['FACE_PLUS_API_KEY'] = api_key
                        os.environ['FACE_PLUS_API_SECRET'] = api_secret
                        print("已从配置文件设置 Face++ API 环境变量")
                    else:
                        print("警告: Face++ API 凭证未配置")
            except Exception as e:
                print(f"读取 API 配置失败: {str(e)}")
        
    def upload_image(self):
        """上传图片"""
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择照片",
            filetypes=[
                ("图片文件", "*.jpg;*.jpeg;*.png"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 读取图片
                image = Image.open(file_path)
                try:
                    # 获取EXIF信息
                    exif = image._getexif()
                    if exif:
                        # 处理图片方向
                        orientation = exif.get(274)  # 274是方向标签的ID
                        if orientation:
                            # 根据EXIF中的方向信息旋转图片
                            rotate_map = {3: 180, 6: 270, 8: 90}
                            if orientation in rotate_map:
                                image = image.rotate(rotate_map[orientation], expand=True)
                except:
                    pass  # 忽略EXIF处理错误
                
                # 转换为RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 保存图片路径和PIL图像对象
                self.app.current_image_path = file_path
                self.app.current_image = image
                
                # 更新预览
                self.app.preview_manager.setup_upload_preview()
                
                # 更新菜单状态
                self.app.menu_manager.update_menu_state()
                
            except Exception as e:
                messagebox.showerror("错误", f"无法打开图片: {str(e)}")
                
    def clear_upload(self):
        """清除上传的照片"""
        # 清除所有图片相关的属性
        if hasattr(self.app, 'current_image_path'):
            delattr(self.app, 'current_image_path')
        if hasattr(self.app, 'current_image'):
            delattr(self.app, 'current_image')
        if hasattr(self.app, 'transparent_image'):
            delattr(self.app, 'transparent_image')
        if hasattr(self.app, 'transparent_image_hd'):
            delattr(self.app, 'transparent_image_hd')
        if hasattr(self.app, 'processed_image'):
            delattr(self.app, 'processed_image')
        if hasattr(self.app, 'layout_image'):
            delattr(self.app, 'layout_image')
        
        # 重置旋转角度
        self.app.current_rotation = 0
        
        # 清除预览区域
        self.app.preview_manager.setup_upload_preview()
        
        # 清除所有预览图片
        if hasattr(self.app.preview_manager, 'transparent_label'):
            self.app.preview_manager.transparent_label.configure(image='')
        if hasattr(self.app.preview_manager, 'colored_label'):
            self.app.preview_manager.colored_label.configure(image='')
        if hasattr(self.app.preview_manager, 'layout_label'):
            self.app.preview_manager.layout_label.configure(image='')
        
        # 显示所有功能按钮
        if hasattr(self.app.preview_manager, 'matting_btn_container'):
            self.app.preview_manager.matting_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        if hasattr(self.app.preview_manager, 'background_btn_container'):
            self.app.preview_manager.background_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        if hasattr(self.app.preview_manager, 'layout_btn_container'):
            self.app.preview_manager.layout_btn_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 更新菜单状态
        self.app.menu_manager.update_menu_state()
        
    def rotate_image(self, direction):
        """旋转图片
        Args:
            direction: 'left' 或 'right'
        """
        if not hasattr(self.app, 'current_image'):
            return
        
        # 计算旋转角度
        angle = -90 if direction == 'left' else 90
        self.app.current_rotation = (self.app.current_rotation + angle) % 360
        
        # 旋转图片
        self.app.current_image = self.app.current_image.rotate(angle, expand=True)
        
        # 更新预览
        self.app.preview_manager.setup_upload_preview()
        
        # 如果已经有抠图结果，重新抠图
        if hasattr(self.app, 'transparent_image'):
            self.process_matting()

    def process_matting(self):
        """抠图处理"""
        try:
            if not hasattr(self.app, 'current_image'):
                self.upload_image()
                if not hasattr(self.app, 'current_image'):  # 如果用户取消上传
                    return
            
            # 获取选择的尺寸名称
            size_name = self.app.params_manager.matting_params.matting_size_var.get()
            if not size_name:
                size_name = "五寸 (127×89mm)"  # 默认使用五寸
            
            # 切换到抠图参数标签页
            self.app.params_notebook.select(0)
            
            # 准备图片数据 - 转换为BGR格式
            image = cv2.cvtColor(np.array(self.app.current_image), cv2.COLOR_RGB2BGR)
            
            # 检查是否选择了 face++
            face_model = self.app.params_manager.matting_params.get_face_model()
            if "face++" in face_model.lower():
                # 检查 API 凭证
                api_key = os.getenv('FACE_PLUS_API_KEY')
                api_secret = os.getenv('FACE_PLUS_API_SECRET')
                if not api_key or not api_secret:
                    messagebox.showwarning(
                        "警告",
                        "Face++ API 未配置，将使用备用人脸检测模型"
                    )
                    face_model = "retinaface-resnet50"
            
            # 设置抠图和人脸检测模型
            try:
                choose_handler(
                    self.creator,
                    self.app.params_manager.matting_params.get_matting_model(),
                    face_model
                )
            except APIError as e:
                print(f"Face++ API 错误: {str(e)}")
                # 如果 Face++ 失败，切换到备用模型
                choose_handler(
                    self.creator,
                    self.app.params_manager.matting_params.get_matting_model(),
                    "retinaface-resnet50"  # 使用备用人脸检测模型
                )
            
            # 获取参数
            top_value = float(self.app.top_value.get())
            ratio_value = float(self.app.ratio_value.get())
            
            # 获取抠图尺寸
            size_key = self.app.params_manager.matting_params.matting_size_var.get()
            photo_size = self.app.params_manager.matting_params.photo_sizes.get(size_key, (25, 35))  # 默认一寸
            
            # 计算像素尺寸（300dpi）
            dpi = 300
            width = int(photo_size[0] * dpi / 25.4)  # 将毫米转换为像素
            height = int(photo_size[1] * dpi / 25.4)
            
            # 直接执行抠图，不使用 IDParams
            result = self.creator(
                image,
                head_measure_ratio=ratio_value,
                head_top_range=(top_value, 0.1),
                face_alignment=self.app.align_var.get(),
                brightness_strength=self.app.brightness_var.get(),
                contrast_strength=self.app.contrast_var.get(),
                sharpen_strength=self.app.sharpen_var.get(),
                saturation_strength=self.app.saturation_var.get(),
                size=(height, width)
            )
            
            # 保存结果 - 保持BGRA格式
            self.app.transparent_image = result.standard
            if self.app.hd_var.get():
                self.app.transparent_image_hd = result.hd
            
            # 更新预览 - 根据高清选项显示对应版本
            if self.app.hd_var.get():
                preview_image = self.app.transparent_image_hd
            else:
                preview_image = self.app.transparent_image
                
            self.app.preview_manager.update_preview(
                self.app.preview_manager.transparent_label,
                preview_image
            )
            
            # 隐藏抠图按钮
            if hasattr(self.app.preview_manager, 'matting_btn_container'):
                self.app.preview_manager.matting_btn_container.place_forget()
            
            # 更新菜单状态
            self.app.menu_manager.update_menu_state()
            
        except Exception as e:
            messagebox.showerror("错误", f"抠图失败: {str(e)}")
        
    def hex_to_bgr(self, hex_color):
        """将HEX颜色转换为BGR元组"""
        hex_color = hex_color.lstrip('#')
        b = int(hex_color[0:2], 16)  # 蓝色分量
        g = int(hex_color[2:4], 16)  # 绿色分量
        r = int(hex_color[4:6], 16)  # 红色分量
        return (b, g, r)  # 直接返回 BGR 顺序

    def process_background(self):
        """换背景处理"""
        try:
            if not hasattr(self.app, 'transparent_image'):
                self.process_matting()
                if not hasattr(self.app, 'transparent_image'):
                    return
            
            # 切换到换背景参数标签页
            self.app.params_notebook.select(1)
            
            # 获取图片尺寸
            height, width = self.app.transparent_image.shape[:2]
            
            # 创建背景
            if hasattr(self.app.params_manager.background_params, 'render_var') and \
               self.app.params_manager.background_params.render_var.get() > 0:
                # 渐变模式
                if self.app.params_manager.background_params.render_var.get() == 1:  # 上下渐变
                    start_hex = self.app.params_manager.background_params.get_bgr_color(
                        self.app.params_manager.background_params.start_color_var.get()
                    )
                    end_hex = self.app.params_manager.background_params.get_bgr_color(
                        self.app.params_manager.background_params.end_color_var.get()
                    )
                    background = self.create_vertical_gradient(width, height, start_hex, end_hex)
                else:  # 中心渐变
                    start_hex = self.app.params_manager.background_params.get_bgr_color(
                        self.app.params_manager.background_params.start_color_var.get()
                    )
                    end_hex = self.app.params_manager.background_params.get_bgr_color(
                        self.app.params_manager.background_params.end_color_var.get()
                    )
                    background = self.create_radial_gradient(width, height, start_hex, end_hex)
            else:
                # 纯色背景
                color_name = self.app.params_manager.background_params.background_color_var.get()
                hex_color = self.app.params_manager.background_params.get_bgr_color(color_name)
                if not hex_color:
                    hex_color = "#FF0000"  # 默认蓝色 (BGR)
                
                # 转换颜色为BGR
                bgr = self.hex_to_bgr(hex_color)
                background = np.full((height, width, 3), bgr, dtype=np.uint8)
            
            # 合并背景和透明照片
            result = self.merge_with_background(self.app.transparent_image, background)
            
            # 保存结果
            self.app.processed_image = result
            if not hasattr(self.app, 'processed_images'):
                self.app.processed_images = [None] * 3
            self.app.processed_images[0] = result
            
            # 更新预览
            self.app.preview_manager.update_preview(
                self.app.preview_manager.colored_labels[0],
                self.app.processed_image
            )
            
            # 隐藏换背景按钮
            if hasattr(self.app.preview_manager, 'background_btn_container'):
                self.app.preview_manager.background_btn_container.place_forget()
            
            # 更新菜单状态
            self.app.menu_manager.update_menu_state()
            
            # 更新排版参数
            if hasattr(self.app.params_manager.layout_params, 'update_photo_settings'):
                self.app.params_manager.layout_params.update_photo_settings()
            
        except Exception as e:
            messagebox.showerror("错误", f"换背景失败: {str(e)}")

    def create_vertical_gradient(self, width, height, start_hex, end_hex):
        """创建上下渐变背景"""
        background = np.zeros((height, width, 3), dtype=np.uint8)
        start_bgr = self.hex_to_bgr(start_hex)
        end_bgr = self.hex_to_bgr(end_hex)
        
        # 获取渐变强度（-100到100）
        strength = self.app.params_manager.background_params.gradient_strength_var.get()
        
        # 根据强度正负决定渐变方向
        if strength >= 0:
            ratio_scale = strength / 100.0  # 0到1
            for y in range(height):
                ratio = y / (height - 1)
                adjusted_ratio = ratio * ratio_scale
                color = tuple(int(start_bgr[i] * (1 - adjusted_ratio) + end_bgr[i] * adjusted_ratio) for i in range(3))
                background[y, :] = color
        else:
            ratio_scale = -strength / 100.0  # 0到1
            for y in range(height):
                ratio = 1 - (y / (height - 1))
                adjusted_ratio = ratio * ratio_scale
                color = tuple(int(start_bgr[i] * (1 - adjusted_ratio) + end_bgr[i] * adjusted_ratio) for i in range(3))
                background[y, :] = color
            
        return background

    def create_radial_gradient(self, width, height, start_hex, end_hex):
        """创建中心渐变背景"""
        background = np.zeros((height, width, 3), dtype=np.uint8)
        start_bgr = self.hex_to_bgr(start_hex)
        end_bgr = self.hex_to_bgr(end_hex)
        
        center_x, center_y = width // 2, height // 2
        max_dist = np.sqrt((width/2)**2 + (height/2)**2)
        
        y, x = np.ogrid[:height, :width]
        distances = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # 获取渐变强度（-100到100）
        strength = self.app.params_manager.background_params.gradient_strength_var.get()
        
        # 根据强度正负决定渐变方向
        if strength >= 0:
            ratio_scale = strength / 100.0  # 0到1
            ratios = np.clip(distances / max_dist * ratio_scale, 0, 1)
        else:
            ratio_scale = -strength / 100.0  # 0到1
            ratios = np.clip((1 - distances / max_dist) * ratio_scale, 0, 1)
        
        for i in range(3):
            background[:, :, i] = (start_bgr[i] * (1 - ratios) + end_bgr[i] * ratios).astype(np.uint8)
        
        return background

    def merge_with_background(self, foreground, background):
        """合并前景和背景"""
        # 分离前景的BGR和Alpha通道
        b, g, r, a = cv2.split(foreground)
        foreground_bgr = cv2.merge([b, g, r])
        
        # 归一化Alpha通道
        alpha = a.astype(float) / 255
        
        # 扩展维度以便广播
        alpha = np.expand_dims(alpha, axis=-1)
        
        # 合并图像
        result = (foreground_bgr * alpha + background * (1 - alpha)).astype(np.uint8)
        
        return result

    def process_layout(self):
        """排版处理"""
        try:
            # 检查是否有照片可以排版
            if not hasattr(self.app, 'processed_images'):
                messagebox.showerror("错误", "请先准备需要排版的照片")
                return
                
            valid_photos = [i for i, img in enumerate(self.app.processed_images) if img is not None]
            if not valid_photos:
                # 如果没有有效照片，清除排版结果
                if hasattr(self.app, 'layout_image'):
                    delattr(self.app, 'layout_image')
                    self.app.preview_manager.layout_label.configure(image='')
                    self.app.preview_manager.setup_layout_button()
                return
            
            # 获取当前选中的排版样式
            selection = self.app.params_manager.layout_params.styles_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请先选择排版样式")
                return
                
            style_name = self.app.params_manager.layout_params.styles_listbox.get(selection[0])
            style = self.app.params_manager.layout_params.styles[style_name]
            
            # 获取纸张尺寸
            try:
                with open('paper_sizes.json', 'r', encoding='utf-8') as f:
                    paper_sizes = json.load(f)
                paper_size = list(paper_sizes[style['paper_size']])
            except:
                messagebox.showerror("错误", "无法获取纸张尺寸")
                return
            
            # 获取照片尺寸数据
            try:
                with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                    photo_sizes = json.load(f)
            except:
                messagebox.showerror("错误", "无法获取照片尺寸")
                return
            
            # 根据照片数量确定照片索引映射
            if len(valid_photos) == 1:
                photo_mapping = {0: 0, 1: 0, 2: 0}  # 只有一张照片时，所有位置都用这张
            elif len(valid_photos) == 2:
                photo_mapping = {0: 0, 1: 1, 2: 1}  # 两张照片时，第一个位置用第一张，其他用第二张
            else:
                photo_mapping = {0: 0, 1: 1, 2: 2}  # 三张照片时，每个位置用对应的照片
            
            # 准备照片数据
            photos = []
            for i, photo_data in enumerate(style['photos']):
                if photo_data['count'] > 0 and i < len(photo_mapping):
                    photos.append({
                        'size': photo_sizes[photo_data['photo_size']],
                        'count': photo_data['count'],
                        'layout_type': photo_data['layout_type'],
                        'image': self.app.processed_images[valid_photos[photo_mapping[i]]]
                    })
            
            # 生成预览
            canvas = LayoutPreviewGenerator.generate_preview(
                paper_size=paper_size,
                orientation=style['orientation'],
                margins=style['margins'],
                photos=photos,
                spacing=style['spacing'],
                show_gridlines=style['show_gridlines'],
                show_divider=style['show_divider'],
                images=True  # 表示需要绘制实际照片而不是占位符
            )
            
            # 保存结果
            self.app.layout_image = canvas
            
            # 更新预览
            self.app.preview_manager.update_preview(
                self.app.preview_manager.layout_label,
                self.app.layout_image
            )
            
            # 隐藏排版按钮
            if hasattr(self.app.preview_manager, 'layout_btn_container'):
                self.app.preview_manager.layout_btn_container.place_forget()
            
            # 更新菜单状态
            self.app.menu_manager.update_menu_state()
            
        except Exception as e:
            messagebox.showerror("错误", f"排版失败: {str(e)}")

    def draw_gridlines(self, canvas, params):
        """绘制参考线"""
        height, width = canvas.shape[:2]
        color = (200, 200, 200)  # 浅灰色
        thickness = 1
        
        # 获取像素尺寸
        dpi = 300
        margins = {k: int(v * dpi / 25.4) for k, v in params['margins'].items()}
        
        # 绘制边距参考线
        cv2.rectangle(
            canvas,
            (margins['left'], margins['top']),
            (width - margins['right'], height - margins['bottom']),
            color,
            thickness
        )

    def download_image(self, image_type):
        """下载图片
        Args:
            image_type: str - 'transparent', 'colored' 或 'layout'
        """
        try:
            # 检查是否有图片可以保存
            if image_type == 'transparent' and not hasattr(self.app, 'transparent_image'):
                messagebox.showerror("错误", "请先抠图")
                return
            elif image_type == 'colored' and not hasattr(self.app, 'processed_image'):
                messagebox.showerror("错误", "请先换背景")
                return
            elif image_type == 'layout' and not hasattr(self.app, 'layout_image'):
                messagebox.showerror("错误", "请先排版")
                return
            
            # 选择保存路径
            file_path = filedialog.asksaveasfilename(
                title="保存图片",
                initialfile=self.get_default_filename(image_type),
                filetypes=[
                    ("PNG图片", "*.png") if image_type == 'transparent' else ("JPEG图片", "*.jpg"),
                    ("所有文件", "*.*")
                ],
                defaultextension=".png" if image_type == 'transparent' else ".jpg"
            )
            
            if file_path:
                if image_type == 'transparent':
                    # 检查是否使用高清版本
                    if self.app.hd_var.get() and hasattr(self.app, 'transparent_image_hd'):
                        image_data = self.app.transparent_image_hd
                    else:
                        image_data = self.app.transparent_image
                    
                    # 如果是numpy数组，转换为PIL图像
                    if isinstance(image_data, np.ndarray):
                        # BGRA转RGBA
                        b, g, r, a = cv2.split(image_data)
                        rgba = cv2.merge([r, g, b, a])
                        image = Image.fromarray(rgba)
                    else:
                        image = image_data
                    
                    # 保存PNG格式（保持透明通道）
                    image.save(file_path, format='PNG')
                    
                elif image_type == 'colored':
                    # 如果是numpy数组，转换为PIL图像
                    if isinstance(self.app.processed_image, np.ndarray):
                        # BGR转RGB
                        rgb_image = cv2.cvtColor(self.app.processed_image, cv2.COLOR_BGR2RGB)
                        image = Image.fromarray(rgb_image)
                    else:
                        image = self.app.processed_image
                    
                    # 保存JPEG格式
                    image.save(file_path, format='JPEG', quality=95)
                    
                else:  # layout
                    # 如果是numpy数组，转换为PIL图像
                    if isinstance(self.app.layout_image, np.ndarray):
                        # BGR转RGB
                        rgb_image = cv2.cvtColor(self.app.layout_image, cv2.COLOR_BGR2RGB)
                        image = Image.fromarray(rgb_image)
                    else:
                        image = self.app.layout_image
                    
                    # 保存JPEG格式
                    image.save(file_path, format='JPEG', quality=95)
                
                messagebox.showinfo("成功", "图片保存成功")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def get_default_filename(self, image_type):
        """获取默认文件名"""
        if image_type == 'transparent':
            if self.app.hd_var.get():
                return "transparent_hd.png"
            return "transparent.png"
        elif image_type == 'colored':
            return "with_background.jpg"
        else:  # layout
            return "layout.jpg"

    def process_photo(self):
        """一键制作证件照"""
        try:
            # 1. 抠图
            self.process_matting()
            if not hasattr(self.app, 'transparent_image'):
                return
            
            # 2. 换背景
            self.process_background()
            if not hasattr(self.app, 'processed_image'):
                return
            
            # 3. 排版
            self.process_layout()
            if not hasattr(self.app, 'layout_image'):
                return
            
            # 提示完成
            messagebox.showinfo(
                "完成",
                "证件照制作完成！\n"
                "您可以在菜单中选择保存：\n"
                "- 透明照片\n"
                "- 换底片\n"
                "- 排版照片"
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"一键制作失败: {str(e)}")

    def upload_additional_image(self):
        """上传额外的照片"""
        file_path = filedialog.askopenfilename(
            title="选择照片",
            filetypes=[
                ("图片文件", "*.jpg;*.jpeg;*.png"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 使用PIL读取图片，避免中文路径问题
                image = Image.open(file_path)
                # 转换为RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                # 转换为OpenCV格式
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # 初始化processed_images列表
                if not hasattr(self.app, 'processed_images'):
                    self.app.processed_images = [None] * 3
                
                # 如果有processed_image但还没有放入列表，放入第一个位置
                if hasattr(self.app, 'processed_image') and self.app.processed_images[0] is None:
                    self.app.processed_images[0] = self.app.processed_image
                
                # 找到第一个空位
                for i in range(1, 3):
                    if self.app.processed_images[i] is None:
                        self.app.processed_images[i] = image
                        # 更新预览
                        self.app.preview_manager.update_preview(
                            self.app.preview_manager.colored_labels[i],
                            image
                        )
                        break
                
                # 更新排版参数
                self.app.params_manager.layout_params.update_photo_settings()
                
            except Exception as e:
                messagebox.showerror("错误", f"无法打开图片: {str(e)}")

    def print_photo(self):
        """打印照片"""
        try:
            # 检查是否有排版图片
            if not hasattr(self.app, 'layout_image'):
                messagebox.showwarning("提示", "请先进行证照排版")
                return
            
            # 保存临时文件
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, 'photo_print.jpg')
            
            # 保存排版图片为RGB格式
            rgb_image = cv2.cvtColor(self.app.layout_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_image)
            image.save(temp_file, format='JPEG', quality=95)
            
            # 打开系统默认图片查看器进行打印
            if os.name == 'nt':  # Windows
                os.startfile(temp_file, 'print')
            else:  # Linux/Mac
                import subprocess
                subprocess.run(['xdg-open', temp_file])  # Linux
                # subprocess.run(['open', temp_file])  # Mac
                
            # 等待一会儿再删除临时文件
            self.app.window.after(3000, lambda: self.cleanup_temp_file(temp_file))
            
        except Exception as e:
            messagebox.showerror("错误", f"打印失败: {str(e)}")
        
    def cleanup_temp_file(self, temp_file):
        """清理临时文件"""
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass