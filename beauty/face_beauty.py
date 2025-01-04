import cv2
import numpy as np

class FaceBeauty:
    def __init__(self):
        # 只使用 Haar 级联分类器进行人脸检测
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # 加载眼睛检测器
        self.eye_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
    def slim_face(self, image, strength):
        """瘦脸处理
        Args:
            image: 输入图像
            strength: 瘦脸强度 (0-100)
        Returns:
            处理后的图像
        """
        # 检测人脸
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.1, 5)
        
        if len(faces) == 0:
            return image
            
        result = image.copy()
        height, width = image.shape[:2]
        
        # 处理每个检测到的人脸
        for (x, y, w, h) in faces:
            # 计算脸部中心
            center_x = x + w//2
            center_y = y + h//2
            
            # 创建变形映射
            map_x = np.zeros((height, width), np.float32)
            map_y = np.zeros((height, width), np.float32)
            
            # 计算变形
            for i in range(height):
                for j in range(width):
                    # 计算到脸部中心的距离
                    dx = j - center_x
                    dy = i - center_y
                    d = np.sqrt(dx*dx + dy*dy)
                    
                    if d < w//2:  # 在脸部区域内
                        # 计算变形强度
                        factor = (strength/100.0) * (1.0 - d/(w//2))
                        
                        # 向中心收缩
                        if dx != 0:  # 避免除以零
                            # 修正：如果在中心左边，向左移动；在中心右边，向右移动
                            direction = -1 if dx < 0 else 1
                            map_x[i,j] = j + direction * abs(dx) * factor * 0.3
                            map_y[i,j] = i
                        else:
                            map_x[i,j] = j
                            map_y[i,j] = i
                    else:
                        map_x[i,j] = j
                        map_y[i,j] = i
            
            # 应用变形
            result = cv2.remap(result, map_x, map_y, cv2.INTER_LINEAR)
            
        return result
        
    def enlarge_eyes(self, image, strength):
        """大眼处理
        Args:
            image: 输入图像
            strength: 大眼强度 (0-100)
        Returns:
            处理后的图像
        """
        # 检测人脸
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.1, 5)
        
        if len(faces) == 0:
            return image
            
        result = image.copy()
        height, width = image.shape[:2]
        
        # 处理每个检测到的人脸
        for (x, y, w, h) in faces:
            # 提取人脸区域
            face_roi = gray[y:y+h, x:x+w]
            # 检测眼睛
            eyes = self.eye_detector.detectMultiScale(face_roi, 1.1, 5)
            
            # 处理每只眼睛
            for (ex, ey, ew, eh) in eyes:
                # 计算眼睛中心在原图中的位置
                eye_x = x + ex + ew//2
                eye_y = y + ey + eh//2
                eye_width = max(ew, eh)  # 使用较大的值作为眼睛区域
                
                # 创建变形映射
                map_x = np.zeros((height, width), np.float32)
                map_y = np.zeros((height, width), np.float32)
                
                # 计算变形
                for i in range(height):
                    for j in range(width):
                        # 计算到眼睛中心的距离
                        dx = j - eye_x
                        dy = i - eye_y
                        d = np.sqrt(dx*dx + dy*dy)
                        
                        if d < eye_width:  # 在眼睛区域内
                            # 计算放大强度
                            factor = (1.0 - d/eye_width) * (strength/100.0)
                            scale = 1.0 + factor * 0.5  # 最大放大1.5倍
                            
                            # 向外扩张
                            map_x[i,j] = j - dx * (scale - 1.0)
                            map_y[i,j] = i - dy * (scale - 1.0)
                        else:
                            map_x[i,j] = j
                            map_y[i,j] = i
                
                # 应用变形
                result = cv2.remap(result, map_x, map_y, cv2.INTER_LINEAR)
                
        return result 