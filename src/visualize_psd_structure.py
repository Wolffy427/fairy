from psd_tools import PSDImage
import os
import psd_tools.api.layers

def visualize_psd_structure(psd_path):
    """可视化PSD文件的图层结构，特别关注深度嵌套的图层"""
    # 打开PSD文件
    psd = PSDImage.open(psd_path)
    
    print(f"\n分析PSD文件: {os.path.basename(psd_path)}")
    print("=" * 50)
    
    # 用于跟踪最深嵌套的图层路径
    deepest_paths = []
    max_depth_found = [0]  # 使用列表以便在递归函数中可以修改
    
    # 递归分析图层结构
    def analyze_layer(layer, current_path=[], depth=0):
        # 更新当前路径
        path = current_path + [layer.name]
        
        # 检查是否是图层组
        is_group = isinstance(layer, psd_tools.api.layers.Group)
        
        # 更新最大深度
        if depth > max_depth_found[0]:
            max_depth_found[0] = depth
            deepest_paths.clear()  # 清除之前的路径，因为找到了更深的
        
        # 如果是当前最大深度的图层，记录路径
        if depth == max_depth_found[0] and not is_group:
            deepest_paths.append((path, depth, layer.__class__.__name__))
        
        # 如果是图层组，递归分析子图层
        if is_group:
            for child_layer in layer:
                analyze_layer(child_layer, path, depth + 1)
    
    # 分析所有根图层
    for layer in psd:
        analyze_layer(layer)
    
    # 打印最大嵌套深度
    print(f"最大嵌套深度: {max_depth_found[0]}")
    
    # 打印最深嵌套的图层路径
    print("\n最深嵌套的图层:")
    for i, (path, depth, layer_type) in enumerate(deepest_paths, 1):
        path_str = " > ".join(path)
        print(f"{i}. 深度 {depth}: {path_str} [{layer_type}]")
    
    # 打印每个深度的图层数量统计
    depth_stats = {}
    
    def count_layers_by_depth(layer, depth=0):
        # 更新深度统计
        depth_stats[depth] = depth_stats.get(depth, 0) + 1
        
        # 如果是图层组，递归计算子图层
        if isinstance(layer, psd_tools.api.layers.Group):
            for child_layer in layer:
                count_layers_by_depth(child_layer, depth + 1)
    
    # 计算所有图层的深度分布
    for layer in psd:
        count_layers_by_depth(layer)
    
    # 打印深度统计
    print("\n图层深度分布:")
    for depth, count in sorted(depth_stats.items()):
        print(f"  深度 {depth}: {count} 个图层")
    
    # 分析图层组嵌套结构
    print("\n图层组嵌套结构:")
    
    def print_group_structure(layer, indent=0, depth=0):
        # 图层基本信息
        prefix = "  " * indent
        is_group = isinstance(layer, psd_tools.api.layers.Group)
        layer_type = "Group" if is_group else layer.__class__.__name__
        
        # 打印图层信息
        print(f"{prefix}{'└─' if indent > 0 else '├─'} {layer.name} [{layer_type}] (深度: {depth})")
        
        # 如果是图层组，递归打印子图层
        if is_group:
            child_count = sum(1 for _ in layer)
            if child_count > 0:
                print(f"{prefix}  ├─ 包含 {child_count} 个子图层")
                for child_layer in layer:
                    if isinstance(child_layer, psd_tools.api.layers.Group):
                        print_group_structure(child_layer, indent + 1, depth + 1)
    
    # 只打印图层组结构
    for layer in psd:
        if isinstance(layer, psd_tools.api.layers.Group):
            print_group_structure(layer)
    
    print("=" * 50)

def main():
    # 获取PSD文件路径
    psd_path = "/Users/zhouke/Documents/project/fairy/data/psd/武将觐见617.psd"
    
    # 可视化PSD结构
    visualize_psd_structure(psd_path)

if __name__ == "__main__":
    main()