import cv2
import numpy as np

class LayoutPreviewGenerator:
    @staticmethod
    def generate_preview(paper_size, orientation, margins, photos, spacing, 
                        show_gridlines, show_divider, dpi=300, images=False):
        """生成排版预览"""
        # 计算纸张像素尺寸
        paper_pixels = [int(x * dpi / 25.4) for x in paper_size]
        if orientation == "landscape":
            paper_pixels[0], paper_pixels[1] = paper_pixels[1], paper_pixels[0]
            
        # 创建画布
        canvas = np.full((paper_pixels[1], paper_pixels[0], 3), 255, dtype=np.uint8)
        
        # 转换边距为像素
        margins_pixels = {k: int(v * dpi / 25.4) for k, v in margins.items()}
        spacing_pixels = int(spacing * dpi / 25.4)
        
        # 定义线条样式
        GRID_COLOR = (150, 150, 150)
        DIVIDER_COLOR = (180, 180, 180)
        GRID_THICKNESS = 2
        DIVIDER_THICKNESS = 1
        
        # 计算可用区域
        available_width = paper_pixels[0] - margins_pixels['left'] - margins_pixels['right']
        available_height = paper_pixels[1] - margins_pixels['top'] - margins_pixels['bottom']
        
        # 计算布局信息
        layout_info = LayoutPreviewGenerator._calculate_layout(
            photos, available_width, available_height, dpi, spacing_pixels
        )
        
        if not layout_info:
            return canvas
            
        total_width, total_height, row_heights = layout_info['dimensions']
        
        # 计算起始位置（居中）
        start_x = margins_pixels['left'] + (available_width - total_width) // 2
        start_y = margins_pixels['top'] + (available_height - total_height) // 2
        
        # 绘制参考线
        if show_gridlines:
            cv2.rectangle(
                canvas,
                (margins_pixels['left'], margins_pixels['top']),
                (paper_pixels[0] - margins_pixels['right'],
                 paper_pixels[1] - margins_pixels['bottom']),
                GRID_COLOR,
                GRID_THICKNESS
            )
        
        # 绘制照片和分隔线
        row_info = []
        current_row = {
            'start_y': start_y,
            'height': 0,
            'photos': []
        }
        
        current_x = start_x
        current_y = start_y
        row_index = 0
        
        # 绘制照片
        for photo_data in layout_info['photos']:
            if current_x + photo_data['width'] > start_x + total_width:
                row_info.append(current_row)
                current_x = start_x
                current_y += row_heights[row_index] + spacing_pixels
                row_index += 1
                current_row = {
                    'start_y': current_y,
                    'height': photo_data['height'],
                    'photos': []
                }
            
            if images and 'image' in photo_data:
                # 绘制实际照片
                image = photo_data['image']
                # 调整照片方向
                if photo_data['layout_type'] == 'vertical':
                    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                # 缩放照片
                scaled_image = cv2.resize(image, (photo_data['width'], photo_data['height']))
                # 放置照片
                canvas[
                    current_y:current_y+photo_data['height'],
                    current_x:current_x+photo_data['width']
                ] = scaled_image
            else:
                # 绘制占位区域
                cv2.rectangle(
                    canvas,
                    (current_x, current_y),
                    (current_x + photo_data['width'], current_y + photo_data['height']),
                    (240, 240, 240),
                    -1
                )
                
                # 显示尺寸文本
                text = photo_data['size_text']
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
                text_x = current_x + (photo_data['width'] - text_width) // 2
                text_y = current_y + (photo_data['height'] + text_height) // 2
                cv2.putText(
                    canvas,
                    text,
                    (text_x, text_y),
                    font,
                    font_scale,
                    (128, 128, 128),
                    thickness
                )
            
            # 记录照片信息
            current_row['height'] = max(current_row['height'], photo_data['height'])
            current_row['photos'].append({
                'x': current_x,
                'width': photo_data['width']
            })
            
            # 更新位置
            current_x += photo_data['width'] + spacing_pixels
        
        # 添加最后一行
        if current_row['photos']:
            row_info.append(current_row)
        
        # 绘制分隔线
        if show_divider:
            # 水平分隔线
            for i in range(len(row_info) - 1):
                y = row_info[i]['start_y'] + row_info[i]['height'] + spacing_pixels//2
                cv2.line(
                    canvas,
                    (margins_pixels['left'], y),
                    (paper_pixels[0] - margins_pixels['right'], y),
                    DIVIDER_COLOR,
                    DIVIDER_THICKNESS,
                    cv2.LINE_AA
                )
            
            # 垂直分隔线
            for row in row_info:
                for i in range(len(row['photos']) - 1):
                    x = row['photos'][i]['x'] + row['photos'][i]['width'] + spacing_pixels//2
                    cv2.line(
                        canvas,
                        (x, row['start_y']),
                        (x, row['start_y'] + row['height']),
                        DIVIDER_COLOR,
                        DIVIDER_THICKNESS,
                        cv2.LINE_AA
                    )
        
        return canvas
    
    @staticmethod
    def _calculate_layout(photos, available_width, available_height, dpi, spacing_pixels):
        """计算布局信息"""
        total_width = 0
        total_height = 0
        row_heights = []
        current_row_width = 0
        current_row_height = 0
        processed_photos = []
        
        for photo in photos:
            photo_size = photo['size']
            photo_count = photo['count']
            is_vertical = photo['layout_type'] == 'vertical'
            
            # 计算照片像素尺寸
            photo_pixels = [int(x * dpi / 25.4) for x in photo_size]
            if is_vertical:
                photo_pixels[0], photo_pixels[1] = photo_pixels[1], photo_pixels[0]
            
            # 生成照片信息
            for _ in range(photo_count):
                photo_info = {
                    'width': photo_pixels[0],
                    'height': photo_pixels[1],
                    'size_text': f"{photo_size[1]}×{photo_size[0]}mm" if is_vertical else f"{photo_size[0]}×{photo_size[1]}mm",
                    'layout_type': photo['layout_type']  # 添加布局类型
                }
                
                # 如果有实际照片，添加到信息中
                if 'image' in photo:
                    photo_info['image'] = photo['image']
                
                if current_row_width + photo_pixels[0] > available_width:
                    total_width = max(total_width, current_row_width - spacing_pixels)
                    total_height += current_row_height + spacing_pixels
                    row_heights.append(current_row_height)
                    current_row_width = photo_pixels[0] + spacing_pixels
                    current_row_height = photo_pixels[1]
                    
                    if total_height + photo_pixels[1] > available_height:
                        return None
                else:
                    current_row_width += photo_pixels[0] + spacing_pixels
                    current_row_height = max(current_row_height, photo_pixels[1])
                
                processed_photos.append(photo_info)
        
        # 添加最后一行
        if current_row_width > 0 and total_height + current_row_height <= available_height:
            total_width = max(total_width, current_row_width - spacing_pixels)
            total_height += current_row_height
            row_heights.append(current_row_height)
        
        return {
            'dimensions': (total_width, total_height, row_heights),
            'photos': processed_photos
        } 