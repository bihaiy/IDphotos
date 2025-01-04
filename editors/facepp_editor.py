import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
import cv2
import numpy as np
import base64
from utils.image_utils import resize_image_to_kb_base64
from editors.base_editor import BaseEditor

class FacePPEditor(BaseEditor):
    def __init__(self, parent):
        super().__init__(parent)
        self.load_api_config()
        
        # 修正滤镜列表，完全按照文档
        self.filters = {
            "无滤镜": "none",
            "黑白": "black_white",
            "平静": "calm",
            "晴天": "sunny",
            "旅程": "trip",
            "美肤": "beautify",
            "王家卫": "wangjiawei",
            "唯美": "cutie",
            "可人儿": "macaron",
            "纽约": "new_york",
            "樱花": "sakura",
            "十七岁": "17_years_old",
            "柔光灯": "clight",
            "下午茶": "tea_time",
            "亮肤": "whiten",
            "卓别林": "chaplin",
            "花香": "flowers",
            "回忆": "memory",
            "冰美人": "ice_lady",
            "巴黎": "paris",
            "时光": "times",
            "LOMO": "lomo",
            "旧时光": "old_times",
            "早春": "spring",
            "故事": "story",
            "阿宝色": "abao",
            "补光灯": "wlight",
            "暖暖": "warm",
            "绚烂": "glitter",
            "薰衣草": "lavender",
            "香奈儿": "chanel",
            "布拉格": "prague",
            "旧梦": "old_dream",
            "桃花": "blossom",
            "粉黛": "pink",
            "江南": "jiang_nan"
        }
        
    def setup_variables(self):
        """初始化变量"""
        self.whitening_var = tk.IntVar(value=0)     # 美白 0-100，默认0
        self.smoothing_var = tk.IntVar(value=0)     # 磨皮 0-100，默认0
        self.thinface_var = tk.IntVar(value=0)      # 瘦脸 0-100，默认0
        self.shrink_face_var = tk.IntVar(value=0)   # 小脸 0-100，默认0
        self.enlarge_eye_var = tk.IntVar(value=0)   # 大眼 0-100，默认0
        self.remove_eyebrow_var = tk.IntVar(value=0) # 去眉毛 0-100，默认0
        self.filter_var = tk.StringVar(value="无滤镜") # 滤镜
        
    def load_api_config(self):
        """加载API配置"""
        try:
            with open('api_config.json', 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key', '')
                self.api_secret = config.get('api_secret', '')
        except:
            self.api_key = ''
            self.api_secret = ''
            
    def create_widgets(self, notebook):
        """创建编辑器控件"""
        facepp_frame = ttk.Frame(notebook, padding=5)
        notebook.add(facepp_frame, text="Face++美颜")
        
        # API状态
        status_frame = ttk.Frame(facepp_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        if self.api_key and self.api_secret:
            ttk.Label(
                status_frame,
                text="Face++ API 已配置",
                foreground="green"
            ).pack(side=tk.LEFT)
        else:
            ttk.Label(
                status_frame,
                text="Face++ API 未配置",
                foreground="red"
            ).pack(side=tk.LEFT)
            
        ttk.Button(
            status_frame,
            text="设置API",
            command=self.setup_api
        ).pack(side=tk.RIGHT)
        
        # 滤镜选择
        filter_frame = ttk.LabelFrame(facepp_frame, text="滤镜", padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=list(self.filters.keys()),
            state="readonly"
        )
        filter_combo.pack(fill=tk.X)
        filter_combo.bind('<<ComboboxSelected>>', self.on_param_change)
        
        # 美颜参数
        params_frame = ttk.LabelFrame(facepp_frame, text="美颜参数", padding=5)
        params_frame.pack(fill=tk.X, expand=True)
        
        # 磨皮调节
        self.create_slider(
            params_frame,
            "磨皮:",
            self.smoothing_var,
            0, 100,
            self.on_param_change
        )
        
        # 美白调节
        self.create_slider(
            params_frame,
            "美白:",
            self.whitening_var,
            0, 100,
            self.on_param_change
        )
        
        # 瘦脸调节
        self.create_slider(
            params_frame,
            "瘦脸:",
            self.thinface_var,
            0, 100,
            self.on_param_change
        )
        
        # 小脸调节
        self.create_slider(
            params_frame,
            "小脸:",
            self.shrink_face_var,
            0, 100,
            self.on_param_change
        )
        
        # 大眼调节
        self.create_slider(
            params_frame,
            "大眼:",
            self.enlarge_eye_var,
            0, 100,
            self.on_param_change
        )
        
        # 去眉毛调节
        self.create_slider(
            params_frame,
            "去眉毛:",
            self.remove_eyebrow_var,
            0, 100,
            self.on_param_change
        )
        
        # 添加重置按钮
        reset_frame = ttk.Frame(facepp_frame)
        reset_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Button(
            reset_frame,
            text="重置美颜参数",
            command=self.reset_beauty_params,
            style='Small.TButton',
            width=12
        ).pack(side=tk.RIGHT)
        
    def setup_api(self):
        """设置API配置"""
        from dialogs.api_setting import APISettingDialog
        APISettingDialog(self.parent.dialog)
        self.load_api_config()
        
    def create_slider(self, parent, label_text, variable, from_, to, command):
        """创建统一样式的滑动条"""
        # 主容器
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        # 第一行：标签和数值
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X)
        
        # 标签
        label = ttk.Label(
            header_frame, 
            text=label_text, 
            style='SliderLabel.TLabel'
        )
        label.pack(side=tk.LEFT)
        
        # 数值显示
        value_label = ttk.Label(
            header_frame,
            text="0",
            width=4,
            anchor=tk.E
        )
        value_label.pack(side=tk.RIGHT)
        
        # 滑动条
        slider = ttk.Scale(
            frame,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            variable=variable,
            command=lambda v: self.on_scale_change(command)
        )
        slider.pack(fill=tk.X, expand=True)
        
        # 绑定开始和结束滑动事件
        slider.bind("<ButtonPress-1>", self.start_sliding)
        slider.bind("<ButtonRelease-1>", lambda e: self.stop_sliding(command))
        
        # 更新数值显示
        variable.trace_add("write", lambda *args: value_label.configure(text=str(variable.get())))

    def on_param_change(self, *args):
        """参数改变时的处理"""
        if not self.api_key or not self.api_secret:
            messagebox.showwarning("提示", "请先配置Face++ API")
            return
            
        # 检查是否有图片
        if not hasattr(self.parent, 'current_image') or self.parent.current_image is None:
            messagebox.showwarning("提示", "请先上传图片")
            return
            
        # 如果正在滑动，不立即处理
        if self.is_sliding:
            return
            
        try:
            # 保存原始图像
            if not hasattr(self, 'original_image') or self.original_image is None:
                self.original_image = self.parent.current_image.copy()
            
            # 每次处理都从原始图像开始
            current_image = self.original_image.copy()
            
            # 调整图片尺寸到合适大小
            height, width = current_image.shape[:2]
            max_size = 1024  # Face++ 建议的最大尺寸
            
            if width > max_size or height > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                resized_image = cv2.resize(
                    current_image, 
                    (new_width, new_height),
                    interpolation=cv2.INTER_AREA
                )
            else:
                resized_image = current_image.copy()
            
            # 转换为base64
            _, buffer = cv2.imencode('.jpg', resized_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 准备请求参数，严格按照API文档的参数名称
            params = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'image_base64': image_base64,
            }
            
            # 添加美颜参数，确保参数名称完全匹配API文档
            if self.whitening_var.get() > 0:
                params['whitening'] = self.whitening_var.get()
            if self.smoothing_var.get() > 0:
                params['smoothing'] = self.smoothing_var.get()
            if self.thinface_var.get() > 0:
                params['thinface'] = self.thinface_var.get()  # 保持原参数名
            if self.shrink_face_var.get() > 0:
                params['shrink_face'] = self.shrink_face_var.get()  # 保持原参数名
            if self.enlarge_eye_var.get() > 0:
                params['enlarge_eye'] = self.enlarge_eye_var.get()  # 保持原参数名
            if self.remove_eyebrow_var.get() > 0:
                params['remove_eyebrow'] = self.remove_eyebrow_var.get()
            
            # 添加滤镜参数
            filter_type = self.filters.get(self.filter_var.get())
            if filter_type and filter_type != "none":
                params['filter_type'] = filter_type
                
            # 打印请求参数，用于调试
            print("Face++ API请求参数:", params)
            
            # 如果没有任何美颜参数和滤镜，直接恢复原图
            if len(params) <= 3:  # 只有api_key、api_secret和image_base64
                self.parent.current_image = self.original_image.copy()
                self.parent.update_preview()
                return
                
            # 发送请求
            response = requests.post(
                'https://api-cn.faceplusplus.com/facepp/v2/beautify',
                data=params,
                timeout=10
            )
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                if 'error_message' in result:
                    messagebox.showerror("错误", result['error_message'])
                    return
                    
                # 解码返回的图片数据
                image_data = result.get('result')
                if not image_data:
                    messagebox.showerror("错误", "未收到处理后的图片数据")
                    return
                    
                # 将base64转换为图像
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    messagebox.showerror("错误", "图片解码失败")
                    return
                
                # 更新预览
                self.parent.current_image = image
                self.parent.update_preview()
            else:
                error_msg = f"请求失败: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error_message' in error_data:
                        error_msg += f"\n{error_data['error_message']}"
                except:
                    pass
                messagebox.showerror("错误", error_msg)
                
        except requests.exceptions.Timeout:
            messagebox.showerror("错误", "请求超时，请重试")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("错误", f"网络请求失败: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"美颜处理失败: {str(e)}")
            
    def reset_beauty_params(self):
        """重置美颜参数"""
        self.smoothing_var.set(0)      # 恢复默认值0
        self.whitening_var.set(0)      # 恢复默认值0
        self.thinface_var.set(0)       # 恢复默认值0
        self.shrink_face_var.set(0)    # 恢复默认值0
        self.enlarge_eye_var.set(0)    # 恢复默认值0
        self.remove_eyebrow_var.set(0) # 恢复默认值0
        self.filter_var.set("无滤镜")
        
        # 恢复原始图像
        if hasattr(self, 'original_image'):
            self.parent.current_image = self.original_image.copy()
            self.parent.update_preview() 