import tkinter as tk
from tkinter import ttk, messagebox
import json
import cv2
import numpy as np
from PIL import Image, ImageTk
from utils.layout_preview import LayoutPreviewGenerator

class LayoutEditorDialog:
    def __init__(self, parent, callback=None, edit_style=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑排版样式" if edit_style else "添加自定义排版")
        self.dialog.geometry("1200x750")
        
        self.callback = callback
        self.edit_style = edit_style  # 保存要编辑的样式数据
        self.setup_ui()
        
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
        
    def setup_ui(self):
        """设置UI"""
        # 主容器 - 左右分栏
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧预览区
        preview_frame = ttk.LabelFrame(main_frame, text="排版预览", padding=10)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 创建预览容器，用于居中显示
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建预览标签
        self.preview_label = ttk.Label(preview_container)
        
        # 绑定容器大小变化事件
        preview_container.bind('<Configure>', self.on_container_resize)
        
        # 右侧参数区
        params_frame = ttk.Frame(main_frame)
        params_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 样式名称
        name_frame = ttk.LabelFrame(params_frame, text="样式名称", padding=5)
        name_frame.pack(fill=tk.X, pady=(0, 2))
        
        self.name_var = tk.StringVar()
        if self.edit_style:
            self.name_var.set(self.edit_style['name'])
            ttk.Entry(name_frame, textvariable=self.name_var, state='readonly').pack(fill=tk.X)
        else:
            ttk.Entry(name_frame, textvariable=self.name_var).pack(fill=tk.X)
        
        # 纸张设置
        paper_frame = ttk.LabelFrame(params_frame, text="纸张设置", padding=5)
        paper_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 加载纸张尺寸数据
        try:
            with open('paper_sizes.json', 'r', encoding='utf-8') as f:
                self.paper_sizes = json.load(f)
        except:
            self.paper_sizes = {}
            
        paper_size_list = list(self.paper_sizes.keys())
        
        # 纸张尺寸下拉框
        # 如果是编辑模式，使用保存的值，否则使用第一个纸张尺寸
        default_paper = (self.edit_style['paper_size'] if self.edit_style 
                        else paper_size_list[0] if paper_size_list 
                        else "A4 (210×297mm)")
        self.paper_var = tk.StringVar(value=default_paper)
        paper_combo = ttk.Combobox(
            paper_frame,
            textvariable=self.paper_var,
            values=paper_size_list,
            state="readonly"
        )
        paper_combo.pack(fill=tk.X, pady=2)
        paper_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        # 纸张方向
        orientation_frame = ttk.Frame(paper_frame)
        orientation_frame.pack(fill=tk.X, pady=2)
        
        # 如果是编辑模式，使用保存的值，否则使用默认值
        default_orientation = self.edit_style['orientation'] if self.edit_style else "portrait"
        self.orientation_var = tk.StringVar(value=default_orientation)
        ttk.Radiobutton(
            orientation_frame,
            text="纵向",
            value="portrait",
            variable=self.orientation_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            orientation_frame,
            text="横向",
            value="landscape",
            variable=self.orientation_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        # 页边距设置
        margin_frame = ttk.LabelFrame(params_frame, text="页边距(mm)", padding=5)
        margin_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 上下边距
        top_bottom_frame = ttk.Frame(margin_frame)
        top_bottom_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(top_bottom_frame, text="上:").pack(side=tk.LEFT)
        # 如果是编辑模式，使用保存的值，否则使用默认值
        default_top = str(self.edit_style['margins']['top']) if self.edit_style else "5"
        self.margin_top_var = tk.StringVar(value=default_top)
        ttk.Spinbox(
            top_bottom_frame,
            from_=0,
            to=50,
            width=5,
            textvariable=self.margin_top_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_bottom_frame, text="下:").pack(side=tk.LEFT, padx=(20, 0))
        default_bottom = str(self.edit_style['margins']['bottom']) if self.edit_style else "5"
        self.margin_bottom_var = tk.StringVar(value=default_bottom)
        ttk.Spinbox(
            top_bottom_frame,
            from_=0,
            to=50,
            width=5,
            textvariable=self.margin_bottom_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        # 左右边距
        left_right_frame = ttk.Frame(margin_frame)
        left_right_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(left_right_frame, text="左:").pack(side=tk.LEFT)
        default_left = str(self.edit_style['margins']['left']) if self.edit_style else "5"
        self.margin_left_var = tk.StringVar(value=default_left)
        ttk.Spinbox(
            left_right_frame,
            from_=0,
            to=50,
            width=5,
            textvariable=self.margin_left_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(left_right_frame, text="右:").pack(side=tk.LEFT, padx=(20, 0))
        default_right = str(self.edit_style['margins']['right']) if self.edit_style else "5"
        self.margin_right_var = tk.StringVar(value=default_right)
        ttk.Spinbox(
            left_right_frame,
            from_=0,
            to=50,
            width=5,
            textvariable=self.margin_right_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        # 照片设置
        photos_frame = ttk.LabelFrame(params_frame, text="照片设置", padding=5)
        photos_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 加载照片尺寸数据
        try:
            with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                self.photo_sizes = json.load(f)
        except:
            self.photo_sizes = {}
            
        photo_size_list = list(self.photo_sizes.keys())
        
        # 创建三个照片的设置
        self.photo_settings = []
        for i in range(3):
            # 每张照片的设置框架
            photo_frame = ttk.LabelFrame(photos_frame, text=f"照片{i+1}设置", padding=2)  # 减小内边距
            photo_frame.pack(fill=tk.X, pady=1)  # 减小外边距
            
            # 照片尺寸
            size_frame = ttk.Frame(photo_frame)
            size_frame.pack(fill=tk.X, pady=1)  # 减小垂直间距
            
            ttk.Label(size_frame, text="尺寸:").pack(side=tk.LEFT)
            size_var = tk.StringVar(value=photo_size_list[0])
            size_combo = ttk.Combobox(
                size_frame,
                textvariable=size_var,
                values=photo_size_list,
                state="readonly",
                width=20
            )
            size_combo.pack(side=tk.LEFT, padx=5)
            size_combo.bind('<<ComboboxSelected>>', self.update_preview)
            
            # 排列方式
            layout_frame = ttk.Frame(photo_frame)
            layout_frame.pack(fill=tk.X, pady=1)  # 减小垂直间距
            
            layout_type_var = tk.StringVar(value="horizontal")
            ttk.Radiobutton(
                layout_frame,
                text="横向排列",
                value="horizontal",
                variable=layout_type_var,
                command=self.update_preview
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Radiobutton(
                layout_frame,
                text="竖向排列",
                value="vertical",
                variable=layout_type_var,
                command=self.update_preview
            ).pack(side=tk.LEFT, padx=5)
            
            # 照片数量
            count_frame = ttk.Frame(photo_frame)
            count_frame.pack(fill=tk.X, pady=1)  # 减小垂直间距
            
            ttk.Label(count_frame, text="数量:").pack(side=tk.LEFT)
            # 设置默认数量：照片1为1，照片2和3为0
            default_count = "1" if i == 0 else "0"
            count_var = tk.StringVar(value=default_count)
            count_spin = ttk.Spinbox(
                count_frame,
                from_=0 if i > 0 else 1,  # 照片1最小值为1，其他为0
                to=100,
                width=5,
                textvariable=count_var,
                command=self.update_preview
            )
            count_spin.pack(side=tk.LEFT, padx=5)
            
            # 保存设置变量
            self.photo_settings.append({
                'size_var': size_var,
                'layout_type_var': layout_type_var,
                'count_var': count_var
            })
            
            # 如果是编辑模式，设置默认值
            if self.edit_style and 'photos' in self.edit_style:
                photo_data = self.edit_style['photos'][i] if i < len(self.edit_style['photos']) else None
                if photo_data:
                    size_var.set(photo_data['photo_size'])
                    layout_type_var.set(photo_data['layout_type'])
                    count_var.set(str(photo_data['count']))
        
        # 照片间隔
        spacing_frame = ttk.LabelFrame(params_frame, text="照片间隔(mm)", padding=5)
        spacing_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 如果是编辑模式，使用保存的值，否则使用默认值
        default_spacing = str(self.edit_style['spacing']) if self.edit_style else "2"
        self.spacing_var = tk.StringVar(value=default_spacing)
        ttk.Spinbox(
            spacing_frame,
            from_=0,
            to=50,
            width=5,
            textvariable=self.spacing_var,
            command=self.update_preview
        ).pack(side=tk.LEFT)
        
        # 其他选项
        options_frame = ttk.LabelFrame(params_frame, text="其他选项", padding=5)
        options_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 创建一个框架来水平排列两个选项
        options_container = ttk.Frame(options_frame)
        options_container.pack(fill=tk.X)
        
        # 如果是编辑模式，使用保存的值，否则使用默认值
        default_gridlines = self.edit_style.get('show_gridlines', True) if self.edit_style else True
        self.show_gridlines_var = tk.BooleanVar(value=default_gridlines)
        ttk.Checkbutton(
            options_container,
            text="显示参考线",
            variable=self.show_gridlines_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, expand=True)
        
        default_divider = self.edit_style.get('show_divider', True) if self.edit_style else True
        self.show_divider_var = tk.BooleanVar(value=default_divider)
        ttk.Checkbutton(
            options_container,
            text="显示分隔线",
            variable=self.show_divider_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, expand=True)
        
        # 底部按钮
        btn_frame = ttk.Frame(params_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 初始化预览
        self.update_preview()
        
    def on_container_resize(self, event):
        """当容器大小改变时更新预览"""
        self.update_preview()
        
    def update_preview(self, *args):
        """更新预览"""
        try:
            # 获取纸张尺寸
            paper_size = list(self.paper_sizes[self.paper_var.get()])
            
            # 获取照片设置
            photos = []
            for photo_settings in self.photo_settings:
                count = int(photo_settings['count_var'].get())
                if count > 0:
                    photo_size = list(self.photo_sizes[photo_settings['size_var'].get()])
                    photos.append({
                        'size': photo_size,
                        'count': count,
                        'layout_type': photo_settings['layout_type_var'].get()
                    })
            
            # 生成预览
            canvas = LayoutPreviewGenerator.generate_preview(
                paper_size=paper_size,
                orientation=self.orientation_var.get(),
                margins={
                    'top': float(self.margin_top_var.get()),
                    'bottom': float(self.margin_bottom_var.get()),
                    'left': float(self.margin_left_var.get()),
                    'right': float(self.margin_right_var.get())
                },
                photos=photos,
                spacing=float(self.spacing_var.get()),
                show_gridlines=self.show_gridlines_var.get(),
                show_divider=self.show_divider_var.get()
            )
            
            # 获取预览容器的大小
            container_width = self.preview_label.master.winfo_width()
            container_height = self.preview_label.master.winfo_height()
            
            if container_width > 1 and container_height > 1:  # 确保容器已经有大小
                # 计算缩放比例，保持纸张比例
                paper_ratio = canvas.shape[1] / canvas.shape[0]  # 宽/高
                container_ratio = container_width / container_height
                
                if paper_ratio > container_ratio:
                    # 以宽度为基准缩放
                    preview_width = int(container_width * 0.9)  # 留出一些边距
                    preview_height = int(preview_width / paper_ratio)
                else:
                    # 以高度为基准缩放
                    preview_height = int(container_height * 0.9)  # 留出一些边距
                    preview_width = int(preview_height * paper_ratio)
                
                # 缩放预览图像
                preview = cv2.resize(canvas, (preview_width, preview_height))
                
                # 转换为PhotoImage
                preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(Image.fromarray(preview_rgb))
                
                # 更新预览标签
                self.preview_label.configure(image=photo)
                self.preview_label.image = photo  # 保持引用
                
                # 居中显示预览标签
                self.preview_label.place(
                    relx=0.5,
                    rely=0.5,
                    anchor="center",
                    width=preview_width,
                    height=preview_height
                )
            
        except Exception as e:
            print(f"预览更新失败: {str(e)}")
            
    def save(self):
        """保存排版样式"""
        # 获取样式名称
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入样式名称")
            return
            
        # 创建样式数据
        style_data = {
            "name": name,
            "paper_size": self.paper_var.get(),
            "orientation": self.orientation_var.get(),
            "margins": {
                "top": float(self.margin_top_var.get()),
                "bottom": float(self.margin_bottom_var.get()),
                "left": float(self.margin_left_var.get()),
                "right": float(self.margin_right_var.get())
            },
            "photos": [
                {
                    "photo_size": settings['size_var'].get(),
                    "layout_type": settings['layout_type_var'].get(),
                    "count": int(settings['count_var'].get())
                }
                for settings in self.photo_settings
            ],
            "spacing": float(self.spacing_var.get()),
            "show_gridlines": bool(self.show_gridlines_var.get()),
            "show_divider": bool(self.show_divider_var.get())
        }
        
        # 加载现有样式
        try:
            with open('layout_styles.json', 'r', encoding='utf-8') as f:
                styles = json.load(f)
        except:
            styles = {}
            
        # 更新样式
        styles[name] = style_data
        
        # 保存样式
        with open('layout_styles.json', 'w', encoding='utf-8') as f:
            json.dump(styles, f, ensure_ascii=False, indent=4)
            
        # 回调通知
        if self.callback:
            self.callback()
            
        messagebox.showinfo("成功", "排版样式保存成功")
        self.dialog.destroy() 