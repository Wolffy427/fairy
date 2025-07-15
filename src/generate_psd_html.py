#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from psd_html_generator import generate_psd_html

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
    
    # 确保输入文件存在
    if not os.path.exists(args.psd_info):
        print(f"错误: PSD信息文件不存在: {args.psd_info}")
        return
    
    if not os.path.exists(args.layers_dir):
        print(f"错误: 图层目录不存在: {args.layers_dir}")
        return
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 生成HTML
    generate_psd_html(args.psd_info, args.layers_dir, args.output_file)
    print(f"HTML生成成功: {args.output_file}")
    print("你可以在浏览器中打开此文件查看PSD布局")

if __name__ == "__main__":
    main()