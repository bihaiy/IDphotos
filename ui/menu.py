import tkinter as tk
from tkinter import messagebox

class MenuManager:
    def __init__(self, app):
        self.app = app
        self.setup_menu()
        
    def setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.app.window)
        self.app.window.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开", command=self.app.image_processor.upload_image)
        file_menu.add_command(label="关闭", command=self.app.image_processor.clear_upload)
        file_menu.add_separator()
        file_menu.add_command(label="保存透明照片", command=lambda: self.app.image_processor.download_image('transparent'))
        file_menu.add_command(label="保存单张换底照片", command=lambda: self.app.image_processor.download_image('colored'))
        file_menu.add_command(label="保存排版照片", command=lambda: self.app.image_processor.download_image('layout'))
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.app.window.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="上传文件左转", command=lambda: self.app.image_processor.rotate_image('left'))
        edit_menu.add_command(label="上传文件右转", command=lambda: self.app.image_processor.rotate_image('right'))
        edit_menu.add_separator()
        edit_menu.add_command(label="抠图", command=self.app.image_processor.process_matting)
        edit_menu.add_command(label="换背景", command=self.app.image_processor.process_background)
        edit_menu.add_command(label="证照排版", command=self.app.image_processor.process_layout)
        edit_menu.add_separator()
        edit_menu.add_command(label="一键制作证件照", command=self.app.image_processor.process_photo)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="尺寸管理", command=self.app.params_manager.manage_sizes)
        tools_menu.add_command(label="API设置", command=self.show_api_settings)
        
        # 关于菜单
        menubar.add_command(label="关于", command=self.show_about)
        
        # 保���菜单引用
        self.file_menu = file_menu
        self.edit_menu = edit_menu
        self.tools_menu = tools_menu
        
    def update_menu_state(self):
        """更新菜单项状态"""
        # 检查是否有上传的照片
        has_upload = hasattr(self.app, 'current_image')
        # 检查是否有透明照片
        has_transparent = hasattr(self.app, 'transparent_image')
        # 检查是否有背景色照片
        has_colored = hasattr(self.app, 'processed_image')
        # 检查是否有排版照片
        has_layout = hasattr(self.app, 'layout_image')
        
        # 更新文件菜单
        self.file_menu.entryconfig("关闭", state="normal" if has_upload else "disabled")
        self.file_menu.entryconfig("保存透明照片", state="normal" if has_transparent else "disabled")
        self.file_menu.entryconfig("保存单张换底照片", state="normal" if has_colored else "disabled")
        self.file_menu.entryconfig("保存排版照片", state="normal" if has_layout else "disabled")
        
        # 更新编辑菜单
        self.edit_menu.entryconfig("上传文件左转", state="normal" if has_upload else "disabled")
        self.edit_menu.entryconfig("上传文件右转", state="normal" if has_upload else "disabled")
        self.edit_menu.entryconfig("抠图", state="normal" if has_upload else "disabled")
        self.edit_menu.entryconfig("换背景", state="normal" if has_transparent else "disabled")
        self.edit_menu.entryconfig("证照排版", state="normal" if has_colored else "disabled")
        self.edit_menu.entryconfig("一键制作证件照", state="normal" if has_upload else "disabled")
        
    def show_api_settings(self):
        """显示API设置对话框"""
        from dialogs.api_setting import APISettingDialog
        APISettingDialog(self.app.window)
        
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "证件照制作系统 v1.0\n\n"
            "本系统支持：\n"
            "- 智能抠图\n"
            "- 智能美颜\n"
            "- 换背景\n"
            "- 证照排版\n"
            "- 一键制作\n\n"
            "© 2024 All Rights Reserved"
        ) 