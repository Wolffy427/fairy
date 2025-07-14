from psd_tools import PSDImage
import os
import json
from PIL import Image
import numpy as np
import psd_tools.api.layers

def parse_psd(psd_path):
    """解析PSD文件，提取所有图层信息"""
    # 打开PSD文件
    psd = PSDImage.open(psd_path)
    
    # 获取基本信息
    info = {
        'name': os.path.basename(psd_path),
        'width': psd.width,
        'height': psd.height,
        'layers': []
    }
    
    # 递归提取图层信息
    def extract_layer_info(layers, parent_group=None, parent_path='', used_names=None):
        layer_info_list = []
        
        # 初始化已使用名称字典
        if used_names is None:
            used_names = {}
        
        for i, layer in enumerate(layers):
            # 构建图层路径
            layer_name = layer.name
            if parent_path:
                layer_path = f"{parent_path}/{layer_name}"
            else:
                layer_path = layer_name
                
            # 检查是否与父层同名，如果是则添加后缀
            save_name = layer_name
            if parent_path:
                parent_basename = parent_path.split('/')[-1] if '/' in parent_path else parent_path
                if save_name == parent_basename:
                    # 获取当前路径下已使用的后缀数
                    parent_key = parent_path if parent_path else ''
                    if parent_key not in used_names:
                        used_names[parent_key] = {}
                    
                    if save_name not in used_names[parent_key]:
                        used_names[parent_key][save_name] = 0
                    
                    suffix_num = used_names[parent_key][save_name] + 1
                    used_names[parent_key][save_name] = suffix_num
                    save_name = f"{layer_name}_sub_{suffix_num}"
                    # 更新图层路径以包含后缀
                    if parent_path:
                        layer_path = f"{parent_path}/{save_name}"
                    else:
                        layer_path = save_name
                
            layer_info = {
                'name': layer.name,
                'save_name': save_name,  # 添加保存名称，可能包含后缀
                'visible': layer.is_visible(),
                'opacity': layer.opacity,
                'blend_mode': str(layer.blend_mode),  # 将BlendMode转换为字符串
                'top': layer.top,
                'left': layer.left,
                'bottom': layer.bottom,
                'right': layer.right,
                'width': layer.width,
                'height': layer.height,
                'type': layer.__class__.__name__,
                'path': layer_path,  # 添加图层路径，确保唯一标识
                'index': i  # 添加图层索引，用于保留原始图层顺序
            }
            
            # 如果是图层组，递归处理子图层
            if isinstance(layer, psd_tools.api.layers.Group):
                layer_info['type'] = 'Group'
                layer_info['children'] = extract_layer_info(layer, layer, layer_path, used_names)
            
            layer_info_list.append(layer_info)
        
        return layer_info_list
    
    # 提取所有图层信息
    info['layers'] = extract_layer_info(psd, None, '', {})
    
    return info

