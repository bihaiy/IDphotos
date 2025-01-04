import cv2
import numpy as np
from PIL import Image
import io

def compress_image(image, max_size_kb=500):
    """压缩图片到指定大小
    Args:
        image: PIL.Image 或 numpy.ndarray 图像
        max_size_kb: 最大文件大小(KB)
    Returns:
        压缩后的图像(与输入格式相同)
    """
    # 转换为PIL Image
    if isinstance(image, np.ndarray):
        if len(image.shape) == 3 and image.shape[2] == 4:  # RGBA
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA))
        else:  # RGB
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        pil_image = image
    
    # 初始质量
    quality = 95
    min_quality = 5
    
    while quality > min_quality:
        # 保存到内存
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=quality)
        size_kb = len(buffer.getvalue()) / 1024
        
        # 检查大小
        if size_kb <= max_size_kb:
            break
            
        # 降低质量继续尝试
        quality -= 5
    
    # 如果是numpy数组，转换回去
    if isinstance(image, np.ndarray):
        compressed = cv2.imdecode(
            np.frombuffer(buffer.getvalue(), np.uint8),
            cv2.IMREAD_UNCHANGED
        )
        return compressed
    else:
        buffer.seek(0)
        return Image.open(buffer)

def adjust_color_brightness(hex_color, factor):
    """调整颜色亮度
    Args:
        hex_color: 16进制颜色值，如 '#FF0000'
        factor: 亮度调整因子，>0增加亮度，<0降低亮度
    Returns:
        调整后的16进制颜色值
    """
    # 转换为RGB
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    
    # 调整亮度
    if factor > 0:
        r = min(255, int(r * (1 + factor)))
        g = min(255, int(g * (1 + factor)))
        b = min(255, int(b * (1 + factor)))
    else:
        r = max(0, int(r * (1 + factor)))
        g = max(0, int(g * (1 + factor)))
        b = max(0, int(b * (1 + factor)))
    
    # 转回16进制
    return f'#{r:02x}{g:02x}{b:02x}'

def resize_image_to_kb_base64(image, max_size_kb=500):
    """压缩图片并转换为base64
    Args:
        image: PIL.Image 或 numpy.ndarray 图像
        max_size_kb: 最大文件大小(KB)
    Returns:
        base64字符串
    """
    import base64
    
    # 压缩图片
    compressed = compress_image(image, max_size_kb)
    
    # 转换为base64
    if isinstance(compressed, np.ndarray):
        _, buffer = cv2.imencode('.jpg', compressed)
        base64_str = base64.b64encode(buffer).decode('utf-8')
    else:
        buffer = io.BytesIO()
        compressed.save(buffer, format='JPEG')
        base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return base64_str

def create_gradient_background(width, height, start_color, end_color, direction='vertical'):
    """创建渐变背景
    Args:
        width: 图像宽度
        height: 图像高度
        start_color: 起始颜色 (R,G,B)
        end_color: 结束颜色 (R,G,B)
        direction: 渐变方向，'vertical'或'radial'
    Returns:
        numpy.ndarray 渐变图像
    """
    background = np.zeros((height, width, 3), dtype=np.uint8)
    
    if direction == 'vertical':
        # 创建垂直渐变
        for y in range(height):
            ratio = y / height
            color = tuple(int(start_color[i] * (1 - ratio) + end_color[i] * ratio) for i in range(3))
            background[y, :] = color
    else:
        # 创建径向渐变
        center_x, center_y = width // 2, height // 2
        max_dist = np.sqrt(center_x ** 2 + center_y ** 2)
        
        for y in range(height):
            for x in range(width):
                dist = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                ratio = min(dist / max_dist, 1.0)
                color = tuple(int(start_color[i] * (1 - ratio) + end_color[i] * ratio) for i in range(3))
                background[y, x] = color
    
    return background