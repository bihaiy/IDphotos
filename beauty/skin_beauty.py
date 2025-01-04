import cv2
import numpy as np

class SkinBeauty:
    def __init__(self):
        pass
        
    def smooth_skin(self, image, strength):
        """磨皮处理
        Args:
            image: 输入图像
            strength: 磨皮强度 (0-100)
        Returns:
            处理后的图像
        """
        # 双边滤波参数
        sigma = strength / 10  # 将强度映射到合适范围
        d = int(sigma * 5)    # 邻域直径
        
        # 对图像进行双边滤波
        blur = cv2.bilateralFilter(image, d, sigma*2, sigma)
        
        # 高斯模糊
        gaussian = cv2.GaussianBlur(image, (7, 7), sigma)
        
        # 根据强度混合原图和滤波结果
        result = cv2.addWeighted(
            image, 
            1 - strength/100.0,
            cv2.addWeighted(blur, 0.6, gaussian, 0.4, 0),
            strength/100.0,
            0
        )
        
        return result
        
    def whiten_skin(self, image, strength):
        """美白处理
        Args:
            image: 输入图像
            strength: 美白强度 (0-100)
        Returns:
            处理后的图像
        """
        # 转换到LAB颜色空间
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # 调整亮度通道
        l = cv2.add(l, int(strength * 1.5))
        
        # 合并通道
        lab = cv2.merge([l, a, b])
        
        # 转换回BGR
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # 根据强度混合
        return cv2.addWeighted(image, 1 - strength/100.0, result, strength/100.0, 0) 