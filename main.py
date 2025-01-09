import os
import sys

import tkinter as tk
from tkinter import ttk
from ui.preview import PreviewManager
from ui.params import ParamsManager
from ui.menu import MenuManager
from processors.image_processor import ImageProcessor
from utils.style import setup_styles
from config.default_sizes import init_config_files
from dialogs.print_dialog import PrintDialog
from tkinter import messagebox


class IDPhotoProcessor:
    def __init__(self):
        try:
            self.window = tk.Tk()
            self.setup_window()
            self.setup_variables()
            
            # 创建主框架
            main_frame = ttk.Frame(self.window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建左右分栏
            self.left_frame = ttk.Frame(main_frame)
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            self.right_frame = ttk.Frame(main_frame, width=300)
            self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
            self.right_frame.pack_propagate(False)  # 防止右侧面板被压缩
            
            # 创建参数标签页
            self.params_notebook = ttk.Notebook(self.right_frame)
            self.params_notebook.pack(fill=tk.BOTH, expand=True)
            
            # 创建参数管理器（确保在创建其他组件之后）
            self.params_manager = ParamsManager(self)
            
            # 创建图像处理器
            self.image_processor = ImageProcessor(self)
            
            # 创建预览管理器
            self.preview_manager = PreviewManager(self)
            self.menu_manager = MenuManager(self)
            
            # 创建底部按钮区域
            bottom_frame = ttk.Frame(self.right_frame, padding=(0, 10, 0, 0))
            bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
            
            # 创建功能按钮行
            button_row = ttk.Frame(bottom_frame)
            button_row.pack(fill=tk.X, pady=(0, 5))
            
            # 功能按钮（一行三个）
            ttk.Button(
                button_row,
                text="抠图",
                command=lambda: self.image_processor.process_matting(),
                style='Primary.TButton'
            ).pack(side=tk.LEFT, expand=True, padx=2)
            
            ttk.Button(
                button_row,
                text="换背景",
                command=lambda: self.image_processor.process_background(),
                style='Primary.TButton'
            ).pack(side=tk.LEFT, expand=True, padx=2)
            
            ttk.Button(
                button_row,
                text="证照排版",
                command=lambda: self.image_processor.process_layout(),
                style='Primary.TButton'
            ).pack(side=tk.LEFT, expand=True, padx=2)
            
            # 一键制作按钮（红色大字）
            ttk.Button(
                bottom_frame,
                text="一键制作证件照",
                command=lambda: self.image_processor.process_photo(),
                style='Highlight.TButton'
            ).pack(fill=tk.X, pady=(0, 5))
            
            # 打印按钮
            ttk.Button(
                bottom_frame,
                text="打印证件照",
                command=lambda: PrintDialog(self.window, self.layout_image) if hasattr(self, 'layout_image') else messagebox.showwarning("提示", "请先生成排版照片"),
                style='Primary.TButton'
            ).pack(fill=tk.X, pady=(0, 5))
            
        except Exception as e:
            import traceback
            print(f"初始化失败: {str(e)}")
            print(traceback.format_exc())
            raise
        
    def setup_window(self):
        """设置窗口基本属性"""
        self.window.title("证件照制作系统")
        # self.window.geometry("1280x800")  # 移除固定尺寸设置
        self.window.minsize(1024, 768)     # 保持最小尺寸限制
        self.window.configure(bg='#f0f2f5')
        
        # 设置样式
        setup_styles()
        
        # 窗口最大化
        self.window.state('zoomed')  # Windows系统使用 'zoomed'
        
        # 使窗口居中显示（仅在非最大化时生效）
        self.center_window()
        
    def center_window(self):
        """使主窗口在屏幕中居中显示"""
        # 更新窗口大小信息
        self.window.update_idletasks()
        
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 获取窗口尺寸
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置
        self.window.geometry(f"+{x}+{y}")
        
    def setup_variables(self):
        """初始化变量"""
        # 抠图参数
        self.ratio_value = tk.StringVar(value="0.20")  # 面部比例，保留2位小数
        self.top_value = tk.StringVar(value="0.12")    # 头至顶距离，保留2位小数
        
        # 美颜参数
        self.brightness_var = tk.IntVar(value=0)  # 亮度
        self.contrast_var = tk.IntVar(value=0)    # 对比度
        self.sharpen_var = tk.IntVar(value=0)     # 锐化
        self.saturation_var = tk.IntVar(value=0)  # 饱和度
        
        # 其他参数
        self.align_var = tk.BooleanVar(value=False)  # 人脸矫正
        self.hd_var = tk.BooleanVar(value=False)     # 高清输出
        self.show_gridlines_var = tk.BooleanVar(value=True)  # 显示参考线
        
    def run(self):
        """运行程序"""
        self.window.mainloop()


def init_directories():
    """初始化必要的目录"""
    directories = [
        'config',
        'dialogs',
        'processors',
        'ui',
        'utils'
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            # 创建__init__.py文件
            with open(os.path.join(directory, '__init__.py'), 'w') as f:
                pass


if __name__ == "__main__":
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    
    # 初始化目录和包文件
    init_directories()
    
    # 初始化配置文件
    init_config_files()
    
    # 启动应用
    app = IDPhotoProcessor()
    app.run() 