def save_layer_images(psd_path, output_dir):
    """将PSD文件的每个图层保存为单独的图片，包括图层组和子图层"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开PSD文件
    psd = PSDImage.open(psd_path)
    
    # 递归保存图层
    def save_layers(layers, parent_path='', parent_dir='', used_names=None):
        # 初始化已使用名称字典
        if used_names is None:
            used_names = {}
            
        for i, layer in enumerate(layers):
            # 创建图层保存路径
            layer_name = layer.name.replace('/', '_').replace('\\', '_')
            if parent_path:
                layer_path = f"{parent_path}/{layer_name}"
            else:
                layer_path = layer_name
                
            # 检查是否与父层同名，如果是则添加后缀
            save_name = layer_name
            if parent_dir:
                parent_basename = os.path.basename(parent_dir)
                if save_name == parent_basename:
                    # 获取当前路径下已使用的后缀数
                    parent_key = parent_dir if parent_dir else ''
                    if parent_key not in used_names:
                        used_names[parent_key] = {}
                    
                    if save_name not in used_names[parent_key]:
                        used_names[parent_key][save_name] = 0
                    
                    suffix_num = used_names[parent_key][save_name] + 1
                    used_names[parent_key][save_name] = suffix_num
                    save_name = f"{layer_name}_sub_{suffix_num}"
            
            # 创建文件系统保存路径
            if parent_dir:
                save_dir = os.path.join(parent_dir, save_name)
            else:
                save_dir = save_name
            
            # 检查是否是图层组
            is_group = isinstance(layer, psd_tools.api.layers.Group)
            
            # 如果是图层组，创建目录并保存合成图像和元数据
            if is_group:
                # 为图层组创建目录
                group_dir = os.path.join(output_dir, save_dir)
                os.makedirs(group_dir, exist_ok=True)
                
                try:
                    # 渲染图层组合成图像
                    layer_image = layer.composite()
                    
                    # 保存合成图像到图层组目录，使用可能添加了后缀的名称
                    save_basename = os.path.basename(save_dir)
                    composite_path = os.path.join(group_dir, f"{save_basename}.png")
                    layer_image.save(composite_path)
                    print(f"已保存图层组合成图像到: {save_dir}/{save_basename}.png")
                    
                    # 提取并保存图层组元数据
                    metadata = {
                        'name': layer.name,
                        'visible': layer.is_visible(),
                        'opacity': layer.opacity,
                        'blend_mode': str(layer.blend_mode),
                        'top': layer.top,
                        'left': layer.left,
                        'bottom': layer.bottom,
                        'right': layer.right,
                        'width': layer.width,
                        'height': layer.height,
                        'type': 'Group',
                        'children_count': len(list(layer)),
                        'path': layer_path,
                        'index': i  # 添加图层索引，用于保留原始图层顺序
                    }
                    
                    # 保存元数据到JSON文件，使用可能添加了后缀的名称
                    save_basename = os.path.basename(save_dir)
                    metadata['save_name'] = save_basename  # 添加保存名称到元数据
                    metadata_path = os.path.join(group_dir, f"{save_basename}.json")
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    print(f"已保存图层组元数据到: {save_dir}/{save_basename}.json")
                    
                    if not layer.is_visible():
                        print(f"已保存不可见图层组: {layer_name}")
                except Exception as e:
                    print(f"无法渲染图层组 {layer_name}: {e}")
                    
                # 递归处理子图层
                save_layers(layer, layer_path, save_dir, used_names)
            else:
                # 非图层组，只处理最深层的图层
                # 为非图层组创建目录
                layer_dir = os.path.join(output_dir, save_dir)
                os.makedirs(layer_dir, exist_ok=True)
                
                try:
                    # 尝试直接渲染图层，忽略可见性
                    layer_image = layer.composite()
                    
                    # 保存为PNG，保留透明度
                    save_basename = os.path.basename(save_dir)
                    image_path = os.path.join(layer_dir, f"{save_basename}.png")
                    layer_image.save(image_path)
                    
                    # 保存图层元数据
                    metadata = {
                        'name': layer.name,
                        'save_name': save_name,  # 添加保存名称到元数据
                        'visible': layer.is_visible(),
                        'opacity': layer.opacity,
                        'blend_mode': str(layer.blend_mode),
                        'top': layer.top,
                        'left': layer.left,
                        'bottom': layer.bottom,
                        'right': layer.right,
                        'width': layer.width,
                        'height': layer.height,
                        'type': layer.__class__.__name__,
                        'path': layer_path,
                        'index': i
                    }
                    
                    # 保存元数据到JSON文件
                    metadata_path = os.path.join(layer_dir, f"{save_basename}.json")
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    print(f"已保存图层元数据到: {save_dir}/{save_basename}.json")
                    
                    if not layer.is_visible():
                        print(f"已保存不可见图层: {layer_name}")
                except Exception as e:
                    # 如果无法渲染，创建一个空白图像，标记图层类型
                    try:
                        # 创建一个带有图层信息的空白图像
                        width = max(1, layer.width)
                        height = max(1, layer.height)
                        empty_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                        
                        # 添加图层类型文本
                        layer_type = layer.__class__.__name__
                        
                        # 确保图层目录存在
                        layer_dir = os.path.join(output_dir, save_dir)
                        os.makedirs(layer_dir, exist_ok=True)
                        
                        # 保存空白图像
                        save_basename = os.path.basename(save_dir)
                        image_path = os.path.join(layer_dir, f"{save_basename}.png")
                        empty_image.save(image_path)
                        
                        # 保存图层元数据
                        metadata = {
                            'name': layer.name,
                            'save_name': save_name,  # 添加保存名称到元数据
                            'visible': layer.is_visible(),
                            'opacity': layer.opacity,
                            'blend_mode': str(layer.blend_mode),
                            'top': layer.top,
                            'left': layer.left,
                            'bottom': layer.bottom,
                            'right': layer.right,
                            'width': layer.width,
                            'height': layer.height,
                            'type': layer_type,
                            'path': layer_path,
                            'index': i,
                            'render_error': str(e)  # 记录渲染错误信息
                        }
                        
                        # 保存元数据到JSON文件
                        save_basename = os.path.basename(save_dir)
                        metadata_path = os.path.join(layer_dir, f"{save_basename}.json")
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, ensure_ascii=False, indent=2)
                        print(f"已保存无法渲染图层的元数据到: {save_dir}/{save_basename}.json")
                        
                        print(f"已创建空白图像代替无法渲染的图层 {layer_name} (类型: {layer_type}): {e}")
                    except Exception as inner_e:
                        print(f"无法为图层 {layer_name} 创建空白图像: {inner_e}")
    
    # 保存所有图层
    save_layers(psd, '', '', {})
    
    # 保存整个PSD的合成图像和元数据
    try:
        composite = psd.composite()
        psd_name = os.path.basename(psd_path).replace('.psd', '')
        composite_path = os.path.join(output_dir, f"{psd_name}.png")
        composite.save(composite_path)
        print(f"已保存PSD合成图像到: {psd_name}.png")
        
        # 保存整个PSD的元数据
        root_metadata = {
            'name': os.path.basename(psd_path),
            'width': psd.width,
            'height': psd.height,
            'color_mode': str(psd.color_mode),
            'layer_count': len(list(psd.descendants())),
            'visible_layer_count': len([l for l in psd.descendants() if l.is_visible()]),
            'group_count': len([l for l in psd.descendants() if isinstance(l, psd_tools.api.layers.Group)])
        }
        
        metadata_path = os.path.join(output_dir, f"{psd_name}.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(root_metadata, f, ensure_ascii=False, indent=2)
        print(f"已保存PSD元数据到: {psd_name}.json")
    except Exception as e:
        print(f"无法保存PSD合成图像或元数据: {e}")

def print_psd_info(psd_path):
    """打印PSD文件的详细信息，包括所有图层的结构和属性"""
    # 打开PSD文件
    psd = PSDImage.open(psd_path)
    
    # 打印基本信息
    print("\n" + "=" * 50)
    print(f"PSD文件: {os.path.basename(psd_path)}")
    print(f"尺寸: {psd.width} x {psd.height} 像素")
    print(f"颜色模式: {psd.color_mode}")
    print("=" * 50)
    
    # 初始化深度统计
    depth_stats = {}
    
    # 递归打印图层信息
    def print_layer(layer, indent=0, depth=0):
        # 更新深度统计
        depth_stats[depth] = depth_stats.get(depth, 0) + 1
            
        # 图层基本信息
        visibility = "可见" if layer.is_visible() else "隐藏"
        opacity_percent = round(layer.opacity / 2.55) if hasattr(layer, 'opacity') else 100
        layer_type = layer.__class__.__name__
        
        # 检查是否是图层组
        is_group = isinstance(layer, psd_tools.api.layers.Group)
        if is_group:
            layer_type = "Group"
        
        # 打印图层信息
        prefix = "  " * indent
        print(f"{prefix}├─ {layer.name} [{visibility}] [{opacity_percent}%] [{layer_type}]")
        
        # 打印图层详细属性
        detail_prefix = "  " * (indent + 1)
        print(f"{detail_prefix}位置: 左={layer.left}, 上={layer.top}, 右={layer.right}, 下={layer.bottom}")
        print(f"{detail_prefix}尺寸: {layer.width} x {layer.height} 像素")
        print(f"{detail_prefix}混合模式: {layer.blend_mode}")
        
        # 打印其他可用属性
        if hasattr(layer, 'has_pixels') and callable(layer.has_pixels):
            has_pixels = layer.has_pixels()
            print(f"{detail_prefix}包含像素数据: {'是' if has_pixels else '否'}")
        
        # 如果是图层组，递归打印子图层
        if is_group:
            # 使用正确的方法访问子图层
            for child_layer in layer:
                print_layer(child_layer, indent + 1, depth + 1)
    
    # 打印所有图层
    print("\n图层结构:")
    for layer in psd:
        print_layer(layer, 0, 0)
    
    # 打印统计信息
    total_layers = len(list(psd.descendants()))
    visible_layers = len([l for l in psd.descendants() if l.is_visible()])
    pixel_layers = len([l for l in psd.descendants() if hasattr(l, 'has_pixels') and callable(l.has_pixels) and l.has_pixels()])
    
    # 修复图层组计数 - 使用更可靠的方法
    group_count = 0
    for layer in psd.descendants():
        # 检查图层类型是否为Group
        if isinstance(layer, psd_tools.api.layers.Group):
            group_count += 1
    
    # 计算调整图层数量
    adjustment_layer_count = len([l for l in psd.descendants() if any(adj_type in l.__class__.__name__ for adj_type in ['Adjustment', 'Hue', 'Brightness', 'Levels', 'Curves', 'Exposure', 'Vibrance', 'ColorBalance'])])
    
    # 计算智能对象数量
    smart_object_count = len([l for l in psd.descendants() if l.__class__.__name__ == 'SmartObjectLayer'])
    
    # 计算文本图层数量
    text_layer_count = len([l for l in psd.descendants() if l.__class__.__name__ == 'TypeLayer'])
    
    # 计算形状图层数量
    shape_layer_count = len([l for l in psd.descendants() if l.__class__.__name__ == 'ShapeLayer'])
    
    # 计算最大嵌套深度
    max_depth = max(depth_stats.keys()) if depth_stats else 0
    
    print("\n" + "=" * 50)
    print(f"统计信息:")
    print(f"总图层数: {total_layers}")
    print(f"可见图层数: {visible_layers}")
    print(f"不可见图层数: {total_layers - visible_layers}")
    print(f"包含像素的图层数: {pixel_layers}")
    print(f"图层组数: {group_count}")
    print(f"调整图层数: {adjustment_layer_count}")
    print(f"智能对象数: {smart_object_count}")
    print(f"文本图层数: {text_layer_count}")
    print(f"形状图层数: {shape_layer_count}")
    print(f"最大嵌套深度: {max_depth}")
    
    # 打印深度统计
    print("\n图层深度分布:")
    for depth, count in sorted(depth_stats.items()):
        print(f"  深度 {depth}: {count} 个图层")
    
    print("=" * 50 + "\n")

    # 打印额外的图层属性信息
    print("\n图层属性详情:")
    print("=" * 50)
    
    # 获取所有图层类型
    layer_types = set(l.__class__.__name__ for l in psd.descendants())
    print(f"图层类型: {', '.join(layer_types)}")
    
    # 获取所有混合模式
    blend_modes = set(str(l.blend_mode) for l in psd.descendants() if hasattr(l, 'blend_mode'))
    print(f"混合模式: {', '.join(blend_modes)}")
    
    # 打印调整图层信息
    adjustment_layers = [l for l in psd.descendants() if 'adjustment' in l.__class__.__name__.lower() or not hasattr(l, 'has_pixels') or (hasattr(l, 'has_pixels') and callable(l.has_pixels) and not l.has_pixels())]
    print(f"\n调整图层或无像素图层数量: {len(adjustment_layers)}")
    if adjustment_layers:
        print("调整图层列表:")
        for i, layer in enumerate(adjustment_layers[:10], 1):  # 只显示前10个
            layer_type = "Group" if hasattr(layer, 'layers') and layer.layers else layer.__class__.__name__
            print(f"  {i}. {layer.name} [{layer_type}]")
        if len(adjustment_layers) > 10:
            print(f"  ... 还有 {len(adjustment_layers) - 10} 个调整图层")
    
    print("=" * 50 + "\n")

def main():
    # 设置PSD文件路径
    psd_path = "/Users/zhouke/Documents/project/fairy/data/psd/武将觐见617.psd"
    output_dir = "/Users/zhouke/Documents/project/fairy/data/image/layers"
    
    # 打印PSD详细信息
    print_psd_info(psd_path)
    
    # 解析PSD文件
    psd_info = parse_psd(psd_path)
    
    # 将解析结果保存为JSON文件
    with open("/Users/zhouke/Documents/project/fairy/data/image/psd_info.json", 'w', encoding='utf-8') as f:
        json.dump(psd_info, f, ensure_ascii=False, indent=2)
    
    print(f"PSD信息已保存到 psd_info.json")
    
    # 保存图层为单独的图片
    save_layer_images(psd_path, output_dir)
    print(f"图层已保存到 {output_dir}")

if __name__ == "__main__":
    main()