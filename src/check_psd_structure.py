from psd_tools import PSDImage

def check_psd_structure(psd_path):
    # 打开PSD文件
    psd = PSDImage.open(psd_path)
    
    print(f'根图层数: {len(list(psd))}')
    
    # 检查每个根图层
    for i, layer in enumerate(psd):
        is_group = layer.__class__.__name__ == 'Group'
        children_count = 0
        if is_group:
            try:
                children_count = len(layer.layers)
                print(f'图层 {i+1}: {layer.name}, 类型: {layer.__class__.__name__}, 子图层数: {children_count}')
                
                # 如果有子图层，递归检查
                if children_count > 0:
                    print(f'  子图层列表:')
                    for j, child in enumerate(layer.layers):
                        print(f'    子图层 {j+1}: {child.name}, 类型: {child.__class__.__name__}')
                        # 检查是否有更深层次的嵌套
                        if child.__class__.__name__ == 'Group' and hasattr(child, 'layers') and len(child.layers) > 0:
                            print(f'      有更深层次的嵌套!')
            except Exception as e:
                print(f'图层 {i+1}: {layer.name}, 类型: {layer.__class__.__name__}, 访问子图层时出错: {e}')
        else:
            print(f'图层 {i+1}: {layer.name}, 类型: {layer.__class__.__name__}, 非图层组')

if __name__ == '__main__':
    psd_path = '/Users/zhouke/Documents/project/fairy/data/psd/武将觐见617.psd'
    check_psd_structure(psd_path)