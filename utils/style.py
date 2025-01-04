from tkinter import ttk

def setup_styles():
    """设置全局样式"""
    style = ttk.Style()
    
    # 主要按钮样式
    style.configure(
        'Primary.TButton',
        padding=10,
        font=('TkDefaultFont', 10)
    )
    
    # 上传按钮样式
    style.configure(
        'Upload.TButton',
        padding=20,
        font=('TkDefaultFont', 12)
    ) 
    
    # 关闭按钮样式
    style.configure(
        'Close.TButton',
        padding=2,
        width=3,
        font=('TkDefaultFont', 8)
    )
    
    # 工具按钮样式
    style.configure(
        'Tool.TButton',
        padding=2,
        width=3,
        font=('TkDefaultFont', 8)
    )
    
    # 高亮按钮样式（红色大字）
    style.configure(
        'Highlight.TButton',
        padding=15,
        font=('TkDefaultFont', 12, 'bold'),
        foreground='#ff0000'  # 红色文字
    )
    
    # 透明照片标签样式
    style.configure(
        'Transparent.TLabel',
        relief='solid',  # 实线边框
        borderwidth=1    # 边框宽度
    )
    
    # 选中照片的标签样式
    style.configure(
        'Selected.TLabel',
        relief='solid',  # 实线边框
        borderwidth=2    # 边框宽度
    )
    
    # 上传图标按钮样式（修改）
    style.configure(
        'IconUpload.TButton',
        padding=2,
        width=3,
        font=('TkDefaultFont', 12, 'bold'),
        foreground='#40a9ff'  # 使用更柔和的蓝色
    )
    
    # 鼠标悬停时的样式
    style.map(
        'IconUpload.TButton',
        foreground=[('active', '#1890ff')]  # 悬停时使用深蓝色
    )
    
    # 编辑器滑动条样式
    style.configure(
        'Editor.Horizontal.TScale',
        sliderthickness=16,     # 滑块更大
        troughcolor='#f0f0f0',  # 轨道颜色
        background='#ffffff',    # 背景色
        borderwidth=0           # 无边框
    )
    
    # 滑动条标签样式
    style.configure(
        'SliderLabel.TLabel',
        font=('TkDefaultFont', 9),
        foreground='#333333',
        padding=(0, 0, 0, 2)    # 底部间距
    )
    
    # 刻度标签样式
    style.configure(
        'Scale.TLabel',
        font=('TkDefaultFont', 8),
        foreground='#666666'
    )
    
    # 数值标签样式
    style.configure(
        'Value.TLabel',
        font=('TkDefaultFont', 9, 'bold'),  # 加粗
        foreground='#1890ff'    # 使用主题蓝色
    )
    
    # 重置按钮样式
    style.configure(
        'Reset.TButton',
        padding=0,
        font=('TkDefaultFont', 8),
        width=2,
        foreground='#666666'
    )
    
    # 鼠标悬停时的样式
    style.map(
        'Reset.TButton',
        foreground=[('active', '#1890ff')],
        background=[('active', '#f0f0f0')]
    )
    
    # 工具栏按钮样式
    style.configure(
        'Toolbar.TButton',
        padding=(10, 5),
        width=8,
        justify='center',
        font=('TkDefaultFont', 9)
    )
    
    # 浮动参数面板样式
    style.configure(
        'Popup.TFrame',
        background='#ffffff',
        relief='solid',
        borderwidth=1
    )
    
    # 参数面板内部样式
    style.configure(
        'Panel.TFrame',
        background='#ffffff',
        relief='flat'
    )
    
    # 参数面板标签样式
    style.configure(
        'Panel.TLabel',
        background='#ffffff',
        foreground='#333333'
    )
    
    # 参数面板按钮样式
    style.configure(
        'Panel.TButton',
        background='#ffffff',
        padding=3
    )
    
    # 小按钮样式
    style.configure(
        'Small.TButton',
        padding=2,
        width=4,
        font=('TkDefaultFont', 8)
    )
    
    # 恢复按钮样式
    style.configure(
        'Restore.TButton',
        padding=2,
        width=2,
        font=('TkDefaultFont', 12),  # 使用更大的字体
        foreground='#666666',  # 使用灰色
        background='#ffffff'   # 白色背景
    )
    
    # 鼠标悬停时的样式
    style.map(
        'Restore.TButton',
        foreground=[('active', '#1890ff')],  # 悬停时变蓝
        background=[('active', '#ffffff')]
    )