#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse
import re

def sanitize_css_name(name):
    """
    将图层名称转换为有效的CSS类名
    """
    # 移除非法字符，只保留字母、数字、连字符和下划线
    sanitized = re.sub(r'[^\w\-]', '_', name)
    # 确保不以数字开头
    if sanitized and sanitized[0].isdigit():
        sanitized = 'layer_' + sanitized
    return sanitized

def get_layer_css(layer, parent_path=''):
    """
    生成图层的CSS样式
    """
    # 计算相对于父图层的位置
    left = layer['left']
    top = layer['top']
    width = layer['width']
    height = layer['height']
    
    # 生成CSS类名
    layer_path = layer['path']
    if parent_path and layer_path.startswith(parent_path + '/'):
        relative_path = layer_path[len(parent_path)+1:]
    else:
        relative_path = layer_path
    
    css_class_name = sanitize_css_name(relative_path)
    
    # 生成CSS样式
    css = f".{css_class_name} {{"
    css += f"\n    position: absolute;"
    css += f"\n    left: {left}px;"
    css += f"\n    top: {top}px;"
    css += f"\n    width: {width}px;"
    css += f"\n    height: {height}px;"
    
    # 设置可见性
    if not layer['visible']:
        css += "\n    display: none;"
    
    # 设置不透明度
    opacity = round(layer['opacity'] / 255, 2)
    if opacity < 1.0:
        css += f"\n    opacity: {opacity};"
    
    # 设置混合模式
    blend_mode = layer['blend_mode']
    if blend_mode and 'NORMAL' not in blend_mode:
        css_blend_mode = blend_mode.lower().replace('_', '-')
        css += f"\n    mix-blend-mode: {css_blend_mode};"
    
    css += "\n}\n"
    
    return css_class_name, css

def get_layer_html(layer, layers_dir, parent_path='', depth=0):
    """
    生成图层的HTML代码
    """
    indent = '    ' * depth
    layer_name = layer['name']
    layer_path = layer['path']
    layer_type = layer['type']
    is_group = layer_type == 'Group' or ('children' in layer and layer['children'])
    
    # 生成CSS类名
    if parent_path and layer_path.startswith(parent_path + '/'):
        relative_path = layer_path[len(parent_path)+1:]
    else:
        relative_path = layer_path
    
    css_class_name = sanitize_css_name(relative_path)
    
    # 构建图层图片路径
    layer_name_encoded = layer['save_name'] or layer['name']
    parent_segments = layer_path.split('/')
    parent_name = parent_segments[-2] if len(parent_segments) > 1 else ''
    
    # 尝试多种可能的图片路径
    img_paths = [
        # 直接使用图层名称
        f"{layers_dir}/{layer_name_encoded}/{layer_name_encoded}.png",
        # 使用图层路径的最后一部分
        f"{layers_dir}/{layer_path.split('/')[-1]}/{layer_path.split('/')[-1]}.png",
        # 处理子图层路径
        f"{layers_dir}/{parent_name}/{layer_name_encoded}/{layer_name_encoded}.png",
        # 子图层特殊处理 - 使用子图层目录名称作为文件名
        f"{layers_dir}/{parent_name}/{parent_name}_sub_1/{parent_name}_sub_1.png"
    ]
    
    # 查找第一个存在的图片路径
    img_path = None
    for path in img_paths:
        if os.path.exists(path):
            img_path = path
            break
    
    # 生成HTML代码
    html = f"{indent}<div class=\"layer {css_class_name}\" title=\"{layer_name}\">"
    
    # 如果是图层组，递归处理子图层
    if is_group and 'children' in layer and layer['children']:
        html += "\n"
        for child in layer['children']:
            html += get_layer_html(child, layers_dir, layer_path, depth + 1)
        html += f"{indent}"
    elif img_path:  # 如果找到了图片路径，添加图片
        html += f"\n{indent}    <img src=\"{img_path}\" alt=\"{layer_name}\" />"
        html += f"\n{indent}"
    
    html += "</div>\n"
    
    return html

