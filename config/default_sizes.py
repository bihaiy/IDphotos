import json
import os

def init_config_files():
    """初始化配置文件"""
    # 默认纸张尺寸
    default_paper_sizes = {
        "4R（102x152mm）": [102, 152],
        "A4 (210×297mm)": [210, 297],
        "A5 (148×210mm)": [148, 210],
        "A6 (105×148mm)": [105, 148],
        "B5 (176×250mm)": [176, 250],
        "5寸 (127×178mm)": [127, 178],
        "6寸 (152×102mm)": [152, 102],
        "7寸 (178×127mm)": [178, 127],
        "8寸 (203×152mm)": [203, 152]
    }

    # 默认证件照尺寸
    default_photo_sizes = {
        "一寸 (25×35mm)": [25, 35],
        "二寸 (35×49mm)": [35, 49],
        "小一寸 (22×32mm)": [22, 32],
        "小二寸 (35×45mm)": [35, 45],
        "大一寸 (33×48mm)": [33, 48],
        "大二寸 (35×53mm)": [35, 53],
        "五寸（127x89mm）": [89, 127],
        "护照 (33×48mm)": [33, 48],
        "签证 (35×45mm)": [35, 45],
        "驾照 (21×26mm)": [21, 26],
        "职业资格 (25×35mm)": [25, 35],
        "社保 (26×32mm)": [26, 32],
        "学历 (33×48mm)": [33, 48],
        "健康证 (32×40mm)": [32, 40]
    }

    # 默认排版样式
    default_layout_styles = {
        "1寸9张": {
            "name": "1寸9张",
            "paper_size": "4R（102x152mm）",
            "orientation": "portrait",
            "margins": {
                "top": 5.0,
                "bottom": 5.0,
                "left": 5.0,
                "right": 5.0
            },
            "photos": [
                {
                    "photo_size": "一寸 (25×35mm)",
                    "layout_type": "horizontal",
                    "count": 3
                },
                {
                    "photo_size": "一寸 (25×35mm)",
                    "layout_type": "horizontal",
                    "count": 3
                },
                {
                    "photo_size": "一寸 (25×35mm)",
                    "layout_type": "horizontal",
                    "count": 3
                }
            ],
            "spacing": 2.0,
            "show_gridlines": False,
            "show_divider": True
        },
        "2寸8张": {
            "name": "2寸8张",
            "paper_size": "4R（102x152mm）",
            "orientation": "landscape",
            "margins": {
                "top": 1.0,
                "bottom": 1.0,
                "left": 3.0,
                "right": 3.0
            },
            "photos": [
                {
                    "photo_size": "二寸 (35×49mm)",
                    "layout_type": "horizontal",
                    "count": 4
                },
                {
                    "photo_size": "二寸 (35×49mm)",
                    "layout_type": "horizontal",
                    "count": 2
                },
                {
                    "photo_size": "二寸 (35×49mm)",
                    "layout_type": "horizontal",
                    "count": 2
                }
            ],
            "spacing": 1.0,
            "show_gridlines": False,
            "show_divider": True
        },
        "1寸5张2寸4张混排": {
            "name": "1寸5张2寸4张混排",
            "paper_size": "4R（102x152mm）",
            "orientation": "landscape",
            "margins": {
                "top": 5.0,
                "bottom": 5.0,
                "left": 4.0,
                "right": 4.0
            },
            "photos": [
                {
                    "photo_size": "一寸 (25×35mm)",
                    "layout_type": "horizontal",
                    "count": 5
                },
                {
                    "photo_size": "二寸 (35×49mm)",
                    "layout_type": "horizontal",
                    "count": 2
                },
                {
                    "photo_size": "二寸 (35×49mm)",
                    "layout_type": "horizontal",
                    "count": 2
                }
            ],
            "spacing": 1.0,
            "show_gridlines": False,
            "show_divider": True
        }
    }

    # 初始化纸张尺寸配置
    if not os.path.exists('paper_sizes.json'):
        with open('paper_sizes.json', 'w', encoding='utf-8') as f:
            json.dump(default_paper_sizes, f, ensure_ascii=False, indent=4)

    # 初始化证件照尺寸配置
    if not os.path.exists('photo_sizes.json'):
        with open('photo_sizes.json', 'w', encoding='utf-8') as f:
            json.dump(default_photo_sizes, f, ensure_ascii=False, indent=4)

    # 初始化排版样式配置
    if not os.path.exists('layout_styles.json'):
        with open('layout_styles.json', 'w', encoding='utf-8') as f:
            json.dump(default_layout_styles, f, ensure_ascii=False, indent=4)

    # 初始化API配置
    if not os.path.exists('api_config.json'):
        with open('api_config.json', 'w', encoding='utf-8') as f:
            json.dump({"api_key": "", "api_secret": ""}, f)