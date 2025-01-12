import tkinter as tk
from tkinter import ttk, messagebox
import json
from dialogs.layout_editor import LayoutEditorDialog

class LayoutParams:
    def __init__(self, app, parent_notebook):
        self.app = app
        self.setup_layout_params(parent_notebook)
        
    def setup_layout_params(self, parent_notebook):
        """设置排版参数标签页"""
        layout_frame = ttk.Frame(parent_notebook, padding=10)
        parent_notebook.add(layout_frame, text="排版参数")
        
        # 排版样式列表
        styles_frame = ttk.LabelFrame(layout_frame, text="排版样式", padding=5)
        styles_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建列表框和滚动条
        list_container = ttk.Frame(styles_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建排序按钮容器
        sort_frame = ttk.Frame(list_container)
        sort_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 上移按钮
        ttk.Button(
            sort_frame,
            text="↑",
            width=2,
            command=lambda: self.move_style("up")
        ).pack(side=tk.TOP, pady=1)
        
        # 下移按钮
        ttk.Button(
            sort_frame,
            text="↓",
            width=2,
            command=lambda: self.move_style("down")
        ).pack(side=tk.TOP, pady=1)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.styles_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            height=10
        )
        self.styles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.styles_listbox.yview)
        
        # 按钮容器
        btn_frame = ttk.Frame(styles_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # 添加、编辑和删除按钮
        ttk.Button(
            btn_frame,
            text="添加自定义排版",
            command=self.add_custom_layout,
            width=15  # 设置固定宽度
        ).pack(side=tk.LEFT, expand=True, padx=2)
        
        ttk.Button(
            btn_frame,
            text="编辑",
            command=self.edit_layout,
            width=8  # 设置固定宽度
        ).pack(side=tk.LEFT, expand=True, padx=2)
        
        ttk.Button(
            btn_frame,
            text="删除",
            command=self.delete_layout,
            width=8  # 设置固定宽度
        ).pack(side=tk.LEFT, expand=True, padx=2)
        
        # 选项容器
        options_frame = ttk.Frame(layout_frame)
        options_frame.pack(fill=tk.X)
        
        # 显示选项
        self.show_gridlines_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="显示参考线",
            variable=self.show_gridlines_var,
            command=self.update_layout
        ).pack(side=tk.LEFT, expand=True)
        
        self.show_divider_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="照片间用灰线隔开",
            variable=self.show_divider_var,
            command=self.update_layout
        ).pack(side=tk.LEFT, expand=True)
        
        # 加载排版样式
        self.load_layout_styles()
        
        # 绑定选择事件
        self.styles_listbox.bind('<<ListboxSelect>>', self.on_style_select)
        
    def load_layout_styles(self):
        """加载排版样式"""
        try:
            with open('layout_styles.json', 'r', encoding='utf-8') as f:
                self.styles = json.load(f)
                
            # 清空列表
            self.styles_listbox.delete(0, tk.END)
            
            # 添加样式名称
            for name in self.styles.keys():
                self.styles_listbox.insert(tk.END, name)
                
            # 自动选择第一个样式
            if self.styles_listbox.size() > 0:
                self.styles_listbox.selection_set(0)
                self.on_style_select(None)  # 触发选择事件
                
        except FileNotFoundError:
            self.styles = {}
            
    def add_custom_layout(self):
        """添加自定义排版"""
        LayoutEditorDialog(self.app.window, self.on_style_added)
        
    def on_style_added(self):
        """排版样式添加后的回调"""
        # 保存当前选中的样式名称
        current_selection = self.styles_listbox.curselection()
        current_name = self.styles_listbox.get(current_selection[0]) if current_selection else None
        
        # 重新加载样式列表
        self.load_layout_styles()
        
        # 如果是编辑模式，选中原来的样式
        if current_name:
            items = self.styles_listbox.get(0, tk.END)
            if current_name in items:
                index = items.index(current_name)
                self.styles_listbox.selection_clear(0, tk.END)
                self.styles_listbox.selection_set(index)
                self.styles_listbox.see(index)  # 确保选中项可见
                self.on_style_select(None)
        # 如果是新增模式，选中最后一个样式
        else:
            last_index = self.styles_listbox.size() - 1
            if last_index >= 0:
                self.styles_listbox.selection_clear(0, tk.END)
                self.styles_listbox.selection_set(last_index)
                self.styles_listbox.see(last_index)  # 确保选中项可见
                self.on_style_select(None)
        
    def delete_layout(self):
        """删除排版样式"""
        selection = self.styles_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的排版样式")
            return
            
        name = self.styles_listbox.get(selection[0])
        if messagebox.askyesno("确认", f"确定要删除排版样式 '{name}' 吗?"):
            # 从字典和文件中删除
            del self.styles[name]
            with open('layout_styles.json', 'w', encoding='utf-8') as f:
                json.dump(self.styles, f, ensure_ascii=False, indent=4)
                
            # 从列表框中删除
            self.styles_listbox.delete(selection[0])
            
    def on_style_select(self, event):
        """排版样式选择改变时的处理"""
        selection = self.styles_listbox.curselection()
        if selection:
            name = self.styles_listbox.get(selection[0])
            style = self.styles[name]
            
            # 更新显示选项
            self.show_gridlines_var.set(style.get('show_gridlines', True))
            self.show_divider_var.set(style.get('show_divider', True))
            
            # 更新排版
            self.update_layout()
            
    def update_layout(self, *args):
        """更新排版"""
        selection = self.styles_listbox.curselection()
        if selection and hasattr(self.app, 'processed_images'):
            name = self.styles_listbox.get(selection[0])
            style = self.styles[name]
            
            # 更新样式的显示选项
            style['show_gridlines'] = self.show_gridlines_var.get()
            style['show_divider'] = self.show_divider_var.get()
            
            # 执行排版
            self.app.image_processor.process_layout()
        
    def update_photo_settings(self):
        """更新照片设置"""
        # 检查是否有选中的排版样式
        selection = self.styles_listbox.curselection()
        if selection:
            name = self.styles_listbox.get(selection[0])
            style = self.styles[name]
            
            # 更新显示选项
            self.show_gridlines_var.set(style.get('show_gridlines', True))
            self.show_divider_var.set(style.get('show_divider', True))
            
            # 更新排版
            self.update_layout()
        
    def edit_layout(self):
        """编辑排版样式"""
        selection = self.styles_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要编辑的排版样式")
            return
            
        name = self.styles_listbox.get(selection[0])
        style = self.styles[name]
        
        # 打开编辑对话框，传入当前样式数据
        LayoutEditorDialog(
            self.app.window,
            self.on_style_added,
            edit_style=style  # 传入要编辑的样式数据
        )
        
    def move_style(self, direction):
        """移动排版样式"""
        selection = self.styles_listbox.curselection()
        if not selection:
            return
            
        current_index = selection[0]
        if direction == "up" and current_index > 0:
            self._swap_styles(current_index, current_index - 1)
        elif direction == "down" and current_index < self.styles_listbox.size() - 1:
            self._swap_styles(current_index, current_index + 1)
            
    def _swap_styles(self, index1, index2):
        """交换两个样式的位置"""
        # 获取样式名称
        name1 = self.styles_listbox.get(index1)
        name2 = self.styles_listbox.get(index2)
        
        # 交换列表框中的位置
        self.styles_listbox.delete(index1)
        self.styles_listbox.insert(index1, name2)
        self.styles_listbox.delete(index2)
        self.styles_listbox.insert(index2, name1)
        
        # 更新选中项 - 始终跟随移动的项目
        self.styles_listbox.selection_clear(0, tk.END)
        self.styles_listbox.selection_set(index2)  # 选择目标位置
        self.styles_listbox.see(index2)  # 确保选中项可见
        
        # 重新排序样式字典
        styles_list = list(self.styles_listbox.get(0, tk.END))
        sorted_styles = {name: self.styles[name] for name in styles_list}
        
        # 保存排序后的样式
        self.styles = sorted_styles
        with open('layout_styles.json', 'w', encoding='utf-8') as f:
            json.dump(self.styles, f, ensure_ascii=False, indent=4)
        
        # 触发选择事件以更新显示
        self.on_style_select(None)
        
    def setup_buttons(self):
        """设置按钮"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 排版按钮
        ttk.Button(
            button_frame,
            text="证照排版",
            command=self.app.image_processor.process_layout
        ).pack(side=tk.LEFT, padx=5)
        
        # 管理尺寸按钮
        ttk.Button(
            button_frame,
            text="尺寸管理",
            command=self.app.params_manager.manage_sizes
        ).pack(side=tk.LEFT, padx=5)
        
        # 不在这里创建打印按钮，而是使用ParamsManager中的打印按钮
        
    def update_photos(self):
        """更新照片后刷新排版"""
        if hasattr(self.app, 'layout_image'):
            self.update_layout()