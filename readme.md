# 证件照制作系统

软件基于开源的项目
<a href="https://github.com/Zeyi-Lin/HivisionIDPhotos" target="_blank">https://github.com/Zeyi-Lin/HivisionIDPhotos</a>

**软件下载链接:** <a href="https://pan.baidu.com/s/1fqAv4iHtHa8gmnjsFnK9AQ?pwd=svam" target="_blank">百度网盘</a> 提取码: svam

## 软件操作视频
[![证件照制作系统操作视频](https://img.youtube.com/vi/NhPxdoP4R2o/0.jpg)](https://youtu.be/NhPxdoP4R2o)

点击上方图片观看视频教程

# 目录
* [功能特点](#功能特点)
* [安装说明](#安装说明)
  * [环境要求](#环境要求)
  * [安装步骤](#安装步骤)
  * [打包说明](#打包说明)
* [使用说明](#使用说明)
  * [基本操作流程](#基本操作流程)
  * [照片编辑](#照片编辑)
  * [尺寸管理](#尺寸管理)
  * [保存与导出](#保存与导出)

## 功能特点
- 智能抠图：支持多种抠图模型，精准分离人像
- 智能美颜：本地美颜和Face++美颜双引擎支持
- 换背景：支持纯色、渐变背景，提供多种预设颜色
- 证照排版：提供多种预设排版样式，支持自定义排版
- 一键制作：一键完成抠图、美颜、换底、排版全流程

# 安装说明

## 环境要求
- Python 3.8+
- pip包管理器
- Windows 7/10/11

## 安装步骤
1. 克隆或下载项目代码
   ```bash
   git clone https://github.com/bihaiy/IDphotos.git
   cd IDphotos
   ```
2. 创建并激活虚拟环境（推荐）：
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 下载人像抠图模型权重文件：

   模型文件需存放在 `hivision/creator/weights` 目录下：

   | 人像抠图模型 | 介绍 | 下载链接 |
   |------------|------|---------|
   | MODNet | MODNet官方权重 | <a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/modnet%5Fphotographic%5Fportrait%5Fmatting.onnx" target="_blank">下载</a>(24.7MB) |
   | hivision_modnet | 对纯色换底适配性更好的抠图模型 | <a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/hivision%5Fmodnet.onnx" target="_blank">下载</a>(24.7MB) |
   | rmbg-1.4 | BRIA AI开源的抠图模型 | <a href="https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model.onnx?download=true" target="_blank">下载</a>(176.2MB)后重命名为rmbg-1.4.onnx |
   | birefnet-v1-lite | ZhengPeng7开源的抠图模型，拥有最好的分割精度 | <a href="https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-bb%5Fswin%5Fv1%5Ftiny-epoch%5F232.onnx" target="_blank">下载</a>(224MB)后重命名为birefnet-v1-lite.onnx |

5. 人脸检测模型配置（可选）：

   | 人脸检测模型 | 介绍 | 使用说明 |
   |------------|------|---------|
   | MTCNN | **离线**人脸检测模型，高性能CPU推理（毫秒级），为默认模型，检测精度较低 | Clone此项目后直接使用 |
   | RetinaFace | **离线**人脸检测模型，CPU推理速度中等（秒级），精度较高 | <a href="https://github.com/Zeyi-Lin/HivisionIDPhotos/releases/download/pretrained-model/retinaface-resnet50.onnx" target="_blank">下载</a>后放到hivision/creator/retinaface/weights目录下 |
   | Face++ | 旷视推出的在线人脸检测API，检测精度较高 | 需配置Face++ API密钥，详见<a href="https://console.faceplusplus.com.cn/documents/4888373" target="_blank">官方文档</a> |

6. 运行程序：
   ```bash
   python main.py
   ```

## 打包说明
1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 执行打包命令：
   ```bash
   pyinstaller idphoto.spec
   ```
3. 打包完成后，可执行文件位于 `dist` 目录

4. 或者直接下载打包好的文件：
   - 链接: <a href="https://pan.baidu.com/s/1fqAv4iHtHa8gmnjsFnK9AQ?pwd=svam" target="_blank">百度网盘</a> 提取码: svam

# 使用说明

## 基本操作流程
1. 上传照片：
   - 点击左上角预览区的"上传"按钮
   - 支持jpg、png格式的图片
   - 可通过菜单栏"文件->打开"上传
   - 点击左上角编辑图标可调整照片的亮度、对比度等参数

2. 抠图处理：
   - 点击"抠图"按钮或使用菜单栏"编辑->抠图"
   - 可调整面部比例(0.1-0.5)和头顶距离(0.05-0.3)
   - 支持人脸矫正和高清照片输出
   - 可选择不同的抠图模型和人脸检测模型

3. 换背景：
   - 点击"换背景"按钮或使用菜单栏"编辑->换背景"
   - 支持纯色背景和渐变背景
   - 提供多种预设颜色和自定义颜色
   - 可调整渐变方向和强度
   - 支持添加最多3张照片，每张照片可独立编辑
   - 点击左上角"+"号添加照片，点击编辑图标调整照片参数

4. 证照排版：
   - 点击"证照排版"按钮或使用菜单栏"编辑->证照排版"
   - 提供多种预设排版样式
   - 可自定义排版参数和照片尺寸
   - 支持显示参考线和分隔线
   - 可使用换背景区域的1-3张照片进行混合排版

## 照片编辑
1. 基础调整：
   - 亮度：-50 到 50
   - 对比度：-30 到 50
   - 饱和度：-50 到 50
   - 色相：-30 到 30
   - 锐化：0 到 30

2. 本地美颜：
   - 磨皮：0 到 50
   - 美白：0 到 30
   - 瘦脸：0 到 20
   - 大眼：0 到 15

3. Face++美颜：
   - 需配置Face++ API密钥
   - 支持多种美颜参数调节
   - 提供35种滤镜效果

## 尺寸管理
1. 通过菜单栏"工具->尺寸管理"打开管理窗口
2. 支持添加、编辑、删除和排序
3. 可管理纸张尺寸和证件照尺寸
4. 所有尺寸数据保存在JSON配置文件中

## 保存与导出
1. 支持保存多种格式：
   - 透明照片(PNG)
   - 换底照片(JPG)
   - 排版照片(JPG)
2. 可通过菜单栏"文件"进行相应操作
3. 支持一键制作完整流程

## 常见问题(FAQ)

### 1. Face++美颜功能无法使用
- 确认已正确配置Face++ API密钥
- 检查网络连接是否正常
- 确认API调用次数未超出限制

### 2. 抠图效果不理想
- 确保照片光线充足、背景简单
- 尝试调整面部比例和头顶距离参数
- 选择不同的抠图模型进行尝试

### 3. 排版照片模糊
- 检查原始照片分辨率是否足够
- 开启高清照片选项
- 确认打印机DPI设置正确

### 4. 程序运行缓慢
- 使用1MB以下的照片
- 关闭不必要的美颜效果
- 确保电脑内存充足

## 项目结构
```
├── config/              # 配置文件目录
│   ├── __init__.py
│   └── default_sizes.py # 默认尺寸配置
├── dialogs/             # 对话框界面
│   ├── __init__.py
│   ├── api_setting.py   # API设置对话框
│   ├── custom_size.py   # 自定义尺寸对话框
│   ├── layout_editor.py # 排版样式编辑器
│   ├── photo_editor.py  # 照片编辑器
│   └── size_manager.py  # 尺寸管理器
├── processors/          # 图像处理
│   ├── __init__.py
│   └── image_processor.py # 图像处理器
├── ui/                  # 用户界面
│   ├── __init__.py
│   ├── preview.py      # 预览区管理
│   ├── params.py       # 参数管理
│   ├── menu.py         # 菜单管理
│   ├── matting_params.py # 抠图参数
│   ├── background_params.py # 背景参数
│   └── layout_params.py # 排版参数
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── constants.py    # 常量定义
│   ├── image_utils.py  # 图像工具
│   ├── layout_preview.py # 排版预览
│   └── style.py        # 界面样式
├── beauty/             # 美颜处理
│   ├── __init__.py
│   ├── face_beauty.py  # 人脸美颜
│   └── skin_beauty.py  # 皮肤美白
├── main.py            # 主程序入口
├── requirements.txt   # 依赖包列表
├── idphoto.spec      # 打包配置
└── README.md         # 项目文档
```

## 贡献指南
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证
本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式
- 问题反馈：通过 GitHub Issues
- 功能建议：通过 GitHub Discussions
- 邮件支持：bihaiy@gmail.com

## 更新记录

### 2025-01-04
- 优化了排版功能：
  - 添加了1寸5张2寸4张混排预设样式
  - 优化了排版参数的默认值
  - 改进了排版预览的显示效果
  - 完善了排版样式的保存机制

### 2024-01-09
- 优化了预览区功能：
  - 在预览区添加了"抠图"、"换背景"、"证照排版"按钮
  - 优化了按钮显示逻辑，有照片时隐藏，无照片时显示
  - 改进了按钮样式，与上传按钮保持一致
- 优化了操作流程：
  - 点击换背景时自动执行上传和抠图
  - 改进了参数标签页的切换逻辑
  - 完善了图片数据的清理机制

### 2024-01-08
- 优化了自定义尺寸管理功能：
  - 添加了尺寸列表的手动排序功能
  - 修复了编辑时尺寸显示的问题
  - 改进了窗口显示位置，现在会居中显示
  - 移除了不必要的操作提示
  - 优化了用户界面交互体验
- 修改了默认设置：
  - 照片间隔默认值改为2mm
  - 默认显示间隔线
  - 页边距默认值设为5mm

### 2024-01-07
- 添加了纸张尺寸和证件照尺寸的JSON配置文件
- 实现了纸张尺寸和证件照尺寸的管理功能
- 添加了自定义纸张和证件照尺寸的功能
- 添加了页边距设置功能，支持上下左右四个方向独立设置

### 2024-01-06
- 完善了核心功能模块：
  - 实现了背景功能，支持多种渲染方式
  - 添加了美颜参数调节功能
  - 实现了打印排版功能
- 优化了用户界面：
  - 添加了参数调节滑动条
  - 实现了实时预览功能
  - 添加了图片下载功能
- 增加了打印功能支持
- 添加了配置保存和加载功能

### 2024-01-05
- 创建了基础的软件界面框架
- 实现了主要功能区域的布局：
  - 左侧预览区（上传区和三个预览窗口）
  - 右侧参数设置区（使用选项卡组织）
- 添加了基本的图片处理功能：
  - 图片上传和预览
  - 图片压缩和格式转换
  - 基础的抠图功能

### 2025-01-09

#### 打印功能改进
- 修复了打印尺寸不正确的问题
- 添加了对不同纸张尺寸的支持
- 改进了图像缩放逻辑，确保打印尺寸准确
- 优化了打印机设置的处理方式

具体改进：
1. 纸张设置
   - 正确设置打印机纸张尺寸
   - 清除自定义纸张设置
   - 设置正确的打印区域

2. 图像缩放
   - 使用纸张实际物理尺寸进行缩放
   - 不受打印机边距限制
   - 保持图像纵横比

3. 打印精度
   - 使用物理坐标进行精确定位
   - 考虑设备分辨率进行正确缩放
   - 确保打印尺寸与选择的纸张大小一致

4. 错误处理
   - 添加了详细的错误信息输出
   - 改进了异常处理机制
   - 提供了更好的用户反馈

#### 使用说明
1. 在打印对话框中选择所需的纸张尺寸
2. 系统会自动调整图像以适应选择的纸张
3. 打印输出的尺寸将严格符合所选纸张大小