# PSD到HTML转换工具

这个工具集可以将PSD文件解析结果转换为HTML布局，使网页布局与PSD设计稿保持一致。

## 功能特点

- 根据PSD解析结果生成HTML布局
- 保持图层的位置、大小、可见性和混合模式
- 支持图层组和嵌套图层
- 提供交互控制，可以切换图层可见性
- 自动查找并使用正确的图层图片

## 文件说明

- `psd_parser.py`: PSD文件解析工具，提取图层信息并保存为JSON
- `psd_html_generator.py`: 核心功能模块，将PSD信息转换为HTML
- `generate_psd_html.py`: 命令行工具，用于生成HTML文件

## 使用方法

### 1. 解析PSD文件

首先使用`psd_parser.py`解析PSD文件，生成图层信息和图片：

```bash
python psd_parser.py --psd-file path/to/your.psd --output-dir ../data/image/layers
```

这将在指定目录下生成：
- `psd_info.json`: 包含所有图层信息的JSON文件
- `layers/`: 包含所有图层图片的目录

### 2. 生成HTML布局

然后使用`generate_psd_html.py`生成HTML文件：

```bash
python generate_psd_html.py --psd-info ../data/image/psd_info.json --layers-dir ../data/image/layers --output-file ../src/psd_layout_generated.html
```

参数说明：
- `--psd-info`: PSD信息JSON文件路径
- `--layers-dir`: 图层图片目录路径
- `--output-file`: 输出HTML文件路径

### 3. 查看HTML布局

在浏览器中打开生成的HTML文件，即可查看PSD布局。

## 交互功能

生成的HTML页面提供以下交互功能：

- **显示/隐藏所有**: 切换所有图层的可见性
- **重置视图**: 恢复所有图层的初始可见性
- **点击图层**: 点击单个图层可以切换其可见性

## 自定义样式

如果需要自定义HTML布局的样式，可以修改`psd_html_generator.py`中的CSS部分。

## 注意事项

- 确保图层图片目录结构与PSD解析结果一致
- 对于复杂的PSD文件，生成的HTML可能会比较大
- 某些高级混合模式在浏览器中可能无法完全还原