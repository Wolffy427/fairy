#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from PIL import Image, ImageChops, ImageMath
import argparse

def apply_blend_mode(base, top, blend_mode, opacity=1.0):
    """
    应用混合模式将顶层图像与基础图像混合
    
    参数:
        base: 基础图像（PIL.Image）
        top: 顶层图像（PIL.Image）
        blend_mode: 混合模式字符串
        opacity: 不透明度，范围0.0-1.0
    
    返回:
        混合后的图像
    """
    # 确保两个图像都是RGBA模式
    if base.mode != 'RGBA':
        base = base.convert('RGBA')
    if top.mode != 'RGBA':
        top = top.convert('RGBA')
    
    # 提取alpha通道
    r1, g1, b1, a1 = base.split()
    r2, g2, b2, a2 = top.split()
    
    # 如果不透明度不是100%，则调整图像的alpha通道
    if opacity < 1.0:
        # 调整alpha通道
        a2 = a2.point(lambda i: int(i * opacity))
    
    # 根据混合模式应用不同的混合算法
    if 'NORMAL' in blend_mode:
        # 正常模式，直接使用PIL的alpha合成
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将顶层图像与调整后的alpha通道合并
        top_with_opacity = Image.merge('RGBA', (r2, g2, b2, a2))
        # 将顶层图像粘贴到结果图像上
        result.paste(top_with_opacity, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'PASS_THROUGH' in blend_mode:
        # PASS_THROUGH 模式，保持图层组内部混合模式
        # 对于图层组，这意味着子图层直接与图层组外部的图层混合
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将顶层图像与调整后的alpha通道合并
        top_with_opacity = Image.merge('RGBA', (r2, g2, b2, a2))
        # 将顶层图像粘贴到结果图像上
        result.paste(top_with_opacity, (0, 0), a2)
        # 将结果与基础图像合成，使用alpha_composite确保透明度正确处理
        result = Image.alpha_composite(base, result)
    elif 'MULTIPLY' in blend_mode:
        # 正片叠底模式
        r = ImageMath.eval("convert(a*b/255, 'L')", a=r1, b=r2)
        g = ImageMath.eval("convert(a*b/255, 'L')", a=g1, b=g2)
        b = ImageMath.eval("convert(a*b/255, 'L')", a=b1, b=b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'SCREEN' in blend_mode:
        # 滤色模式
        r = ImageMath.eval("convert(255 - ((255-a)*(255-b))/255, 'L')", a=r1, b=r2)
        g = ImageMath.eval("convert(255 - ((255-a)*(255-b))/255, 'L')", a=g1, b=g2)
        b = ImageMath.eval("convert(255 - ((255-a)*(255-b))/255, 'L')", a=b1, b=b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'OVERLAY' in blend_mode:
        # 叠加模式
        r = ImageMath.eval("convert((a>128)*((255-2*(255-a))*(255-b)/255+2*a*b/255)+(a<=128)*(2*a*b/255), 'L')", a=r1, b=r2)
        g = ImageMath.eval("convert((a>128)*((255-2*(255-a))*(255-b)/255+2*a*b/255)+(a<=128)*(2*a*b/255), 'L')", a=g1, b=g2)
        b = ImageMath.eval("convert((a>128)*((255-2*(255-a))*(255-b)/255+2*a*b/255)+(a<=128)*(2*a*b/255), 'L')", a=b1, b=b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'SOFT_LIGHT' in blend_mode:
        # 柔光模式
        r = ImageMath.eval("convert((b<128)*(2*a*b/255+(a*a/255)*(255-2*b))+(b>=128)*(2*a*(255-b)/255+sqrt(a/255)*(2*b-255))*255, 'L')", a=r1, b=r2)
        g = ImageMath.eval("convert((b<128)*(2*a*b/255+(a*a/255)*(255-2*b))+(b>=128)*(2*a*(255-b)/255+sqrt(a/255)*(2*b-255))*255, 'L')", a=g1, b=g2)
        b = ImageMath.eval("convert((b<128)*(2*a*b/255+(a*a/255)*(255-2*b))+(b>=128)*(2*a*(255-b)/255+sqrt(a/255)*(2*b-255))*255, 'L')", a=b1, b=b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'HARD_LIGHT' in blend_mode:
        # 强光模式
        r = ImageMath.eval("convert((b<128)*(2*a*b/255)+(b>=128)*(255-2*(255-a)*(255-b)/255), 'L')", a=r1, b=r2)
        g = ImageMath.eval("convert((b<128)*(2*a*b/255)+(b>=128)*(255-2*(255-a)*(255-b)/255), 'L')", a=g1, b=g2)
        b = ImageMath.eval("convert((b<128)*(2*a*b/255)+(b>=128)*(255-2*(255-a)*(255-b)/255), 'L')", a=b1, b=b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'COLOR_DODGE' in blend_mode:
        # 颜色减淡模式
        def dodge(a, b):
            return ImageMath.eval("convert((b==255)*255+(b!=255)*(min(255, a*255/(255-b))), 'L')", a=a, b=b)
        
        r = dodge(r1, r2)
        g = dodge(g1, g2)
        b = dodge(b1, b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'COLOR_BURN' in blend_mode:
        # 颜色加深模式
        def burn(a, b):
            return ImageMath.eval("convert((b==0)*0+(b!=0)*(255-min(255, (255-a)*255/b)), 'L')", a=a, b=b)
        
        r = burn(r1, r2)
        g = burn(g1, g2)
        b = burn(b1, b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'DARKEN' in blend_mode:
        # 变暗模式
        r = ImageMath.eval("convert(min(a,b), 'L')", a=r1, b=r2)
        g = ImageMath.eval("convert(min(a,b), 'L')", a=g1, b=g2)
        b = ImageMath.eval("convert(min(a,b), 'L')", a=b1, b=b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    elif 'LIGHTEN' in blend_mode:
        # 变亮模式
        r = ImageMath.eval("convert(max(a,b), 'L')", a=r1, b=r2)
        g = ImageMath.eval("convert(max(a,b), 'L')", a=g1, b=g2)
        b = ImageMath.eval("convert(max(a,b), 'L')", a=b1, b=b2)
        # 创建混合结果
        blend_result = Image.merge('RGB', (r, g, b))
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将混合结果与alpha通道合并
        result.paste(blend_result, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    else:
        # 其他混合模式，默认使用正常模式
        print(f"不支持的混合模式: {blend_mode}，使用正常模式代替")
        # 创建一个与基础图像大小相同的透明图像
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        # 将顶层图像与调整后的alpha通道合并
        top_with_opacity = Image.merge('RGBA', (r2, g2, b2, a2))
        # 将顶层图像粘贴到结果图像上
        result.paste(top_with_opacity, (0, 0), a2)
        # 将结果与基础图像合成
        result = Image.alpha_composite(base, result)
    
    return result

def compose_layers(layers_dir, output_path=None):
    """
    根据图层组的JSON元数据将PNG图像拼接成一张完整的图像
    
    参数:
        layers_dir: 图层目录路径，包含图层组的PNG和JSON文件
        output_path: 输出图像的路径，如果为None，则使用layers_dir的父目录和PSD文件名
    
    返回:
        拼接后的图像路径
    """
    # 获取PSD元数据
    psd_json_path = None
    for file in os.listdir(layers_dir):
        if file.endswith('.json') and not os.path.isdir(os.path.join(layers_dir, file)):
            psd_json_path = os.path.join(layers_dir, file)
            break
    
    if not psd_json_path:
        raise FileNotFoundError(f"在 {layers_dir} 中找不到PSD元数据文件")
    
    # 读取PSD元数据
    with open(psd_json_path, 'r', encoding='utf-8') as f:
        psd_metadata = json.load(f)
    
    # 创建一个空白画布，尺寸与PSD文件相同
    canvas = Image.new('RGBA', (psd_metadata['width'], psd_metadata['height']), (0, 0, 0, 0))
    
    # 收集所有图层组信息
    layer_groups = []
    
    def collect_groups(group_dir, depth=0, parent_path=''):
        # 获取当前目录下的所有文件和子目录
        items = os.listdir(group_dir)
        
        # 处理当前目录下的图层组自身的PNG和JSON
        group_name = os.path.basename(group_dir)
        group_png = os.path.join(group_dir, f"{group_name}.png")
        group_json = os.path.join(group_dir, f"{group_name}.json")
        
        # 检查图层组的PNG和JSON是否存在
        if os.path.exists(group_png) and os.path.exists(group_json):
            # 读取图层组元数据
            with open(group_json, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 计算完整路径用于排序
            full_path = os.path.join(parent_path, group_name) if parent_path else group_name
            
            # 添加到图层组列表
            layer_groups.append({
                'path': group_dir,
                'png': group_png,
                'metadata': metadata,
                'depth': depth,
                'full_path': full_path,
                'index': metadata.get('index', 0)  # 获取图层索引，用于同级图层排序
            })
        
        # 递归处理子目录
        for item in items:
            item_path = os.path.join(group_dir, item)
            if os.path.isdir(item_path):
                new_parent_path = os.path.join(parent_path, group_name) if parent_path else group_name
                collect_groups(item_path, depth + 1, new_parent_path)
    
    # 从根目录开始收集图层组信息
    collect_groups(layers_dir)
    
    # 在PSD中，图层从下到上的顺序对应索引从小到大
    # 我们需要先渲染底层图层，然后是上层图层
    # 但是，我们需要先处理浅层图层组，再处理深层图层组
    # 因为深层图层组应该覆盖在浅层图层组上面
    # 所以按深度升序排列，对于同一深度的图层，按照索引升序排列
    layer_groups.sort(key=lambda x: (x['depth'], x['metadata'].get('index', 0)))
    
    print(f"排序后的图层组顺序:")
    for group in layer_groups:
        print(f"  - 图层组: {group['metadata']['path']}, 深度: {group['depth']}, 索引: {group['metadata'].get('index', 0)}, 可见性: {group['metadata'].get('visible', True)}")
    
    # 渲染图层组
    for group in layer_groups:
        # 检查图层是否可见
        visible = group['metadata'].get('visible', True)
        if visible:
            try:
                # 读取图层组图像
                layer_image = Image.open(group['png'])
                
                # 获取不透明度
                opacity = group['metadata'].get('opacity', 255) / 255.0
                
                # 创建一个与画布大小相同的透明图像
                temp = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
                
                # 将图层组图像粘贴到正确的位置
                temp.paste(layer_image, (group['metadata']['left'], group['metadata']['top']), layer_image)
                
                # 应用混合模式和不透明度
                blend_mode = group['metadata'].get('blend_mode', 'BlendMode.NORMAL')
                
                # 打印图层信息，帮助调试
                print(f"正在合成图层组: {group['metadata']['path']}")
                print(f"  - 深度: {group['depth']}, 索引: {group['metadata'].get('index', 0)}")
                print(f"  - 混合模式: {blend_mode}, 不透明度: {opacity:.2f}, 可见性: {visible}")
                
                # 应用混合模式和不透明度
                canvas = apply_blend_mode(canvas, temp, blend_mode, opacity)
                
                print(f"已合成图层组: {group['metadata']['path']}")
            except Exception as e:
                print(f"无法处理图层组 {os.path.basename(group['path'])}: {e}")
        else:
            print(f"跳过不可见图层组: {group['metadata']['path']}")
            print(f"  - 深度: {group['depth']}, 索引: {group['metadata'].get('index', 0)}, 可见性: {visible}")
    
    # 如果没有指定输出路径，则使用PSD文件名
    if output_path is None:
        psd_name = os.path.splitext(psd_metadata['name'])[0]
        output_path = os.path.join(os.path.dirname(layers_dir), f"{psd_name}_composed.png")
    
    # 保存拼接后的图像
    canvas.save(output_path)
    print(f"已保存拼接图像到: {output_path}")
    
    return output_path

def compare_images(image1_path, image2_path, output_path, enhance=True, side_by_side=False):
    """
    比较两个图像并生成差异图像
    
    参数:
        image1_path: 第一个图像的路径
        image2_path: 第二个图像的路径
        output_path: 输出差异图像的路径
        enhance: 是否增强差异以便更容易看到
        side_by_side: 是否生成并排比较图像
    
    返回:
        差异图像的路径
    """
    # 读取图像
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)
    
    # 确保两个图像都是RGBA模式
    if image1.mode != 'RGBA':
        image1 = image1.convert('RGBA')
    if image2.mode != 'RGBA':
        image2 = image2.convert('RGBA')
    
    # 确保两个图像尺寸相同
    if image1.size != image2.size:
        print(f"警告: 图像尺寸不同 {image1.size} vs {image2.size}，将调整第二个图像的尺寸")
        image2 = image2.resize(image1.size)
    
    # 创建差异图像
    diff = ImageChops.difference(image1, image2)
    
    if enhance:
        # 增强差异以便更容易看到
        diff = ImageChops.multiply(diff, diff)
        
        # 进一步增强差异，使用伪彩色显示
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(diff)
        diff = enhancer.enhance(2.0)  # 增加亮度
        
        # 将差异区域标记为红色
        r, g, b, a = diff.split()
        # 增强红色通道，减弱绿色和蓝色通道
        r = r.point(lambda i: min(i * 2, 255))
        g = g.point(lambda i: i // 2)
        b = b.point(lambda i: i // 2)
        diff = Image.merge('RGBA', (r, g, b, a))
    
    if side_by_side:
        # 创建并排比较图像
        width = image1.width * 3
        height = image1.height
        comparison = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        comparison.paste(image1, (0, 0))
        comparison.paste(image2, (image1.width, 0))
        comparison.paste(diff, (image1.width * 2, 0))
        
        # 添加标签
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(comparison)
        try:
            # 尝试加载系统字体，如果失败则使用默认字体
            font = ImageFont.truetype("Arial", 20)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text((10, 10), "原始图像", fill=(255, 255, 255, 255), font=font)
        draw.text((image1.width + 10, 10), "优化图像", fill=(255, 255, 255, 255), font=font)
        draw.text((image1.width * 2 + 10, 10), "差异图像", fill=(255, 255, 255, 255), font=font)
        
        # 保存并排比较图像
        comparison.save(output_path)
        print(f"已保存并排比较图像到: {output_path}")
    else:
        # 保存差异图像
        diff.save(output_path)
        print(f"已保存差异图像到: {output_path}")
    
    return output_path

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将图层组的PNG图像拼接成一张完整的图像')
    
    # 创建子解析器
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 拼接子命令
    compose_parser = subparsers.add_parser('compose', help='拼接图层组的PNG图像')
    compose_parser.add_argument('layers_dir', help='图层目录路径')
    compose_parser.add_argument('-o', '--output', help='输出图像的路径')
    
    # 比较子命令
    compare_parser = subparsers.add_parser('compare', help='比较两个图像并生成差异图像')
    compare_parser.add_argument('image1', help='第一个图像的路径')
    compare_parser.add_argument('image2', help='第二个图像的路径')
    compare_parser.add_argument('-o', '--output', help='差异图像的输出路径', default='diff.png')
    compare_parser.add_argument('--no-enhance', action='store_true', help='不增强差异图像')
    compare_parser.add_argument('--side-by-side', action='store_true', help='生成并排比较图像')
    
    # 为了向后兼容，添加全局参数
    parser.add_argument('--layers-dir', dest='compat_layers_dir', help='图层目录路径（向后兼容）')
    parser.add_argument('-o', '--output', dest='compat_output', help='输出图像的路径（向后兼容）')
    parser.add_argument('-c', '--compare', nargs=2, metavar=('IMAGE1', 'IMAGE2'), help='比较两个图像并生成差异图像（向后兼容）')
    parser.add_argument('-d', '--diff-output', help='差异图像的输出路径（向后兼容）')
    
    args = parser.parse_args()
    
    # 处理子命令
    if hasattr(args, 'command') and args.command == 'compose':
        compose_layers(args.layers_dir, args.output)
    elif hasattr(args, 'command') and args.command == 'compare':
        compare_images(args.image1, args.image2, args.output, 
                     enhance=not args.no_enhance, 
                     side_by_side=args.side_by_side)
    # 向后兼容的处理
    elif hasattr(args, 'compare') and args.compare:
        # 比较两个图像
        diff_output = args.diff_output or 'diff.png'
        compare_images(args.compare[0], args.compare[1], diff_output)
    elif hasattr(args, 'compat_layers_dir') and args.compat_layers_dir:
        # 拼接图像
        compose_layers(args.compat_layers_dir, args.compat_output)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()