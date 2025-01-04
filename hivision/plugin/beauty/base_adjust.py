"""
亮度、对比度、锐化、饱和度调整模块
"""

import cv2
import numpy as np


class BaseAdjust:
    """基础图像调整类"""
    
    @staticmethod
    def adjust_brightness(image, value):
        """调整亮度
        Args:
            image: numpy.ndarray - 输入图像
            value: int - 亮度调整值 (-100 到 100)
        Returns:
            numpy.ndarray - 调整后的图像
        """
        if value == 0:
            return image
            
        # 将值映射到合适的范围
        alpha = 1.0 + (value / 100.0)  # 亮度系数
        
        # 调整亮度
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        return adjusted
    
    @staticmethod
    def adjust_contrast(image, value):
        """调整对比度
        Args:
            image: numpy.ndarray - 输入图像
            value: int - 对比度调整值 (-100 到 100)
        Returns:
            numpy.ndarray - 调整后的图像
        """
        if value == 0:
            return image
            
        # 将值映射到合适的范围
        alpha = 1.0 + (value / 100.0)  # 对比度系数
        beta = 128 * (1 - alpha)  # 亮度偏移
        
        # 调整对比度
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return adjusted
    
    @staticmethod
    def adjust_saturation(image, value):
        """调整饱和度
        Args:
            image: numpy.ndarray - 输入图像
            value: int - 饱和度调整值 (-100 到 100)
        Returns:
            numpy.ndarray - 调整后的图像
        """
        if value == 0:
            return image
            
        # 将值映射到合适的范围
        alpha = 1.0 + (value / 100.0)  # 饱和度系数
        
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 调整饱和度
        s = cv2.convertScaleAbs(s, alpha=alpha, beta=0)
        
        # 合并通道并转回BGR
        hsv = cv2.merge([h, s, v])
        adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return adjusted
    
    @staticmethod
    def adjust_sharpness(image, value):
        """调整锐化
        Args:
            image: numpy.ndarray - 输入图像
            value: int - 锐化调整值 (0 到 100)
        Returns:
            numpy.ndarray - 调整后的图像
        """
        if value == 0:
            return image
            
        # 将值映射到合适的范围
        alpha = value / 100.0  # 锐化强度
        
        # 创建锐化核
        kernel = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ])
        
        # 应用锐化
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # 根据强度混合原图和锐化结果
        adjusted = cv2.addWeighted(image, 1 - alpha, sharpened, alpha, 0)
        return adjusted


def adjust_brightness_contrast_sharpen_saturation(
    image,
    brightness=0,
    contrast=0,
    sharpness=0,
    saturation=0
):
    """组合调整亮度、对比度、锐化和饱和度
    Args:
        image: numpy.ndarray - 输入图像
        brightness: int - 亮度调整值 (-100 到 100)
        contrast: int - 对比度调整值 (-100 到 100)
        sharpness: int - 锐化调整值 (0 到 100)
        saturation: int - 饱和度调整值 (-100 到 100)
    Returns:
        numpy.ndarray - 调整后的图像
    """
    adjuster = BaseAdjust()
    
    # 按顺序应用调整
    if brightness != 0:
        image = adjuster.adjust_brightness(image, brightness)
    if contrast != 0:
        image = adjuster.adjust_contrast(image, contrast)
    if sharpness != 0:
        image = adjuster.adjust_sharpness(image, sharpness)
    if saturation != 0:
        image = adjuster.adjust_saturation(image, saturation)
    
    return image
