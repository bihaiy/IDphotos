import tkinter as tk
from tkinter import ttk, messagebox
import win32print
import win32api
import tempfile
import os
from PIL import Image, ImageTk, ImageWin
import cv2
import numpy as np
from tkinter import filedialog
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
import json
import win32ui
import win32gui
import win32con
import win32print

class PrintDialog:
    def __init__(self, parent, image):
        # 创建顶层窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("打印")
        self.dialog.withdraw()  # 先隐藏窗口
        
        # 获取屏幕尺寸
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # 计算窗口尺寸（根据屏幕尺寸调整）
        if screen_width >= 1920 and screen_height >= 1080:
            # 高分辨率屏幕
            window_width = 1200
            window_height = 800
        else:
            # 低分辨率屏幕
            window_width = min(screen_width - 100, 1000)  # 预留边距
            window_height = min(screen_height - 100, 700)  # 预留边距
        
        # 设置窗口最小尺寸
        self.dialog.minsize(800, 600)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 保存图像
        self.image = image
        
        # 初始化变量
        self.printer_var = tk.StringVar()
        self.paper_var = tk.StringVar()
        self.copies_var = tk.StringVar(value="1")
        
        # 根据图像方向设置打印方向
        if isinstance(self.image, np.ndarray):
            height, width = self.image.shape[:2]
        elif isinstance(self.image, Image.Image):
            width, height = self.image.size
        else:
            width, height = 0, 0
            
        # 如果图像是横向的（宽度大于高度），设置为横向打印
        self.orientation_var = tk.StringVar(value="landscape" if width > height else "portrait")
        
        # 获取系统默认打印机
        try:
            self.default_printer = win32print.GetDefaultPrinter()
            self.printer_var.set(self.default_printer)
        except:
            self.default_printer = "Microsoft Print to PDF"
            self.printer_var.set(self.default_printer)
        
        # 加载上次使用的打印机
        self.config_file = 'printer_config.json'
        self.last_printer = self.load_last_printer()
        
        # 初始化打印机变量并设置为上次使用的打印机
        self.printer_var = tk.StringVar(value=self.last_printer if self.last_printer else "")
        
        # 添加纸张尺寸映射表
        self.paper_sizes_mm = {
            "A3": (297, 420),
            "A4": (210, 297),
            "A5": (148, 210),
            "A6": (105, 148),
            "B4": (250, 353),
            "B5": (176, 250),
            "B6": (125, 176),
            "Letter": (216, 279),
            "Legal": (216, 356),
            "Executive": (184, 267),
            "16K": (195, 270),
            "明信片": (100, 148),
        }
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左右分栏
        self.preview_frame = ttk.LabelFrame(main_frame, text="打印预览")
        self.preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        settings_frame = ttk.LabelFrame(main_frame, text="打印设置")
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        # 设置分栏宽度比例
        self.preview_frame.configure(width=500)
        settings_frame.configure(width=250)
        
        # 创建预览区域和设置区域
        self.setup_preview_area()
        self.setup_settings_area(settings_frame)
        
        # 显示窗口
        self.dialog.deiconify()  # 显示窗口
        
        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 延迟初始化打印机设置和预览
        self.dialog.after(100, self.delayed_init)
        
    def delayed_init(self):
        """延迟初始化"""
        # 更新打印机列表
        self.update_printer_list()
        self.printer_cb.bind('<<ComboboxSelected>>', self.on_printer_changed)
        
        # 等待窗口创建完成后居中
        self.dialog.update_idletasks()
        self.center_window()
        
        # 延迟更新预览
        self.dialog.after(100, self.update_preview)
        
    def setup_preview_area(self):
        """设置预览区域"""
        preview_container = ttk.Frame(self.preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建水平标尺
        self.h_ruler = tk.Canvas(preview_container, height=15, bg='white')
        self.h_ruler.pack(fill=tk.X, padx=(15, 0))
        
        # 创建中间区域（包含垂直标尺和预览）
        middle_frame = ttk.Frame(preview_container)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建垂直标尺
        self.v_ruler = tk.Canvas(middle_frame, width=15, bg='white')
        self.v_ruler.pack(side=tk.LEFT, fill=tk.Y)
        
        # 创建预览容器（添加内边距）
        preview_frame = ttk.Frame(middle_frame)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建预览标签
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 设置分栏比例
        self.preview_frame.configure(width=int(self.dialog.winfo_width() * 0.7))  # 预览区域占70%
        
    def setup_settings_area(self, parent):
        """设置打印参数区域"""
        # 打印机选择框架
        printer_frame = ttk.Frame(parent)
        printer_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(printer_frame, text="打印机:").pack(side=tk.LEFT)
        
        # 创建打印机下拉列表
        self.printer_cb = ttk.Combobox(printer_frame, textvariable=self.printer_var, state="readonly")
        self.printer_cb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        # 打印机属性按钮
        prop_btn = ttk.Button(printer_frame, text="属性", width=6, command=self.show_printer_properties)
        prop_btn.pack(side=tk.LEFT)
        
        # 份数设置
        copies_frame = ttk.Frame(parent)
        copies_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(copies_frame, text="份数:").pack(side=tk.LEFT)
        copies_spinbox = ttk.Spinbox(copies_frame, from_=1, to=99, width=5, 
                                   textvariable=self.copies_var)
        copies_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 纸张设置
        paper_frame = ttk.Frame(parent)
        paper_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(paper_frame, text="纸张:").pack(side=tk.LEFT)
        self.paper_cb = ttk.Combobox(paper_frame, textvariable=self.paper_var, state="readonly")
        self.paper_cb.pack(fill=tk.X, padx=(5, 0))
        
        # 绑定纸张选择改变事件
        self.paper_cb.bind('<<ComboboxSelected>>', self.on_paper_changed)
        
        # 方向设置
        orientation_frame = ttk.Frame(parent)
        orientation_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(orientation_frame, text="方向:").pack(side=tk.LEFT)
        ttk.Radiobutton(orientation_frame, text="纵向", value="portrait", 
                       variable=self.orientation_var, command=self.update_preview).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Radiobutton(orientation_frame, text="横向", value="landscape", 
                       variable=self.orientation_var, command=self.update_preview).pack(side=tk.LEFT)
        
        # 按钮区域
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="打印", command=self.print_image).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(fill=tk.X)
        
        # 在所有控件创建完成后，更新打印机列表和纸张尺寸
        self.update_printer_list()
        self.printer_cb.bind('<<ComboboxSelected>>', self.on_printer_changed)

    def update_paper_sizes(self):
        """更新纸张尺寸列表"""
        try:
            printer = win32print.OpenPrinter(self.printer_var.get())
            try:
                # 获取打印机信息
                properties = win32print.GetPrinter(printer, 2)
                dev_mode = properties['pDevMode']
                
                # 获取当前纸张尺寸
                current_paper_size = dev_mode.PaperSize
                
                # 获取打印机支持的纸张列表
                DC_PAPERS = 2
                DC_PAPERNAMES = 16
                
                # 获取支持的纸张ID列表和名称
                papers = win32print.DeviceCapabilities(
                    self.printer_var.get(), "", DC_PAPERS)
                paper_names_list = win32print.DeviceCapabilities(
                    self.printer_var.get(), "", DC_PAPERNAMES)
                
                # 获取打印机支持的所有纸张
                available_sizes = []
                paper_id_map = {}  # 用于存储纸张名称和ID的映射
                
                # 遍历所有支持的纸张
                for i, paper_id in enumerate(papers):
                    try:
                        paper_name = paper_names_list[i].strip()
                        if paper_name and paper_name not in available_sizes:
                            available_sizes.append(paper_name)
                            paper_id_map[paper_name] = paper_id
                    except:
                        continue
                
                # 如果没有获取到任何尺寸，使用默认值
                if not available_sizes:
                    available_sizes = ["A4"]
                
                # 更新下拉列表
                self.paper_cb['values'] = available_sizes
                
                # 设置当前选择的纸张
                try:
                    current_paper_name = paper_names_list[papers.index(current_paper_size)].strip()
                    self.paper_var.set(current_paper_name)
                except:
                    self.paper_var.set(available_sizes[0])
                
                # 更新预览
                self.dialog.after(100, self.update_preview)
                
            finally:
                win32print.ClosePrinter(printer)
                
        except Exception as e:
            print(f"获取纸张尺寸失败: {str(e)}")
            self.paper_var.set("A4")
            self.paper_cb['values'] = ["A4"]
            
    def update_printer_list(self):
        """更新打印机列表"""
        try:
            # 获取当前选中的打印机
            current_printer = self.printer_var.get()
            
            # 获取最新的打印机列表
            printers = []
            
            # 获取本地打印机
            try:
                local_printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1)
                printers.extend([printer[2] for printer in local_printers])
            except:
                pass
                
            # 获取网络打印机
            try:
                network_printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS, None, 1)
                printers.extend([printer[2] for printer in network_printers])
            except:
                pass
                
            # 获取共享打印机
            try:
                shared_printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_SHARED, None, 1)
                printers.extend([printer[2] for printer in shared_printers])
            except:
                pass
            
            # 移除重复项并排序
            self.printers = sorted(list(set(printers)))
            
            # 获取默认打印机
            try:
                self.default_printer = win32print.GetDefaultPrinter()
            except:
                self.default_printer = self.printers[0] if self.printers else "Microsoft Print to PDF"
            
            # 更新下拉列表
            self.printer_cb['values'] = self.printers
            
            # 按优先级选择打印机：
            # 1. 上次选择的打印机（如果还在列表中）
            # 2. 系统默认打印机
            # 3. 列表中的第一个打印机
            # 4. PDF打印机（作为最后的备选）
            if current_printer and current_printer in self.printers:
                # 使用上次选择的打印机
                self.printer_var.set(current_printer)
            elif self.default_printer in self.printers:
                # 使用系统默认打印机
                self.printer_var.set(self.default_printer)
            elif self.printers:
                # 使用列表中的第一个打印机
                self.printer_var.set(self.printers[0])
            else:
                # 使用PDF打印机作为备选
                self.printer_var.set("Microsoft Print to PDF")
            
            # 更新纸张尺寸
            self.update_paper_sizes()
            
        except Exception as e:
            print(f"更新打印机列表失败: {str(e)}")
            # 设置一个默认值
            self.printer_var.set("Microsoft Print to PDF")
            self.printer_cb['values'] = ["Microsoft Print to PDF"]

    def on_printer_changed(self, event):
        """打印机改变时的处理"""
        # 保存选择的打印机
        self.save_last_printer(self.printer_var.get())
        # 更新纸张尺寸列表
        self.update_paper_sizes()
        # 更新预览
        self.dialog.after(100, self.update_preview)

    def show_printer_properties(self):
        """显示打印机首选项"""
        try:
            # 获取当前打印机名称
            printer_name = self.printer_var.get()
            
            # 使用 shell32.dll 打开打印机首选项
            import win32gui
            import win32con
            import win32api
            import time
            
            # 记录当前打印机设置
            old_paper_size = None
            try:
                printer = win32print.OpenPrinter(printer_name)
                try:
                    properties = win32print.GetPrinter(printer, 2)
                    old_paper_size = properties['pDevMode'].PaperSize
                finally:
                    win32print.ClosePrinter(printer)
            except:
                pass
            
            # 打开打印机首选项对话框
            win32api.ShellExecute(
                0,                          # 父窗口句柄
                "open",                     # 操作
                "rundll32.exe",            # 应用程序
                f"printui.dll,PrintUIEntry /e /n \"{printer_name}\"",  # 参数
                "",                         # 工作目录
                win32con.SW_SHOW           # 显示方式
            )
            
            def check_settings_changed():
                try:
                    # 获取当前纸张设置
                    printer = win32print.OpenPrinter(printer_name)
                    try:
                        properties = win32print.GetPrinter(printer, 2)
                        current_paper_size = properties['pDevMode'].PaperSize
                        
                        # 如果纸张设置发生变化，更新纸张列表
                        if old_paper_size is not None and current_paper_size != old_paper_size:
                            self.update_paper_sizes()
                            return
                            
                    finally:
                        win32print.ClosePrinter(printer)
                except:
                    pass
                
                # 如果设置没有变化，继续检查
                self.dialog.after(500, check_settings_changed)
            
            # 开始检查设置变化
            self.dialog.after(1000, check_settings_changed)
                
        except Exception as e:
            messagebox.showerror("错误", f"无法打开打印机首选项：{str(e)}")
            
    def update_preview(self, *args):
        """更新预览"""
        try:
            # 获取预览区域大小
            preview_width = self.preview_frame.winfo_width() - 60
            preview_height = self.preview_frame.winfo_height() - 60
            
            if preview_width <= 0 or preview_height <= 0:
                return
            
            # 获取当前纸张尺寸
            printer_name = self.printer_var.get()
            paper_name = self.paper_var.get()
            paper_width, paper_height = self.get_paper_dimensions(printer_name, paper_name)
            
            # 如果是横向，交换宽高
            if self.orientation_var.get() == "landscape":
                paper_width, paper_height = paper_height, paper_width
            
            # 转换图像格式
            if isinstance(self.image, np.ndarray):
                if len(self.image.shape) == 3 and self.image.shape[2] == 3:
                    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(image)
            elif isinstance(self.image, Image.Image):
                pil_image = self.image.copy()  # 创建副本
            else:
                return
                
            # 获取原始图像尺寸
            img_width, img_height = pil_image.size
            is_landscape = img_width > img_height
            
            # 根据方向和图像方向决定是否需要旋转
            if (is_landscape and self.orientation_var.get() == "portrait") or \
               (not is_landscape and self.orientation_var.get() == "landscape"):
                pil_image = pil_image.rotate(90, expand=True)
                img_width, img_height = pil_image.size
            
            # 计算预览区域的缩放比例
            margin = 10  # 预留边距
            scale_x = (preview_width - 2 * margin) / paper_width
            scale_y = (preview_height - 2 * margin) / paper_height
            scale = min(scale_x, scale_y)
            
            # 计算预览区域中纸张的实际像素尺寸
            paper_pixel_width = int(paper_width * scale)
            paper_pixel_height = int(paper_height * scale)
            
            # 调整图像大小以适应纸张
            ratio = min(paper_pixel_width/img_width, paper_pixel_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # 调整图像大小
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            
            # 创建一个白色背景的新图像，大小为纸张尺寸
            preview_image = Image.new('RGB', (paper_pixel_width, paper_pixel_height), 'white')
            
            # 将调整后的图像粘贴到中心位置
            x = (paper_pixel_width - new_width) // 2
            y = (paper_pixel_height - new_height) // 2
            preview_image.paste(resized_image, (x, y))
            
            # 更新预览图像
            photo = ImageTk.PhotoImage(preview_image)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            
            # 更新标尺
            self.update_rulers(preview_image.size, preview_width, preview_height)
            
        except Exception as e:
            print(f"更新预览失败: {str(e)}")
            
    def update_rulers(self, image_size, preview_width, preview_height):
        """更新标尺"""
        try:
            # 清除现有标尺
            self.h_ruler.delete('all')
            self.v_ruler.delete('all')
            
            # 获取当前纸张尺寸
            printer_name = self.printer_var.get()
            paper_name = self.paper_var.get()
            paper_width, paper_height = self.get_paper_dimensions(printer_name, paper_name)
            
            # 如果是横向，交换宽高
            if self.orientation_var.get() == "landscape":
                paper_width, paper_height = paper_height, paper_width
            
            # 确保预览尺寸有效
            if preview_width <= 0:
                preview_width = 1
            if preview_height <= 0:
                preview_height = 1
            
            # 计算缩放比例（考虑预留边距）
            margin = 10  # 预留10像素边距
            scale_x = (preview_width - 2 * margin) / paper_width
            scale_y = (preview_height - 2 * margin) / paper_height
            scale = min(scale_x, scale_y)
            
            # 计算预览区域中纸张的实际像素尺寸
            paper_pixel_width = int(paper_width * scale)
            paper_pixel_height = int(paper_height * scale)
            
            # 计算纸张在预览区域中的位置
            x_offset = margin
            y_offset = (preview_height - paper_pixel_height) // 2
            
            # 绘制标尺背景
            self.h_ruler.create_rectangle(0, 0, preview_width, 15, fill='white', outline='#E0E0E0')
            self.v_ruler.create_rectangle(0, 0, 15, preview_height, fill='white', outline='#E0E0E0')
            
            # 绘制页面范围背景
            self.h_ruler.create_rectangle(x_offset, 0, x_offset + paper_pixel_width, 15, 
                                        fill='#F5F5F5', outline='#E0E0E0')
            self.v_ruler.create_rectangle(0, y_offset, 15, y_offset + paper_pixel_height, 
                                        fill='#F5F5F5', outline='#E0E0E0')
            
            # 绘制水平标尺刻度
            for i in range(0, int(paper_width) + 1, 10):  # 每10毫米一个刻度
                x = x_offset + i * scale
                if i % 50 == 0:  # 每50毫米一个主刻度
                    # 绘制主刻度线
                    self.h_ruler.create_line(x, 4, x, 14, fill='#404040', width=1)
                    # 绘制刻度值
                    self.h_ruler.create_text(x, 2, text=str(i), anchor='n', 
                                           font=('Arial', 6), fill='#404040')
                elif i % 10 == 0:  # 每10毫米一个次刻度
                    self.h_ruler.create_line(x, 8, x, 14, fill='#808080')
            
            # 绘制垂直标尺刻度
            for i in range(0, int(paper_height) + 1, 10):
                y = y_offset + i * scale
                if i % 50 == 0:
                    # 绘制主刻度线
                    self.v_ruler.create_line(4, y, 14, y, fill='#404040', width=1)
                    # 绘制刻度值
                    self.v_ruler.create_text(2, y, text=str(i), anchor='w', 
                                           font=('Arial', 6), fill='#404040')
                elif i % 10 == 0:
                    self.v_ruler.create_line(8, y, 14, y, fill='#808080')
            
            # 绘制页面边界
            self.h_ruler.create_line(x_offset, 0, x_offset, 15, fill='#2196F3', width=2)
            self.h_ruler.create_line(x_offset + paper_pixel_width, 0, 
                                   x_offset + paper_pixel_width, 15, fill='#2196F3', width=2)
            
            self.v_ruler.create_line(0, y_offset, 15, y_offset, fill='#2196F3', width=2)
            self.v_ruler.create_line(0, y_offset + paper_pixel_height, 15,
                                   y_offset + paper_pixel_height, fill='#2196F3', width=2)
            
            # 显示单位（小字体）
            self.h_ruler.create_text(preview_width-4, 7, text='mm', anchor='e', 
                                   font=('Arial', 6), fill='#808080')
            self.v_ruler.create_text(7, preview_height-4, text='mm', anchor='s', 
                                   font=('Arial', 6), fill='#808080')
            
        except Exception as e:
            print(f"更新标尺失败: {str(e)}")

    def get_paper_dimensions(self, printer_name, paper_name):
        """获取纸张实际尺寸（毫米）"""
        try:
            # 创建打印机DC
            hdc = win32gui.CreateDC("WINSPOOL", printer_name, None)
            dc = win32ui.CreateDCFromHandle(hdc)
            
            try:
                # 获取设备分辨率
                dpi_x = dc.GetDeviceCaps(win32con.LOGPIXELSX)
                dpi_y = dc.GetDeviceCaps(win32con.LOGPIXELSY)
                
                # 打开打印机获取纸张ID
                printer = win32print.OpenPrinter(printer_name)
                try:
                    # 获取打印机信息
                    properties = win32print.GetPrinter(printer, 2)
                    dm = properties['pDevMode']
                    
                    # 获取纸张ID列表
                    papers = win32print.DeviceCapabilities(printer_name, "", 2)
                    paper_names = win32print.DeviceCapabilities(printer_name, "", 16)
                    
                    # 找到选中的纸张ID
                    paper_index = paper_names.index(paper_name)
                    paper_id = papers[paper_index]
                    
                    # 保存原始设置
                    original_size = dm.PaperSize
                    original_width = dm.PaperWidth
                    original_length = dm.PaperLength
                    
                    # 设置要查询的纸张
                    dm.PaperSize = paper_id
                    dm.PaperWidth = 0
                    dm.PaperLength = 0
                    
                    # 应用设置
                    dm_out = win32print.DocumentProperties(
                        0, printer, printer_name, dm, dm, 0)
                    
                    if dm_out >= 0:
                        # 使用新设置创建DC
                        new_hdc = win32gui.CreateDC("WINSPOOL", printer_name, dm)
                        new_dc = win32ui.CreateDCFromHandle(new_hdc)
                        try:
                            # 获取物理页面尺寸（像素）
                            width_pixels = new_dc.GetDeviceCaps(win32con.PHYSICALWIDTH)
                            height_pixels = new_dc.GetDeviceCaps(win32con.PHYSICALHEIGHT)
                            
                            # 转换为毫米
                            width_mm = width_pixels * 25.4 / dpi_x
                            height_mm = height_pixels * 25.4 / dpi_y
                            
                            if width_mm > 0 and height_mm > 0:
                                return width_mm, height_mm
                                
                        finally:
                            new_dc.DeleteDC()
                            
                    # 恢复原始设置
                    dm.PaperSize = original_size
                    dm.PaperWidth = original_width
                    dm.PaperLength = original_length
                    win32print.DocumentProperties(0, printer, printer_name, dm, dm, 0)
                    
                finally:
                    win32print.ClosePrinter(printer)
                    
            finally:
                dc.DeleteDC()
                
        except Exception as e:
            print(f"获取纸张尺寸失败: {str(e)}")
        
        # 如果获取失败，尝试使用标准尺寸
        paper_type = paper_name.split()[0]
        return self.paper_sizes_mm.get(paper_type, (210, 297))  # 默认A4

    def print_image(self):
        """打印图像"""
        try:
            # 获取打印参数
            printer_name = self.printer_var.get()
            copies = int(self.copies_var.get())
            
            # 检查是否是 PDF 打印机
            is_pdf_printer = "PDF" in printer_name.upper()
            
            if is_pdf_printer:
                # 创建文件保存对话框
                from tkinter import filedialog
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    title="保存PDF文件"
                )
                
                if filename:  # 如果用户选择了保存位置
                    # 准备图像
                    if isinstance(self.image, np.ndarray):
                        if len(self.image.shape) == 3 and self.image.shape[2] == 3:
                            image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                        pil_image = Image.fromarray(image)
                    elif isinstance(self.image, Image.Image):
                        pil_image = self.image
                    
                    # 获取原始图像尺寸并确定方向
                    img_width, img_height = pil_image.size
                    is_landscape = img_width > img_height
                    
                    # 根据方向和图像方向决定是否需要旋转
                    if (is_landscape and self.orientation_var.get() == "portrait") or \
                       (not is_landscape and self.orientation_var.get() == "landscape"):
                        pil_image = pil_image.rotate(90, expand=True)
                    
                    # 将图像转换为PDF
                    try:
                        # 创建临时JPG文件
                        temp_jpg = None
                        temp_jpg_name = None
                        
                        try:
                            temp_jpg = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                            temp_jpg_name = temp_jpg.name
                            temp_jpg.close()  # 关闭文件句柄
                            
                            # 保存为高质量JPG
                            pil_image.save(temp_jpg_name, "JPEG", quality=100, dpi=(300, 300))
                            
                            # 获取选择的纸张尺寸
                            paper_width, paper_height = self.get_paper_size(self.paper_var.get())
                            
                            # 确定页面方向
                            if self.orientation_var.get() == "landscape":
                                pagesize = (paper_height, paper_width)  # 交换宽高
                            else:
                                pagesize = (paper_width, paper_height)
                            
                            # 创建PDF文档
                            c = canvas.Canvas(filename, pagesize=pagesize)
                            
                            # 获取页面尺寸
                            page_width, page_height = pagesize
                            
                            # 读取图像
                            img = ImageReader(temp_jpg_name)
                            img_width, img_height = pil_image.size
                            
                            # 计算缩放比例和位置，使图像居中并适应页面（留出边距）
                            margin = 28.35  # 1厘米的边距 (28.35点 = 1厘米)
                            available_width = page_width - 2 * margin
                            available_height = page_height - 2 * margin
                            ratio = min(available_width/img_width, available_height/img_height)
                            new_width = img_width * ratio
                            new_height = img_height * ratio
                            x = (page_width - new_width) / 2
                            y = (page_height - new_height) / 2
                            
                            # 绘制图像
                            for _ in range(copies):
                                c.drawImage(img, x, y, width=new_width, height=new_height)
                                c.showPage()
                            
                            # 保存PDF
                            c.save()
                            
                        finally:
                            # 确保删除临时文件
                            if temp_jpg_name and os.path.exists(temp_jpg_name):
                                try:
                                    os.unlink(temp_jpg_name)
                                except:
                                    pass
                                    
                    except Exception as e:
                        messagebox.showerror("错误", f"生成PDF失败：{str(e)}")
                        return
                    
            else:
                # 对普通打印机使用GDI打印
                # 准备图像
                if isinstance(self.image, np.ndarray):
                    if len(self.image.shape) == 3 and self.image.shape[2] == 3:
                        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(image)
                elif isinstance(self.image, Image.Image):
                    pil_image = self.image
                
                # 获取原始图像尺寸并确定方向
                img_width, img_height = pil_image.size
                is_landscape = img_width > img_height
                
                # 根据方向和图像方向决定是否需要旋转
                if (is_landscape and self.orientation_var.get() == "portrait") or \
                   (not is_landscape and self.orientation_var.get() == "landscape"):
                    pil_image = pil_image.rotate(90, expand=True)
                
                # 获取打印机DC
                hprinter = win32print.OpenPrinter(printer_name)
                printer_info = win32print.GetPrinter(hprinter, 2)
                dev_mode = printer_info['pDevMode']
                
                # 获取当前选择的纸张ID
                papers = win32print.DeviceCapabilities(printer_name, "", 2)  # DC_PAPERS
                paper_names = win32print.DeviceCapabilities(printer_name, "", 16)  # DC_PAPERNAMES
                selected_paper = self.paper_var.get()
                
                # 找到选择的纸张ID并设置纸张
                try:
                    paper_index = paper_names.index(selected_paper)
                    paper_size = papers[paper_index]
                    
                    # 创建新的DEVMODE结构
                    dm = printer_info['pDevMode']
                    
                    # 设置纸张尺寸
                    dm.PaperSize = paper_size
                    dm.Orientation = 1 if self.orientation_var.get() == "portrait" else 2
                    
                    # 清除自定义纸张设置
                    dm.PaperLength = 0
                    dm.PaperWidth = 0
                    
                    # 设置打印区域为整个页面
                    dm.Fields |= 0x40000  # DM_PAPERSIZE
                    dm.Fields |= 0x100000  # DM_ORIENTATION
                    
                    # 使用DocumentProperties更新设置
                    dm_out = win32print.DocumentProperties(
                        self.dialog.winfo_id(),  # 父窗口句柄
                        hprinter,                # 打印机句柄
                        printer_name,            # 打印机名称
                        dm,                      # 输出缓冲区
                        dm,                      # 输入缓冲区
                        0                        # 只更新设置，不显示对话框
                    )
                    
                    if dm_out < 0:
                        raise Exception("更新打印机设置失败")
                        
                    printer_info['pDevMode'] = dm
                    
                except Exception as e:
                    print(f"设置纸张尺寸失败: {str(e)}")
                
                # 创建打印机DC
                hdc = win32gui.CreateDC("WINSPOOL", printer_name, printer_info['pDevMode'])
                dc = win32ui.CreateDCFromHandle(hdc)
                
                try:
                    # 开始文档打印
                    dc.StartDoc('Photo Print')
                    
                    # 循环打印指定份数
                    for _ in range(copies):
                        try:
                            # 开始页面
                            dc.StartPage()
                            
                            # 获取设备分辨率
                            dpi_x = dc.GetDeviceCaps(win32con.LOGPIXELSX)
                            dpi_y = dc.GetDeviceCaps(win32con.LOGPIXELSY)
                            
                            # 获取纸张实际尺寸（0.1mm）
                            paper_width = dev_mode.PaperWidth / 10  # 转换为毫米
                            paper_height = dev_mode.PaperLength / 10  # 转换为毫米
                            
                            # 如果尺寸为0，获取物理页面尺寸
                            if paper_width == 0 or paper_height == 0:
                                paper_width = dc.GetDeviceCaps(win32con.PHYSICALWIDTH) * 25.4 / dpi_x
                                paper_height = dc.GetDeviceCaps(win32con.PHYSICALHEIGHT) * 25.4 / dpi_y
                            
                            # 转换纸张尺寸为像素
                            width_pixels = int(paper_width * dpi_x / 25.4)
                            height_pixels = int(paper_height * dpi_y / 25.4)
                            
                            # 获取实际可打印区域
                            printable_width = dc.GetDeviceCaps(win32con.HORZRES)
                            printable_height = dc.GetDeviceCaps(win32con.VERTRES)
                            
                            # 计算边距
                            margin_x = (width_pixels - printable_width) // 2
                            margin_y = (height_pixels - printable_height) // 2
                            
                            # 调整图像大小以适应纸张（不考虑边距）
                            img_width, img_height = pil_image.size
                            ratio = min(width_pixels/img_width, height_pixels/img_height)
                            new_width = int(img_width * ratio)
                            new_height = int(img_height * ratio)
                            
                            # 计算居中位置（忽略打印机边距）
                            x = (width_pixels - new_width) // 2
                            y = (height_pixels - new_height) // 2
                            
                            # 调整图像大小
                            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                            
                            # 将PIL图像转换为Windows位图
                            dib = ImageWin.Dib(resized_image)
                            
                            # 在打印机DC上绘制图像（使用物理坐标）
                            dib.draw(dc.GetHandleOutput(), (x, y, x + new_width, y + new_height))
                            
                            # 结束页面
                            dc.EndPage()
                            
                        except Exception as e:
                            print(f"打印页面失败: {str(e)}")
                            continue
                            
                    # 结束文档
                    dc.EndDoc()
                    
                finally:
                    # 清理资源
                    dc.DeleteDC()
                    win32print.ClosePrinter(hprinter)
            
            # 关闭对话框
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"打印失败：{str(e)}")
            
    def center_window(self):
        """使窗口居中显示"""
        window_width = self.dialog.winfo_width()
        window_height = self.dialog.winfo_height()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f'+{x}+{y}') 

    def load_last_printer(self):
        """加载上次使用的打印机"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('last_printer', '')
        except:
            pass
        return ''

    def save_last_printer(self, printer_name):
        """保存当前使用的打印机"""
        try:
            config = {'last_printer': printer_name}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except:
            pass 

    def on_paper_changed(self, event=None):
        """纸张选择改变时的处理"""
        try:
            # 获取当前打印机和纸张
            printer_name = self.printer_var.get()
            selected_paper = self.paper_var.get()
            
            # 打开打印机
            printer = win32print.OpenPrinter(printer_name)
            try:
                # 获取打印机信息并更新纸张设置
                properties = win32print.GetPrinter(printer, 2)
                dm = properties['pDevMode']
                
                # 获取纸张ID列表
                papers = win32print.DeviceCapabilities(printer_name, "", 2)
                paper_names = win32print.DeviceCapabilities(printer_name, "", 16)
                
                # 设置选中的纸张
                paper_index = paper_names.index(selected_paper)
                dm.PaperSize = papers[paper_index]
                dm.PaperLength = 0
                dm.PaperWidth = 0
                
                # 更新设备模式
                properties['pDevMode'] = dm
                
            finally:
                win32print.ClosePrinter(printer)
                
            # 更新预览
            self.dialog.after(100, self.update_preview)
            
        except Exception as e:
            print(f"更新纸张设置失败: {str(e)}")
            
    def delayed_preview_update(self):
        """延迟更新预览"""
        try:
            # 重新获取打印机设置
            printer_name = self.printer_var.get()
            printer = win32print.OpenPrinter(printer_name)
            try:
                properties = win32print.GetPrinter(printer, 2)
                if properties['pDevMode'].PaperWidth == 0:
                    # 如果设置还未生效，继续等待
                    self.dialog.after(100, self.delayed_preview_update)
                else:
                    # 设置已生效，更新预览
                    self.update_preview()
            finally:
                win32print.ClosePrinter(printer)
        except Exception as e:
            print(f"延迟更新预览失败: {str(e)}") 

    def get_paper_size(self, paper_name):
        """获取纸张尺寸（单位：点，1点=1/72英寸）"""
        # 将毫米转换为点数（1英寸=72点=25.4毫米）
        def mm_to_points(mm):
            return mm * 72 / 25.4
            
        try:
            # 获取纸张尺寸（毫米）
            width_mm, height_mm = self.get_paper_dimensions(self.printer_var.get(), paper_name)
            
            # 转换为点数
            width_points = mm_to_points(width_mm)
            height_points = mm_to_points(height_mm)
            
            return (width_points, height_points)
            
        except Exception as e:
            print(f"获取纸张尺寸失败: {str(e)}")
            # 默认返回A4尺寸（595.28, 841.89）点
            return (595.28, 841.89) 