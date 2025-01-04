import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import json
from editors.basic_editor import BasicEditor, CollapsibleFrame
from editors.beauty_editor import BeautyEditor
from editors.facepp_editor import FacePPEditor

class PhotoEditorDialog:
    def __init__(self, parent, image, callback=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑照片")
        self.dialog.geometry("1100x700")
        
        self.original_image = image.copy()  # 保存原始图像
        self.current_image = image.copy()   # 当前编辑的图像
        self.callback = callback
        
        # 创建编辑器实例
        self.basic_editor = BasicEditor(self)
        self.beauty_editor = BeautyEditor(self)
        self.facepp_editor = FacePPEditor(self)
        
        self.crop_rect = None  # 裁剪框坐标
        self.dragging = False  # 拖动状态
        self.drag_start = None  # 拖动起点
        self.preview_scale = 1.0  # 预览缩放比例
        self.preview_offset = (0, 0)  # 预览偏移量
        
        # 添加参考线状态
        self.guide_lines = {
            'h1': 1/3,  # 第一条横线位置（比例）
            'h2': 2/3,  # 第二条横线位置
            'v1': 1/3,  # 第一条竖线位置
            'v2': 2/3,  # 第二条竖线位置
        }
        self.dragging_line = None  # 当前拖动的参考线
        
        # 清除之前的折叠菜单引用
        CollapsibleFrame.clear_frames()
        
        self.setup_ui()
        
        # 设置模态和居中
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_window(parent)
        
        parent.wait_window(self.dialog)

    def setup_ui(self):
        """设置编辑器UI"""
        # 主容器
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧区域 - 固定宽度
        left_frame = ttk.Frame(main_frame, width=750)  # 设置固定宽度
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_frame.pack_propagate(False)  # 禁止自动调整大小
        
        # 工具栏
        self.toolbar = ttk.Frame(left_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # 保存按钮
        save_btn = ttk.Button(
            self.toolbar,
            text="💾保存",
            style='Toolbar.TButton',
            command=self.save_image
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 裁剪按钮和参数面板
        self.crop_frame = ttk.Frame(left_frame)
        crop_btn = ttk.Button(
            self.toolbar,
            text="✂剪裁",
            style='Toolbar.TButton',
            command=lambda: self.toggle_panel(self.crop_frame)
        )
        crop_btn.pack(side=tk.LEFT, padx=5)
        
        # 旋转按钮和参数面板
        self.rotate_frame = ttk.Frame(left_frame)
        rotate_btn = ttk.Button(
            self.toolbar,
            text="🔄旋转",
            style='Toolbar.TButton',
            command=lambda: self.toggle_panel(self.rotate_frame)
        )
        rotate_btn.pack(side=tk.LEFT, padx=5)
        
        # 预览区
        preview_frame = ttk.LabelFrame(left_frame, text="预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建预览容器
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas用于显示图片和参考线
        self.preview_canvas = tk.Canvas(
            preview_container,
            highlightthickness=0,
            bg='#F0F0F0'
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 添加恢复图标按钮（浮动在右
        restore_btn = ttk.Button(
            preview_container,
            text="↺",  # 使用Unicode箭头作为恢复图标
            width=2,
            style='Restore.TButton',
            command=self.restore_image
        )
        restore_btn.place(relx=1.0, x=-10, y=5, anchor='ne')
        
        # 绑定Canvas事件
        self.preview_canvas.bind('<Motion>', self.on_mouse_move)
        self.preview_canvas.bind('<Button-1>', self.on_mouse_down)
        self.preview_canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.preview_canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.preview_canvas.bind('<Double-Button-1>', self.on_double_click)  # 添加双击事件绑定
        
        # 初始化参考线
        self.guide_lines = {
            'h1': {'pos': 1/3, 'id': None},
            'h2': {'pos': 2/3, 'id': None},
            'v1': {'pos': 1/3, 'id': None},
            'v2': {'pos': 2/3, 'id': None}
        }
        
        # 右侧参数区 - 固定宽度
        params_frame = ttk.Frame(main_frame, width=300)  # 设置固定宽度
        params_frame.pack(side=tk.RIGHT, fill=tk.Y)
        params_frame.pack_propagate(False)  # 禁止自动调整大小
        
        # 创建标签页
        self.notebook = ttk.Notebook(params_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 添加基本编辑标签页
        self.basic_editor = BasicEditor(self)
        self.basic_editor.create_widgets(self.notebook)
        
        # 添加本地美颜标签页
        self.beauty_editor = BeautyEditor(self)
        self.beauty_editor.create_widgets(self.notebook)
        
        # 添加Face++标签页
        self.facepp_editor = FacePPEditor(self)
        self.facepp_editor.create_widgets(self.notebook)
        
        # 底部按钮
        btn_frame = ttk.Frame(params_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="确定", command=self.confirm).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset).pack(side=tk.RIGHT, padx=5)
        
        # 创建浮动参数面板容器
        self.popup_frame = ttk.Frame(left_frame, style='Popup.TFrame')
        
        # 裁剪参数面板
        self.crop_frame = ttk.Frame(self.popup_frame)
        self.setup_crop_panel()
        
        # 旋转参数面板
        self.rotate_frame = ttk.Frame(self.popup_frame)
        self.setup_rotate_panel()
        
        # 绑定大小变化事件
        preview_container.bind('<Configure>', lambda e: self.update_preview())
        
        # 显示预览
        self.update_preview()

    def update_preview(self):
        """更新预览图像"""
        try:
            # 获取Canvas尺寸
            preview_width = self.preview_canvas.winfo_width()
            preview_height = self.preview_canvas.winfo_height()
            
            if preview_width <= 1 or preview_height <= 1:
                preview_width = 800
                preview_height = 600
            
            # 计算缩放和偏移
            height, width = self.current_image.shape[:2]
            self.preview_scale = min(preview_width/width, preview_height/height)
            new_width = int(width * self.preview_scale)
            new_height = int(height * self.preview_scale)
            
            # 计算居中位置
            x_offset = (preview_width - new_width) // 2
            y_offset = (preview_height - new_height) // 2
            self.preview_offset = (x_offset, y_offset)
            
            # 缩放图像并转换为PhotoImage
            resized = cv2.resize(self.current_image, (new_width, new_height))
            rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(Image.fromarray(rgb_image))
            
            # 清除Canvas
            self.preview_canvas.delete("all")
            
            # 显示图片
            self.preview_canvas.create_image(
                x_offset, y_offset,
                anchor=tk.NW,
                image=self.photo
            )
            
            # 显示裁剪框
            if hasattr(self, 'crop_frame') and self.crop_frame.winfo_manager():
                if hasattr(self, 'crop_rect') and self.crop_rect:
                    x1, y1, x2, y2 = self.crop_rect
                    # 转换裁剪框坐标到预览尺寸
                    x1 = int(x1 * self.preview_scale) + self.preview_offset[0]
                    y1 = int(y1 * self.preview_scale) + self.preview_offset[1]
                    x2 = int(x2 * self.preview_scale) + self.preview_offset[0]
                    y2 = int(y2 * self.preview_scale) + self.preview_offset[1]
                    
                    # 绘制裁剪框边框
                    self.preview_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline='#00FF00',
                        width=2,
                        tags='crop'
                    )
                    
                    # 绘制九宫格虚线
                    dash_pattern = (5, 5)  # 虚线样式：5像素线段，5像素间隔
                    
                    # 计算三个点
                    third_x1 = x1 + (x2 - x1) / 3
                    third_x2 = x1 + (x2 - x1) * 2 / 3
                    third_y1 = y1 + (y2 - y1) / 3
                    third_y2 = y1 + (y2 - y1) * 2 / 3
                    
                    # 绘制垂直虚线
                    self.preview_canvas.create_line(
                        third_x1, y1, third_x1, y2,
                        fill='#00FF00', dash=dash_pattern,
                        tags='crop_grid'
                    )
                    self.preview_canvas.create_line(
                        third_x2, y1, third_x2, y2,
                        fill='#00FF00', dash=dash_pattern,
                        tags='crop_grid'
                    )
                    
                    # 绘制水平虚线
                    self.preview_canvas.create_line(
                        x1, third_y1, x2, third_y1,
                        fill='#00FF00', dash=dash_pattern,
                        tags='crop_grid'
                    )
                    self.preview_canvas.create_line(
                        x1, third_y2, x2, third_y2,
                        fill='#00FF00', dash=dash_pattern,
                        tags='crop_grid'
                    )
                    
                    # 绘制控制点
                    handle_size = 5
                    handles = [
                        (x1, y1, 'nw'), (x2, y1, 'ne'),
                        (x1, y2, 'sw'), (x2, y2, 'se'),
                        ((x1+x2)/2, y1, 'n'), ((x1+x2)/2, y2, 's'),
                        (x1, (y1+y2)/2, 'w'), (x2, (y1+y2)/2, 'e')
                    ]
                    
                    for x, y, pos in handles:
                        self.preview_canvas.create_rectangle(
                            x - handle_size, y - handle_size,
                            x + handle_size, y + handle_size,
                            fill='white',
                            outline='#00FF00',
                            tags=('crop_handle', f'handle_{pos}')
                        )
            
            # 如果在旋转面板中且显示参考线
            if (hasattr(self, 'rotate_frame') and 
                self.rotate_frame.winfo_manager() and 
                self.show_guides.get()):
                
                # 绘制参考线
                for key, guide in self.guide_lines.items():
                    if key.startswith('h'):  # 横线
                        y = int(new_height * guide['pos']) + y_offset
                        line_id = self.preview_canvas.create_line(
                            x_offset, y,
                            x_offset + new_width, y,
                            fill='#00FF00',
                            width=1,
                            tags=('guide', key),
                            dash=(5, 5)  # 添加虚线样式
                        )
                        guide['id'] = line_id
                    else:  # 竖线
                        x = int(new_width * guide['pos']) + x_offset
                        line_id = self.preview_canvas.create_line(
                            x, y_offset,
                            x, y_offset + new_height,
                            fill='#00FF00',
                            width=1,
                            tags=('guide', key),
                            dash=(5, 5)  # 添加虚线样式
                        )
                        guide['id'] = line_id
            
            # 绑定参考线事件
            self.preview_canvas.tag_bind('guide', '<Enter>', self.on_guide_enter)
            self.preview_canvas.tag_bind('guide', '<Leave>', self.on_guide_leave)
            
        except Exception as e:
            print(f"预览更新失败: {str(e)}")

    def reset(self):
        """重置图像"""
        self.current_image = self.original_image.copy()
        self.update_preview()
        
        # 重置所有编辑器参数
        self.basic_editor.reset()
        self.beauty_editor.reset()
        self.facepp_editor.reset()

    def confirm(self):
        """确认编辑"""
        # 关闭所有面板
        if hasattr(self, 'rotate_frame') and self.rotate_frame.winfo_manager():
            self.toggle_panel(self.rotate_frame)
        if hasattr(self, 'crop_frame') and self.crop_frame.winfo_manager():
            self.toggle_panel(self.crop_frame)
            
        if self.callback:
            self.callback(self.current_image)
        self.dialog.destroy()

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

    def setup_crop_panel(self):
        """设置裁剪参数面板"""
        # 主容器
        content_frame = ttk.Frame(self.crop_frame, style='Panel.TFrame')
        content_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 照片尺寸选择
        ttk.Label(content_frame, text="照片尺寸:").pack(side=tk.LEFT)
        
        # 从photo_sizes.json加载预设尺寸
        try:
            with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                size_map = json.load(f)
                sizes = list(size_map.keys())
                sizes.append("自定义")
        except Exception as e:
            print(f"加载尺寸配置失败: {str(e)}")
            sizes = ["自定义"]
            size_map = {}
            
        self.size_map = size_map
        self.size_var = tk.StringVar(value=sizes[0] if sizes else "自定义")
        
        # 尺寸下拉框
        size_combo = ttk.Combobox(
            content_frame, 
            textvariable=self.size_var,
            values=sizes,
            state="readonly",
            width=20
        )
        size_combo.pack(side=tk.LEFT, padx=5)
        size_combo.bind('<<ComboboxSelected>>', self.on_size_change)
        
        # 自定义尺寸输入框和相关控件
        self.custom_size_frame = ttk.Frame(content_frame)
        ttk.Label(self.custom_size_frame, text="宽:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar()
        ttk.Entry(self.custom_size_frame, textvariable=self.width_var, width=5).pack(side=tk.LEFT)
        
        ttk.Label(self.custom_size_frame, text="高:").pack(side=tk.LEFT, padx=(5,0))
        self.height_var = tk.StringVar()
        ttk.Entry(self.custom_size_frame, textvariable=self.height_var, width=5).pack(side=tk.LEFT)
        
        ttk.Label(self.custom_size_frame, text="mm").pack(side=tk.LEFT)
        
        # 锁定尺寸复选框（默认不勾选）
        self.lock_var = tk.BooleanVar(value=True)  # 默认勾选
        self.lock_checkbox = ttk.Checkbutton(
            self.custom_size_frame, 
            text="锁定",
            variable=self.lock_var,
            command=self.on_lock_change
        )
        self.lock_checkbox.pack(side=tk.LEFT, padx=5)
        
        # 互换按钮移到自定义尺寸框中）
        ttk.Button(
            self.custom_size_frame,
            text="⇄",
            width=2,
            command=self.swap_dimensions
        ).pack(side=tk.LEFT)
        
        # 绑定输入框变化事件
        self.width_var.trace_add('write', self.on_size_input_change)
        self.height_var.trace_add('write', self.on_size_input_change)
        
        # 取消和确定按钮（互换位置）
        ttk.Button(
            content_frame,
            text="取消",
            width=4,
            style='Small.TButton',
            command=lambda: self.toggle_panel(self.crop_frame)
        ).pack(side=tk.RIGHT, padx=(2, 0))
        
        ttk.Button(
            content_frame,
            text="确定",
            width=4,
            style='Small.TButton',
            command=lambda: self.apply_crop()
        ).pack(side=tk.RIGHT, padx=(2, 0))

    def setup_rotate_panel(self):
        """设置旋转参数面板"""
        # 内容域
        content_frame = ttk.Frame(self.rotate_frame, style='Panel.TFrame')
        content_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 所有按钮排一行
        ttk.Button(
            content_frame,
            text="左转90°",
            width=8,
            command=lambda: self.rotate_90(-1)
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            content_frame,
            text="右转90°",
            width=8,
            command=lambda: self.rotate_90(1)
        ).pack(side=tk.LEFT, padx=2)
        
        # 添加水平翻转状态变量
        self.horizontal_flipped = False
        self.horizontal_btn = ttk.Button(
            content_frame,
            text="水平",
            width=8,
            command=self.toggle_horizontal_flip
        )
        self.horizontal_btn.pack(side=tk.LEFT, padx=2)
        
        # 添加上下翻转状态变量
        self.vertical_flipped = False
        self.vertical_btn = ttk.Button(
            content_frame,
            text="上下",
            width=8,
            command=self.toggle_vertical_flip
        )
        self.vertical_btn.pack(side=tk.LEFT, padx=2)
        
        # 微调角度
        angle_frame = ttk.Frame(content_frame)
        angle_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.angle_var = tk.IntVar(value=0)
        angle_scale = ttk.Scale(
            angle_frame,
            from_=-45,
            to=45,
            variable=self.angle_var,
            orient=tk.HORIZONTAL,
            command=self.temp_rotate_by_angle
        )
        angle_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        angle_label = ttk.Label(angle_frame, textvariable=self.angle_var, width=4)
        angle_label.pack(side=tk.LEFT)
        
        # 添加参考线复选框
        self.show_guides = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            content_frame,
            text="参考线",
            variable=self.show_guides,
            command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        # 确定和取消按钮
        ttk.Button(
            content_frame,
            text="确定",
            width=4,
            style='Small.TButton',
            command=self.apply_rotate
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            content_frame,
            text="取消",
            width=4,
            style='Small.TButton',
            command=self.cancel_rotate
        ).pack(side=tk.LEFT, padx=2)

    def toggle_horizontal_flip(self):
        """切换水平翻转状态"""
        if not hasattr(self, 'temp_image'):
            self.temp_image = self.current_image.copy()
            
        self.horizontal_flipped = not self.horizontal_flipped
        if self.horizontal_flipped:
            self.current_image = cv2.flip(self.current_image, 1)
            self.horizontal_btn.configure(style='Toggled.TButton')
        else:
            self.current_image = cv2.flip(self.current_image, 1)  # 再次翻转恢复原状
            self.horizontal_btn.configure(style='TButton')
        self.update_preview()

    def toggle_vertical_flip(self):
        """切换上下翻转状态"""
        if not hasattr(self, 'temp_image'):
            self.temp_image = self.current_image.copy()
            
        self.vertical_flipped = not self.vertical_flipped
        if self.vertical_flipped:
            self.current_image = cv2.flip(self.current_image, 0)
            self.vertical_btn.configure(style='Toggled.TButton')
        else:
            self.current_image = cv2.flip(self.current_image, 0)  # 再次翻转恢复原状
            self.vertical_btn.configure(style='TButton')
        self.update_preview()

    def apply_rotate(self):
        """应用旋转"""
        if hasattr(self, 'temp_image'):
            delattr(self, 'temp_image')
        self.angle_var.set(0)  # 重置角度
        # 重置翻转状态
        self.horizontal_flipped = False
        self.vertical_flipped = False
        self.horizontal_btn.configure(style='TButton')
        self.vertical_btn.configure(style='TButton')
        self.toggle_panel(self.rotate_frame)

    def cancel_rotate(self):
        """取���旋转"""
        if hasattr(self, 'temp_image'):
            self.current_image = self.temp_image.copy()  # 恢复到临时保存的图像
            delattr(self, 'temp_image')
        self.angle_var.set(0)  # 重置角度
        # 重置翻转状态
        self.horizontal_flipped = False
        self.vertical_flipped = False
        self.horizontal_btn.configure(style='TButton')
        self.vertical_btn.configure(style='TButton')
        self.toggle_panel(self.rotate_frame)
        self.update_preview()

    def rotate_90(self, direction):
        """90度旋转
        direction: 1表示顺时针，-1表示逆时针
        """
        # 保存临时图像（如果还没有）
        if not hasattr(self, 'temp_image'):
            self.temp_image = self.original_image.copy()
            
        # 执行旋转（基于原始图像）
        if direction == 1:
            self.current_image = cv2.rotate(self.temp_image, cv2.ROTATE_90_CLOCKWISE)
        else:
            self.current_image = cv2.rotate(self.temp_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
        self.update_preview()

    def temp_rotate_by_angle(self, *args):
        """时按角度旋转"""
        if not hasattr(self, 'temp_image'):
            self.temp_image = self.current_image.copy()
            
        angle = -self.angle_var.get()  # 取反角度，方向正确
        height, width = self.temp_image.shape[:2]
        center = (width // 2, height // 2)
        
        # 计算旋转后的图像大小
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # 调整平移量以确保整个图像可
        matrix[0, 2] += (new_width / 2) - center[0]
        matrix[1, 2] += (new_height / 2) - center[1]
        
        # 执行旋转，使用白色背景
        self.current_image = cv2.warpAffine(
            self.temp_image,
            matrix,
            (new_width, new_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)  # 白色背景
        )
        self.update_preview()

    def apply_crop(self):
        """应用裁剪"""
        if not self.crop_rect:
            return
            
        try:
            x1, y1, x2, y2 = [int(x) for x in self.crop_rect]
            cropped = self.current_image[y1:y2, x1:x2]
            
            if self.size_var.get() == "自定义":
                if self.lock_var.get():
                    # 使用锁定的尺寸
                    w_mm = self.locked_width
                    h_mm = self.locked_height
                else:
                    # 使用输入框的尺寸
                    w_mm = float(self.width_var.get())
                    h_mm = float(self.height_var.get())
            else:
                # 使用预设尺寸
                w_mm, h_mm = self.size_map[self.size_var.get()]
                
            # 转换为像素
            dpi = 300
            target_w = int(w_mm * dpi / 25.4)
            target_h = int(h_mm * dpi / 25.4)
            
            # 调整到目标尺寸
            self.current_image = cv2.resize(cropped, (target_w, target_h))
            
            self.cropping = False
            self.crop_rect = None
            self.toggle_panel(self.crop_frame)
            self.update_preview()
            
        except Exception as e:
            print(f"裁剪失败: {str(e)}")

    def cancel_crop(self):
        """取消裁剪"""
        self.cropping = False
        self.crop_rect = None
        self.toggle_panel(self.crop_frame)
        self.update_preview()

    def toggle_panel(self, panel):
        """切换参数面板的显示状态"""
        if panel.winfo_manager():
            # 隐藏面板
            panel.pack_forget()
            self.popup_frame.place_forget()  # 使用 place_forget 而不是 pack_forget
            
            # 重置状态
            button = None
            if panel == self.crop_frame:
                # 遍历工具栏按钮查找裁剪按钮
                for btn in self.toolbar.winfo_children():
                    if "剪裁" in str(btn.cget("text")):
                        button = btn
                        break
                self.cropping = False  # 停止裁剪模式
                self.crop_rect = None  # 清除裁剪框
                
            elif panel == self.rotate_frame:
                # 遍历工具栏按钮查找旋转按钮
                for btn in self.toolbar.winfo_children():
                    if "旋转" in str(btn.cget("text")):
                        button = btn
                        break
            
            if button:
                button.state(['!pressed'])  # 取消按钮按下状态
            
            self.update_preview()  # 更新预览以清除任何编辑状态
            
        else:
            # 显示面板前先隐藏他面板
            for p in [self.crop_frame, self.rotate_frame]:
                if p != panel and p.winfo_manager():
                    self.toggle_panel(p)
            
            # 显示新面板
            panel.pack(in_=self.popup_frame, fill=tk.BOTH, expand=True)
            
            # 取对应的具栏钮
            button = None
            if panel == self.crop_frame:
                for btn in self.toolbar.winfo_children():
                    if "剪裁" in str(btn.cget("text")):
                        button = btn
                        break
                # 自动显示预设尺寸的裁剪框
                self.show_preset_crop()
                
            elif panel == self.rotate_frame:
                for btn in self.toolbar.winfo_children():
                    if "旋转" in str(btn.cget("text")):
                        button = btn
                        break
            
            if button:
                # 计算面板位置（按钮正下方）
                x = button.winfo_x()
                y = button.winfo_y() + button.winfo_height()
                
                # 显示面板
                self.popup_frame.place(
                    in_=self.toolbar,
                    x=x, y=y,
                    anchor='nw'  # 加锚点设置
                )
                button.state(['pressed'])  # 置钮按下状态

    def show_preset_crop(self):
        """显示预设尺寸的裁剪框"""
        if not self.size_map:
            return
            
        # 获取当���选择的尺寸
        size_name = self.size_var.get()
        if size_name == "自定义":
            size_name = list(self.size_map.keys())[0]  # 使用第一个预设尺寸
            self.size_var.set(size_name)
        
        # 获取预设尺寸的宽高比
        w_mm, h_mm = self.size_map[size_name]
        target_ratio = w_mm / h_mm
        
        # 获取图像尺寸
        img_height, img_width = self.current_image.shape[:2]
        
        # 计算最大可能的裁剪框尺寸
        if img_width / img_height > target_ratio:
            # 图片较宽，以高度为基准
            crop_height = img_height
            crop_width = crop_height * target_ratio
        else:
            # 图片较高，以宽度为基准
            crop_width = img_width
            crop_height = crop_width / target_ratio
        
        # 计算居中位置
        center_x = img_width / 2
        center_y = img_height / 2
        
        # 设置剪框坐标
        x1 = center_x - crop_width / 2
        y1 = center_y - crop_height / 2
        x2 = center_x + crop_width / 2
        y2 = center_y + crop_height / 2
        
        # 更新裁剪框
        self.crop_rect = [x1, y1, x2, y2]
        
        # 锁定宽高比
        self.lock_var.set(True)
        
        # 更新预览
        self.update_preview()

    def on_size_change(self, event):
        """尺寸选择改变的处理"""
        if self.size_var.get() == "自定义":
            # 切换到自定义模式时取消锁定
            self.lock_var.set(False)
            self.on_lock_change()
            # 显示自定义尺寸输入框
            self.custom_size_frame.pack(side=tk.LEFT, padx=5)
        else:
            # 非自定义模式时锁定
            self.lock_var.set(True)
            self.on_lock_change()
            # 隐藏自定义尺寸输入框
            self.custom_size_frame.pack_forget()
            # 更新裁剪框
            self.show_preset_crop()

    def swap_dimensions(self):
        """交换宽高"""
        if self.size_var.get() == "自定义":
            # 交换输入框中的值
            width = self.width_var.get()
            height = self.height_var.get()
            self.width_var.set(height)
            self.height_var.set(width)
            
            # 更新裁剪框
            if self.crop_rect:
                x1, y1, x2, y2 = self.crop_rect
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                current_width = abs(x2 - x1)
                current_height = abs(y2 - y1)
                
                # 计算新的宽（像素）
                dpi = 300
                try:
                    new_width_px = float(height) * dpi / 25.4  # 使用交换后的高作为新宽度
                    new_height_px = float(width) * dpi / 25.4  # 用交换后的宽度作为新高度
                    
                    # 保持中心点不变，更裁剪框坐标
                    half_width = new_width_px / 2
                    half_height = new_height_px / 2
                    
                    self.crop_rect = [
                        center_x - half_width,
                        center_y - half_height,
                        center_x + half_width,
                        center_y + half_height
                    ]
                    self.update_preview()
                except ValueError:
                    print("无效的尺寸值")

    def crop_image(self):
        """裁剪图像"""
        try:
            # 获取目标尺寸（毫米）
            width_mm = float(self.width_var.get())
            height_mm = float(self.height_var.get())
            
            # 转换为像素（假设300dpi）
            dpi = 300
            width_px = int(width_mm * dpi / 25.4)
            height_px = int(height_mm * dpi / 25.4)
            
            # 获取原图尺寸
            img_h, img_w = self.current_image.shape[:2]
            
            # 计算裁剪区域
            if self.lock_var.get():
                # 保持比例
                scale = min(img_w/width_px, img_h/height_px)
                crop_w = int(width_px * scale)
                crop_h = int(height_px * scale)
            else:
                crop_w = img_w
                crop_h = img_h
            
            # 裁剪
            x = (img_w - crop_w) // 2
            y = (img_h - crop_h) // 2
            
            # 裁剪并缩放
            cropped = self.current_image[y:y+crop_h, x:x+crop_w]
            self.current_image = cv2.resize(cropped, (width_px, height_px))
            self.update_preview()
            
        except (ValueError, ZeroDivisionError) as e:
            print(f"裁剪失败: {str(e)}")
            
    def save_image(self):
        """保存图像"""
        if self.callback:
            self.callback(self.current_image)
        self.dialog.destroy()

    def start_crop(self, event):
        """开始裁剪"""
        if not hasattr(self, 'crop_frame') or not self.crop_frame.winfo_manager():
            return
            
        # 转换鼠标坐标到图像坐标
        x = (event.x - self.preview_offset[0]) / self.preview_scale
        y = (event.y - self.preview_offset[1]) / self.preview_scale
        
        # 检查是否点击在裁剪框缘或控制点
        if self.crop_rect:
            x1, y1, x2, y2 = self.crop_rect
            handle_size = 10 / self.preview_scale  # 控制点判定范围
            
            # 检查八个控制点
            handles = [
                ('nw', abs(x - x1) < handle_size and abs(y - y1) < handle_size),
                ('ne', abs(x - x2) < handle_size and abs(y - y1) < handle_size),
                ('sw', abs(x - x1) < handle_size and abs(y - y2) < handle_size),
                ('se', abs(x - x2) < handle_size and abs(y - y2) < handle_size),
                ('n', abs(x - (x1+x2)/2) < handle_size and abs(y - y1) < handle_size),
                ('s', abs(x - (x1+x2)/2) < handle_size and abs(y - y2) < handle_size),
                ('w', abs(x - x1) < handle_size and abs(y - (y1+y2)/2) < handle_size),
                ('e', abs(x - x2) < handle_size and abs(y - (y1+y2)/2) < handle_size)
            ]
            
            for pos, hit in handles:
                if hit:
                    self.dragging = pos
                    self.drag_start = (x, y)
                    return
            
            # 检查是否点击在裁剪框内部
            if x1 < x < x2 and y1 < y < y2:
                self.dragging = 'move'
                self.drag_start = (x - x1, y - y1)  # 点击位置相对于裁剪框左上角的偏移
                return
        
        # 如果没有点击到现有裁剪框，开始新的裁剪
        self.dragging = 'se'  # 从右下角开始调整大小
        self.crop_rect = [x, y, x, y]
        self.update_preview()

    def update_crop(self, event):
        """更新裁剪框"""
        if not self.dragging:
            return
            
        # 转换鼠标坐标到图像坐标
        x = (event.x - self.preview_offset[0]) / self.preview_scale
        y = (event.y - self.preview_offset[1]) / self.preview_scale
        
        # 获取图像尺寸
        height, width = self.current_image.shape[:2]
        x = max(0, min(width, x))
        y = max(0, min(height, y))
        
        if not self.crop_rect:
            self.crop_rect = [x, y, x, y]
            return
            
        x1, y1, x2, y2 = self.crop_rect
        crop_width = x2 - x1
        crop_height = y2 - y1
        
        # 处理不同的拖动模式
        if self.dragging == 'move':
            # 移动整个裁剪框
            if self.drag_start:
                # 计算移动距离
                dx = x - (x1 + self.drag_start[0])
                dy = y - (y1 + self.drag_start[1])
                
                # 计算新位置
                new_x1 = x1 + dx
                new_y1 = y1 + dy
                new_x2 = x2 + dx
                new_y2 = y2 + dy
                
                # 限制图片范围内
                if new_x1 < 0:
                    new_x1 = 0
                    new_x2 = crop_width
                elif new_x2 > width:
                    new_x2 = width
                    new_x1 = width - crop_width
                    
                if new_y1 < 0:
                    new_y1 = 0
                    new_y2 = crop_height
                elif new_y2 > height:
                    new_y2 = height
                    new_y1 = height - crop_height
                
                self.crop_rect = [new_x1, new_y1, new_x2, new_y2]
        
        else:  # 调整裁剪框大小
            # 获取目标宽高比
            target_ratio = None
            if self.size_var.get() != "自定义":
                w_mm, h_mm = self.size_map[self.size_var.get()]
                target_ratio = w_mm / h_mm
            elif self.lock_var.get():
                try:
                    w = float(self.width_var.get() or 0)
                    h = float(self.height_var.get() or 0)
                    if w > 0 and h > 0:
                        target_ratio = w / h
                except ValueError:
                    pass
            
            # 根据拖动的控制点更新坐标
            old_x1, old_y1, old_x2, old_y2 = x1, y1, x2, y2
            
            # 临时更新坐标
            if 'n' in self.dragging: y1 = y
            if 's' in self.dragging: y2 = y
            if 'w' in self.dragging: x1 = x
            if 'e' in self.dragging: x2 = x
            
            # 如果需要保持宽高比
            if target_ratio:
                current_width = abs(x2 - x1)
                current_height = abs(y2 - y1)
                
                # 处理中间控制点的拖动
                if len(self.dragging) == 1:  # 单个方向的控制点
                    if self.dragging in ['n', 's']:  # 上下边中点
                        # 保持宽度不变，调整高度后计算新的宽度
                        new_height = abs(y2 - y1)
                        new_width = new_height * target_ratio
                        
                        # 检查是否超出图片宽度
                        if new_width > width:
                            # 如果超出，反过来用最大宽度计算高度
                            new_width = width
                            new_height = new_width / target_ratio
                            # 更新高度坐标
                            if self.dragging == 'n':
                                y1 = y2 - new_height
                            else:
                                y2 = y1 + new_height
                        
                        # 更新宽度坐标
                        center_x = (x1 + x2) / 2
                        x1 = center_x - new_width / 2
                        x2 = center_x + new_width / 2
                        
                    elif self.dragging in ['w', 'e']:  # 左右边中点
                        # 保持高度不变，调整宽度后计算新的高度
                        new_width = abs(x2 - x1)
                        new_height = new_width / target_ratio
                        
                        # 检查是否超出图片高度
                        if new_height > height:
                            # 如果超出，反过来用最大高度计算宽度
                            new_height = height
                            new_width = new_height * target_ratio
                            # 更新宽度坐标
                            if self.dragging == 'w':
                                x1 = x2 - new_width
                            else:
                                x2 = x1 + new_width
                        
                        # 更新高度坐标
                        center_y = (y1 + y2) / 2
                        y1 = center_y - new_height / 2
                        y2 = center_y + new_height / 2
                    
                    # 更新裁剪框
                    self.crop_rect = [x1, y1, x2, y2]
                    
                elif len(self.dragging) == 2:  # 角点拖动
                    # 计算新的尺寸
                    if 'n' in self.dragging:
                        new_height = current_height
                        new_width = new_height * target_ratio
                    elif 's' in self.dragging:
                        new_height = current_height
                        new_width = new_height * target_ratio
                    elif 'w' in self.dragging:
                        new_width = current_width
                        new_height = new_width / target_ratio
                    elif 'e' in self.dragging:
                        new_width = current_width
                        new_height = new_width / target_ratio
                    
                    # 检查是否超出边界
                    hit_boundary = False
                    temp_x1, temp_y1, temp_x2, temp_y2 = x1, y1, x2, y2
                    
                    # 根据拖动的角点计算新坐标
                    if 'n' in self.dragging:
                        temp_y1 = y2 - new_height
                        if temp_y1 < 0:  # 碰到上边界
                            hit_boundary = True
                            new_height = y2  # 使用到边界的高度
                            new_width = new_height * target_ratio  # 按比例计算宽度
                    if 's' in self.dragging:
                        temp_y2 = y1 + new_height
                        if temp_y2 > height:  # 碰到下边界
                            hit_boundary = True
                            new_height = height - y1  # 使用到边界的高度
                            new_width = new_height * target_ratio  # 按比例计算宽度
                    if 'w' in self.dragging:
                        temp_x1 = x2 - new_width
                        if temp_x1 < 0:  # 碰到左边界
                            hit_boundary = True
                            new_width = x2  # 使用到边界的宽度
                            new_height = new_width / target_ratio  # 按比例计算高度
                    if 'e' in self.dragging:
                        temp_x2 = x1 + new_width
                        if temp_x2 > width:  # 碰到右边界
                            hit_boundary = True
                            new_width = width - x1  # 使用到边界的宽度
                            new_height = new_width / target_ratio  # 按比例计算高度
                    
                    # 如果碰到边界，使用计算出的新尺寸更新坐标
                    if hit_boundary:
                        if 'n' in self.dragging:
                            y1 = y2 - new_height
                        if 's' in self.dragging:
                            y2 = y1 + new_height
                        if 'w' in self.dragging:
                            x1 = x2 - new_width
                        if 'e' in self.dragging:
                            x2 = x1 + new_width
                    else:
                        # 如果没有碰到边界，使用临时计算的坐标
                        x1, y1, x2, y2 = temp_x1, temp_y1, temp_x2, temp_y2
                    
                    # 更新裁剪框坐标
                    self.crop_rect = [x1, y1, x2, y2]
                
                else:  # 没有宽高比自由调整
                    # 直接使用临时更新的坐标
                    pass
            
            # 确保裁剪框不会太小
            min_size = 10 / self.preview_scale
            if abs(x2 - x1) < min_size:
                x1, x2 = old_x1, old_x2
            if abs(y2 - y1) < min_size:
                y1, y2 = old_y1, old_y2
            
            # 确保裁剪框不超出图片边界
            if x1 < 0: x1 = 0
            if x2 > width: x2 = width
            if y1 < 0: y1 = 0
            if y2 > height: y2 = height
            
            self.crop_rect = [x1, y1, x2, y2]
            
            # 在自定义模式且未锁定时，更新输入框的值
            if self.size_var.get() == "自定义" and not self.lock_var.get():
                # 转换像素到毫米
                dpi = 300
                width_mm = abs(x2 - x1) * 25.4 / dpi
                height_mm = abs(y2 - y1) * 25.4 / dpi
                # 更新输入框，避免触发 trace
                self.width_var.set(f"{width_mm:.1f}")
                self.height_var.set(f"{height_mm:.1f}")
        
        self.update_preview()

    def end_crop(self, event):
        """结束裁剪"""
        self.dragging = False
        if self.crop_rect:
            # 确保坐标正确序
            x1, y1, x2, y2 = self.crop_rect
            self.crop_rect = [
                min(x1, x2),
                min(y1, y2),
                max(x1, x2),
                max(y1, y2)
            ]
            self.update_preview()

    def on_lock_change(self):
        """锁定状态改变处理"""
        if self.lock_var.get():
            # 锁定时保存当前输入的尺寸
            try:
                self.locked_width = float(self.width_var.get() or 0)
                self.locked_height = float(self.height_var.get() or 0)
                if self.locked_width <= 0 or self.locked_height <= 0:
                    raise ValueError("Invalid dimensions")
                    
                # 更新裁剪框以匹配锁定的尺寸
                if self.crop_rect:
                    x1, y1, x2, y2 = self.crop_rect
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    # 转换为像素
                    dpi = 300
                    width_px = self.locked_width * dpi / 25.4
                    height_px = self.locked_height * dpi / 25.4
                    
                    # 更新裁剪框
                    self.crop_rect = [
                        center_x - width_px/2,
                        center_y - height_px/2,
                        center_x + width_px/2,
                        center_y + height_px/2
                    ]
                    self.update_preview()
                    
            except ValueError:
                # 使用当前裁剪框的尺寸
                if self.crop_rect:
                    x1, y1, x2, y2 = self.crop_rect
                    dpi = 300
                    self.locked_width = abs(x2 - x1) * 25.4 / dpi
                    self.locked_height = abs(y2 - y1) * 25.4 / dpi
                    self.width_var.set(f"{self.locked_width:.1f}")
                    self.height_var.set(f"{self.locked_height:.1f}")
                else:
                    # 使用默认值
                    self.locked_width = 35
                    self.locked_height = 45
                    self.width_var.set("35.0")
                    self.height_var.set("45.0")
                    
            # 禁用输入框
            for child in self.custom_size_frame.winfo_children():
                if isinstance(child, ttk.Entry):
                    child.configure(state='readonly')
        else:
            # 解锁时启用输入框
            for child in self.custom_size_frame.winfo_children():
                if isinstance(child, ttk.Entry):
                    child.configure(state='normal')

    def on_size_input_change(self, *args):
        """尺寸输入框值改变时的处理"""
        if not self.size_var.get() == "自定义" or self.lock_var.get():
            return
            
        try:
            width = float(self.width_var.get() or 0)
            height = float(self.height_var.get() or 0)
            
            if width <= 0 or height <= 0:
                return
                
            # 转换为像素
            dpi = 300
            width_px = width * dpi / 25.4
            height_px = height * dpi / 25.4
            
            # 获取图像尺寸
            img_height, img_width = self.current_image.shape[:2]
            
            # 如果输入尺寸大于图片尺寸，按比例缩小
            if width_px > img_width or height_px > img_height:
                scale = min(img_width/width_px, img_height/height_px)
                width_px *= scale
                height_px *= scale
                # 更新输入框的值
                width = width_px * 25.4 / dpi
                height = height_px * 25.4 / dpi
                self.width_var.set(f"{width:.1f}")
                self.height_var.set(f"{height:.1f}")
            
            # 如果存在裁剪框更新其尺寸
            if self.crop_rect:
                x1, y1, x2, y2 = self.crop_rect
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # 计算新的裁剪框尺寸
                new_x1 = center_x - width_px / 2
                new_x2 = center_x + width_px / 2
                new_y1 = center_y - height_px / 2
                new_y2 = center_y + height_px / 2
                
                # 保裁剪框不超出图片边界
                if new_x1 < 0:
                    new_x1 = 0
                    new_x2 = width_px
                elif new_x2 > img_width:
                    new_x2 = img_width
                    new_x1 = img_width - width_px
                    
                if new_y1 < 0:
                    new_y1 = 0
                    new_y2 = height_px
                elif new_y2 > img_height:
                    new_y2 = img_height
                    new_y1 = img_height - height_px
                
                # 更新裁剪框
                self.crop_rect = [new_x1, new_y1, new_x2, new_y2]
                self.update_preview()
            
        except ValueError:
            pass

    def on_double_click(self, event):
        """双击处理"""
        if not hasattr(self, 'crop_frame') or not self.crop_frame.winfo_manager():
            return
            
        # 转换鼠标坐标到图像坐标
        x = (event.x - self.preview_offset[0]) / self.preview_scale
        y = (event.y - self.preview_offset[1]) / self.preview_scale
        
        # 检查是否在裁剪框内
        if self.crop_rect:
            x1, y1, x2, y2 = self.crop_rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                # 应用裁剪
                self.apply_crop()

    def restore_image(self):
        """恢复原始图像"""
        self.current_image = self.original_image.copy()
        # 清裁剪框
        if hasattr(self, 'cropping') and self.cropping:
            self.cropping = False
            self.crop_rect = None
        self.update_preview()

    def start_drag_guide(self, event):
        """开始拖动参考线"""
        if not (hasattr(self, 'rotate_frame') and 
            self.rotate_frame.winfo_manager() and 
            self.show_guides.get()):
            return
            
        # 转换鼠标坐标到图像坐标
        x = (event.x - self.preview_offset[0]) / self.preview_scale
        y = (event.y - self.preview_offset[1]) / self.preview_scale
        
        # 获取图像尺寸
        height, width = self.current_image.shape[:2]
        
        # 检查是否点击在参考线（允许5像素的误差）
        tolerance = 5 / self.preview_scale
        
        # 检查横线
        for line_id in ['h1', 'h2']:
            line_y = height * self.guide_lines[line_id]
            if abs(y - line_y) < tolerance:
                self.dragging_line = line_id
                self.preview_label.configure(cursor='sb_v_double_arrow')
                return
                
        # 检查竖线
        for line_id in ['v1', 'v2']:
            line_x = width * self.guide_lines[line_id]
            if abs(x - line_x) < tolerance:
                self.dragging_line = line_id
                self.preview_label.configure(cursor='sb_h_double_arrow')
                return

    def update_guide(self, event):
        """更新参考线位置"""
        if not self.dragging_line:
            return
            
        # 转换鼠标坐标到图像坐标
        x = (event.x - self.preview_offset[0]) / self.preview_scale
        y = (event.y - self.preview_offset[1]) / self.preview_scale
        
        # 获图像尺寸
        height, width = self.current_image.shape[:2]
        
        # 更新参考线位置
        if self.dragging_line.startswith('h'):
            # 横线
            pos = max(0, min(1, y / height))
            self.guide_lines[self.dragging_line] = pos
        else:
            # 竖线
            pos = max(0, min(1, x / width))
            self.guide_lines[self.dragging_line] = pos
            
        self.update_preview()

    def end_drag_guide(self, event):
        """结束拖动参考线"""
        if self.dragging_line:
            self.dragging_line = None
            self.preview_label.configure(cursor='')

    def on_mouse_move(self, event):
        """鼠标移动处理"""
        self.last_mouse_pos = (event.x, event.y)
        # 只在没有拖动参考线时更新预览
        if not self.dragging_line:
            self.update_preview()

    def on_mouse_down(self, event):
        """鼠标按下处理"""
        if hasattr(self, 'rotate_frame') and self.rotate_frame.winfo_manager():
            # 增加选中容差
            tolerance = 10  # 像素
            
            # 获取图像区域
            height, width = self.current_image.shape[:2]
            new_height = int(height * self.preview_scale)
            new_width = int(width * self.preview_scale)
            
            # 检查是否点击在参考线附近
            for key, guide in self.guide_lines.items():
                if key.startswith('h'):  # 横线
                    y = int(new_height * guide['pos']) + self.preview_offset[1]
                    if abs(event.y - y) <= tolerance:
                        self.dragging_line = key
                        self.preview_canvas.configure(cursor='sb_v_double_arrow')
                        return
                else:  # 竖线
                    x = int(new_width * guide['pos']) + self.preview_offset[0]
                    if abs(event.x - x) <= tolerance:
                        self.dragging_line = key
                        self.preview_canvas.configure(cursor='sb_h_double_arrow')
                        return
        
        # 如果没��点击到参考线，处理其他操作
        self.start_crop(event)

    def on_mouse_drag(self, event):
        """鼠标拖动处理"""
        if self.dragging_line and self.show_guides.get():
            # 获取图像区域
            height, width = self.current_image.shape[:2]
            new_height = int(height * self.preview_scale)
            new_width = int(width * self.preview_scale)
            
            # 计算新位置（考虑偏移量）
            if self.dragging_line.startswith('h'):
                # 横线只能上下移动
                pos = (event.y - self.preview_offset[1]) / new_height
                pos = max(0, min(1, pos))  # 限制在0-1范围内
                self.guide_lines[self.dragging_line]['pos'] = pos
                self.preview_canvas.configure(cursor='sb_v_double_arrow')  # 保持光标形状
            else:
                # 竖线只能左右移动
                pos = (event.x - self.preview_offset[0]) / new_width
                pos = max(0, min(1, pos))  # 限制在0-1范围内
                self.guide_lines[self.dragging_line]['pos'] = pos
                self.preview_canvas.configure(cursor='sb_h_double_arrow')  # 保持光标形状
            
            self.update_preview()
        else:
            self.update_crop(event)

    def on_mouse_up(self, event):
        """鼠标释放处理"""
        if self.dragging_line:
            self.dragging_line = None
            self.preview_canvas.configure(cursor='')
        else:
            # 在其他模式下，处理裁剪等操作
            self.end_crop(event)

    def on_guide_enter(self, event):
        """鼠标进入参考线"""
        if not self.dragging_line:  # 只在没有拖动时改变光标
            tolerance = 10  # 增加检测容差范围
            
            # 获取图像区域
            height, width = self.current_image.shape[:2]
            new_height = int(height * self.preview_scale)
            new_width = int(width * self.preview_scale)
            
            # 检查是否在参考线附近
            for key, guide in self.guide_lines.items():
                if key.startswith('h'):  # 横线
                    y = int(new_height * guide['pos']) + self.preview_offset[1]
                    if abs(event.y - y) <= tolerance:
                        self.preview_canvas.configure(cursor='sb_v_double_arrow')
                        return
                else:  # 竖线
                    x = int(new_width * guide['pos']) + self.preview_offset[0]
                    if abs(event.x - x) <= tolerance:
                        self.preview_canvas.configure(cursor='sb_h_double_arrow')
                        return

    def on_guide_leave(self, event):
        """鼠标离开参考线"""
        if not self.dragging_line:
            self.preview_canvas.configure(cursor='')