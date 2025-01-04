import tkinter as tk
from tkinter import ttk, messagebox
from .custom_size import CustomSizeDialog
import json

class SizeManagerDialog:
    def __init__(self, parent, callback=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("尺寸管理")
        self.dialog.geometry("600x400")
        
        self.callback = callback
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
        """设置对话框UI"""
        # 创建标签页
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 纸张尺寸标签页
        paper_frame = ttk.Frame(notebook)
        notebook.add(paper_frame, text="纸张尺寸")
        self.setup_paper_frame(paper_frame)
        
        # 证件照尺寸标签页
        photo_frame = ttk.Frame(notebook)
        notebook.add(photo_frame, text="证件照尺寸")
        self.setup_photo_frame(photo_frame)
        
    def setup_paper_frame(self, parent):
        """设置纸张尺寸标签页"""
        # 工具栏
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="添加", command=self.add_paper_size).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="编辑", command=self.edit_paper_size).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="删除", command=self.delete_paper_size).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="上移", command=lambda: self.move_item(self.paper_tree, "up")).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="下移", command=lambda: self.move_item(self.paper_tree, "down")).pack(side=tk.LEFT, padx=5)
        
        # 尺寸列表
        self.paper_tree = ttk.Treeview(
            parent,
            columns=("name", "width", "height"),
            show="headings"
        )
        self.paper_tree.heading("name", text="名称")
        self.paper_tree.heading("width", text="宽度(mm)")
        self.paper_tree.heading("height", text="高度(mm)")
        self.paper_tree.pack(fill=tk.BOTH, expand=True)
        
        # 加载数据
        self.load_paper_sizes()
        
    def setup_photo_frame(self, parent):
        """设置证件照尺寸标签页"""
        # 工具栏
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="添加", command=self.add_photo_size).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="编辑", command=self.edit_photo_size).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="删除", command=self.delete_photo_size).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="上移", command=lambda: self.move_item(self.photo_tree, "up")).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="下移", command=lambda: self.move_item(self.photo_tree, "down")).pack(side=tk.LEFT, padx=5)
        
        # 尺寸列表
        self.photo_tree = ttk.Treeview(
            parent,
            columns=("name", "width", "height"),
            show="headings"
        )
        self.photo_tree.heading("name", text="名称")
        self.photo_tree.heading("width", text="宽度(mm)")
        self.photo_tree.heading("height", text="高度(mm)")
        self.photo_tree.pack(fill=tk.BOTH, expand=True)
        
        # 加载数据
        self.load_photo_sizes()
        
    def move_item(self, tree, direction):
        """移动选中项"""
        selected = tree.selection()
        if not selected:
            return
            
        item = selected[0]
        items = tree.get_children()
        index = items.index(item)
        
        if direction == "up" and index > 0:
            # 获取所有项的值
            values = []
            for i in items:
                values.append(tree.item(i)['values'])
            
            # 交换位置
            values[index], values[index-1] = values[index-1], values[index]
            
            # 更新显示
            for i, value in enumerate(values):
                tree.item(items[i], values=value)
            
            # 更新选中项
            tree.selection_set(items[index-1])
            
            # 保存更新后的顺序
            self.save_sizes(tree)
            
        elif direction == "down" and index < len(items) - 1:
            # 获取所有项的值
            values = []
            for i in items:
                values.append(tree.item(i)['values'])
            
            # 交换位置
            values[index], values[index+1] = values[index+1], values[index]
            
            # 更新显示
            for i, value in enumerate(values):
                tree.item(items[i], values=value)
            
            # 更新选中项
            tree.selection_set(items[index+1])
            
            # 保存更新后的顺序
            self.save_sizes(tree)
            
    def save_sizes(self, tree):
        """保存排序后的尺寸"""
        sizes = {}
        for item in tree.get_children():
            name, width, height = tree.item(item)['values']
            sizes[name] = [width, height]
            
        filename = 'paper_sizes.json' if tree == self.paper_tree else 'photo_sizes.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sizes, f, ensure_ascii=False, indent=4)
            
        # 回调通知
        if self.callback:
            self.callback()

    def load_paper_sizes(self):
        """加载纸张尺寸数据"""
        try:
            with open('paper_sizes.json', 'r', encoding='utf-8') as f:
                sizes = json.load(f)
                # 清空现有数据
                for item in self.paper_tree.get_children():
                    self.paper_tree.delete(item)
                # 添加新数据
                for name, size in sizes.items():
                    self.paper_tree.insert('', 'end', values=(name, size[0], size[1]))
        except:
            pass

    def load_photo_sizes(self):
        """加载证件照尺寸数据"""
        try:
            with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                sizes = json.load(f)
                # 清空现有数据
                for item in self.photo_tree.get_children():
                    self.photo_tree.delete(item)
                # 添加新数据
                for name, size in sizes.items():
                    self.photo_tree.insert('', 'end', values=(name, size[0], size[1]))
        except:
            pass

    def add_paper_size(self):
        """添加纸张尺寸"""
        dialog = CustomSizeDialog(self.dialog, "添加纸张尺寸")
        if dialog.result:
            name, width, height = dialog.result
            # 检查是否已存在
            try:
                with open('paper_sizes.json', 'r', encoding='utf-8') as f:
                    sizes = json.load(f)
            except:
                sizes = {}
            
            if name in sizes:
                messagebox.showerror("错误", "该尺寸名称已存在")
                return
            
            # 添加新尺寸
            sizes[name] = [int(width), int(height)]
            with open('paper_sizes.json', 'w', encoding='utf-8') as f:
                json.dump(sizes, f, ensure_ascii=False, indent=4)
            
            # 刷新列表
            self.load_paper_sizes()
            # 回调通知
            if self.callback:
                self.callback()

    def add_photo_size(self):
        """添加证件照尺寸"""
        dialog = CustomSizeDialog(self.dialog, "添加证件照尺寸")
        if dialog.result:
            name, width, height = dialog.result
            # 检查是否已存在
            try:
                with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                    sizes = json.load(f)
            except:
                sizes = {}
            
            if name in sizes:
                messagebox.showerror("错误", "该尺寸名称已存在")
                return
            
            # 添加新尺寸
            sizes[name] = [int(width), int(height)]
            with open('photo_sizes.json', 'w', encoding='utf-8') as f:
                json.dump(sizes, f, ensure_ascii=False, indent=4)
            
            # 刷新列表
            self.load_photo_sizes()
            # 回调通知
            if self.callback:
                self.callback()

    def edit_paper_size(self):
        """编辑纸张尺寸"""
        selected = self.paper_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的尺寸")
            return
        
        # 获取选中项的值
        item = self.paper_tree.item(selected[0])
        old_name = item['values'][0]
        old_width = item['values'][1]
        old_height = item['values'][2]
        
        # 打开编辑对话框
        dialog = CustomSizeDialog(
            self.dialog,
            "编辑纸张尺寸",
            default_name=old_name,
            default_width=str(old_width),
            default_height=str(old_height)
        )
        
        if dialog.result:
            name, width, height = dialog.result
            # 加载现有尺寸
            try:
                with open('paper_sizes.json', 'r', encoding='utf-8') as f:
                    sizes = json.load(f)
            except:
                sizes = {}
            
            # 如果名称改变，检查新名称是否已存在
            if name != old_name and name in sizes:
                messagebox.showerror("错误", "该尺寸名称已存在")
                return
            
            # 更新尺寸
            if old_name in sizes:
                del sizes[old_name]
            sizes[name] = [int(width), int(height)]
            
            # 保存更新
            with open('paper_sizes.json', 'w', encoding='utf-8') as f:
                json.dump(sizes, f, ensure_ascii=False, indent=4)
            
            # 刷新列表
            self.load_paper_sizes()
            # 回调通知
            if self.callback:
                self.callback()

    def edit_photo_size(self):
        """编辑证件照尺寸"""
        selected = self.photo_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的尺寸")
            return
        
        # 获取选中项的值
        item = self.photo_tree.item(selected[0])
        old_name = item['values'][0]
        old_width = item['values'][1]
        old_height = item['values'][2]
        
        # 打开编辑对话框
        dialog = CustomSizeDialog(
            self.dialog,
            "编辑证件照尺寸",
            default_name=old_name,
            default_width=str(old_width),
            default_height=str(old_height)
        )
        
        if dialog.result:
            name, width, height = dialog.result
            # 加载现有尺寸
            try:
                with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                    sizes = json.load(f)
            except:
                sizes = {}
            
            # 如果名称改变，检查新名称是否已存在
            if name != old_name and name in sizes:
                messagebox.showerror("错误", "该尺寸名称已存在")
                return
            
            # 更新尺寸
            if old_name in sizes:
                del sizes[old_name]
            sizes[name] = [int(width), int(height)]
            
            # 保存更新
            with open('photo_sizes.json', 'w', encoding='utf-8') as f:
                json.dump(sizes, f, ensure_ascii=False, indent=4)
            
            # 刷新列表
            self.load_photo_sizes()
            # 回调通知
            if self.callback:
                self.callback()

    def delete_paper_size(self):
        """删除纸张尺寸"""
        selected = self.paper_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的尺寸")
            return
        
        if not messagebox.askyesno("确认", "确定要删除选中的尺寸吗？"):
            return
        
        # 获取选中项的名称
        item = self.paper_tree.item(selected[0])
        name = item['values'][0]
        
        # 加载现有尺寸
        try:
            with open('paper_sizes.json', 'r', encoding='utf-8') as f:
                sizes = json.load(f)
        except:
            sizes = {}
        
        # 删除尺寸
        if name in sizes:
            del sizes[name]
            
            # 保存更新
            with open('paper_sizes.json', 'w', encoding='utf-8') as f:
                json.dump(sizes, f, ensure_ascii=False, indent=4)
            
            # 刷新列表
            self.load_paper_sizes()
            # 回调通知
            if self.callback:
                self.callback()

    def delete_photo_size(self):
        """删除证件照尺寸"""
        selected = self.photo_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的尺寸")
            return
        
        if not messagebox.askyesno("确认", "确定要删除选中的尺寸吗？"):
            return
        
        # 获取选中项的名称
        item = self.photo_tree.item(selected[0])
        name = item['values'][0]
        
        # 加载现有尺寸
        try:
            with open('photo_sizes.json', 'r', encoding='utf-8') as f:
                sizes = json.load(f)
        except:
            sizes = {}
        
        # 删除尺寸
        if name in sizes:
            del sizes[name]
            
            # 保存更新
            with open('photo_sizes.json', 'w', encoding='utf-8') as f:
                json.dump(sizes, f, ensure_ascii=False, indent=4)
            
            # 刷新列表
            self.load_photo_sizes()
            # 回调通知
            if self.callback:
                self.callback()