def generate_psd_html(psd_info_path, layers_dir, output_file):
    """
    根据PSD解析结果生成HTML文件
    
    参数:
        psd_info_path: PSD信息JSON文件路径
        layers_dir: 图层图片目录路径
        output_file: 输出HTML文件路径
    """
    # 加载PSD信息
    with open(psd_info_path, 'r', encoding='utf-8') as f:
        psd_info = json.load(f)
    
    # 提取PSD基本信息
    psd_name = psd_info['name']
    psd_width = psd_info['width']
    psd_height = psd_info['height']
    
    # 生成CSS样式
    css = """/* PSD布局样式 */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
    padding: 20px;
}

.psd-container {
    position: relative;
    margin: 0 auto;
    overflow: hidden;
    background-color: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.layer {
    position: absolute;
}

.layer img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

/* 控制面板样式 */
.controls {
    margin-bottom: 20px;
    padding: 15px;
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.controls h2 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 18px;
    color: #333;
}

.control-group {
    margin-bottom: 10px;
}

.control-group label {
    display: inline-block;
    margin-right: 10px;
    font-weight: bold;
}

.toggle-button {
    padding: 5px 10px;
    margin-right: 5px;
    background-color: #4a6bdf;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

.toggle-button:hover {
    background-color: #3a59c0;
}

/* 图层特定样式 */
"""
    
    # 为每个图层生成CSS
    for layer in psd_info['layers']:
        def process_layer(l, parent_path=''):
            class_name, layer_css = get_layer_css(l, parent_path)
            nonlocal css
            css += layer_css
            
            # 递归处理子图层
            if 'children' in l and l['children']:
                for child in l['children']:
                    process_layer(child, l['path'])
        
        process_layer(layer)
    
    # 生成HTML结构
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{psd_name} - PSD布局</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="controls">
        <h2>PSD布局控制</h2>
        <div class="control-group">
            <label>图层可见性:</label>
            <button class="toggle-button" id="toggle-all">显示/隐藏所有</button>
            <button class="toggle-button" id="reset-view">重置视图</button>
        </div>
        <div class="control-group">
            <label>PSD信息:</label>
            <span>{psd_name} ({psd_width}×{psd_height}像素)</span>
        </div>
    </div>
    
    <div class="psd-container" style="width: {psd_width}px; height: {psd_height}px;">
"""
    
    # 添加图层HTML
    for layer in psd_info['layers']:
        html += get_layer_html(layer, layers_dir)
    
    # 添加JavaScript交互
    html += """    </div>
    
    <script>
        // 图层交互功能
        document.addEventListener('DOMContentLoaded', function() {
            // 获取所有图层
            const layers = document.querySelectorAll('.layer');
            
            // 切换所有图层可见性
            document.getElementById('toggle-all').addEventListener('click', function() {
                layers.forEach(layer => {
                    if (layer.style.display === 'none') {
                        layer.style.display = '';
                    } else {
                        layer.style.display = 'none';
                    }
                });
            });
            
            // 重置视图
            document.getElementById('reset-view').addEventListener('click', function() {
                layers.forEach(layer => {
                    layer.style.display = '';
                });
            });
            
            // 点击图层切换可见性
            layers.forEach(layer => {
                layer.addEventListener('click', function(e) {
                    e.stopPropagation();
                    this.style.display = this.style.display === 'none' ? '' : 'none';
                });
            });
        });
    </script>
</body>
</html>
"""
    
    # 写入HTML文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"已生成HTML文件: {output_file}")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将PSD信息转换为HTML布局')
    parser.add_argument('--psd-info', type=str, default='../data/image/psd_info.json',
                        help='PSD信息JSON文件路径')
    parser.add_argument('--layers-dir', type=str, default='../data/image/layers',
                        help='图层图片目录路径')
    parser.add_argument('--output-file', type=str, default='../src/psd_layout_generated.html',
                        help='输出HTML文件路径')
    args = parser.parse_args()
    
    # 生成HTML
    generate_psd_html(args.psd_info, args.layers_dir, args.output_file)

if __name__ == "__main__":
    main()