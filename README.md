# Fairy PSD 工具集

这是一个用于处理和操作 PSD 文件的工具集，提供了 PSD 文件解析、图层提取和图像合成等功能。

## 功能特点

- **PSD 解析**：解析 PSD 文件结构，提取图层信息和元数据
- **图层提取**：将 PSD 文件中的图层和图层组提取为单独的 PNG 图像
- **图像合成**：根据图层信息将提取的 PNG 图像重新合成为完整图像
- **混合模式支持**：支持多种 Photoshop 混合模式，如正常、正片叠底、滤色、叠加等
- **图像比较**：比较两个图像并生成差异图像，支持增强差异显示和并排比较

## 安装依赖

```bash
pip install psd-tools pillow numpy
```

## 使用方法

### 1. PSD 解析和图层提取

使用 `psd_parser.py` 脚本解析 PSD 文件并提取图层：

```bash
python src/psd_parser.py
```

这将：
- 解析指定的 PSD 文件
- 打印 PSD 文件的详细信息
- 将图层信息保存为 JSON 文件
- 将每个图层和图层组提取为单独的 PNG 图像

### 2. 图像合成

使用 `psd_composer.py` 脚本将提取的图层重新合成为完整图像：

```bash
python src/psd_composer.py compose <图层目录路径> [-o <输出图像路径>]
```

例如：

```bash
python src/psd_composer.py compose /Users/zhouke/Documents/project/fairy/data/image/layers
```

### 3. 图像比较

使用 `psd_composer.py` 脚本比较两个图像并生成差异图像：

```bash
python src/psd_composer.py compare <图像1路径> <图像2路径> [-o <差异图像输出路径>] [--no-enhance] [--side-by-side]
```

选项：
- `--no-enhance`：不增强差异图像
- `--side-by-side`：生成并排比较图像

## 项目结构

```
├── src/
│   ├── psd_parser.py      # PSD 解析和图层提取
│   ├── psd_composer.py    # 图层合成和图像比较
│   ├── check_psd_structure.py  # 检查 PSD 结构
│   ├── visualize_psd_structure.py  # 可视化 PSD 结构
│   ├── psd_viewer.html    # PSD 查看器 HTML 界面
│   ├── psd.ipynb          # PSD 处理 Jupyter 笔记本
│   └── autogen.ipynb      # 自动生成代码 Jupyter 笔记本
```

## 图层合成逻辑

`psd_composer.py` 中的图层合成逻辑：

1. 收集图层组信息：
   - 收集根目录下的 PNG 文件（如 PSD 合成图像）
   - 收集第一层级子目录中的 PNG 文件
   - 不递归处理更深层次的子目录

2. 图层排序：
   - 将图层按深度分为两组：深度为 0 的根图层和深度为 1 的第一层子图层
   - 对第一层子图层按索引从大到小排序，确保索引较大的图层后渲染
   - 先渲染第一层子图层，再渲染根图层，确保根图层覆盖在子图层上面

3. 图层渲染：
   - 对于有明确位置信息的图层，使用元数据中的位置信息
   - 对于根目录下的 PNG 文件，直接粘贴到 (0,0) 位置
   - 应用混合模式和不透明度

## 混合模式支持

支持的混合模式包括：
- 正常 (NORMAL)
- 穿透 (PASS_THROUGH)
- 正片叠底 (MULTIPLY)
- 滤色 (SCREEN)
- 叠加 (OVERLAY)
- 柔光 (SOFT_LIGHT)
- 强光 (HARD_LIGHT)
- 颜色减淡 (COLOR_DODGE)
- 颜色加深 (COLOR_BURN)
- 变暗 (DARKEN)
- 变亮 (LIGHTEN)

## 注意事项

- 图层合成仅考虑第一层级的 PNG 文件，不考虑更深层次的子图层
- 图层排序按照 PSD 中的图层索引从大到小排序，确保索引较大的图层（在 PSD 中位于上层）覆盖在索引较小的图层（在 PSD 中位于下层）上面
- 根目录下的 PNG 文件（通常是 PSD 合成图像）最后渲染，确保覆盖在所有子图层上面

## 许可证

[MIT](LICENSE)