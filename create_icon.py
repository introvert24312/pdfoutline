#!/usr/bin/env python3
"""
为PDF目录工具创建macOS应用图标
需要将源图片保存为 icon_source.png
"""

import os
import subprocess
from PIL import Image, ImageDraw

def create_rounded_icon(source_path, output_path, size=1024, corner_radius=180):
    """创建圆角矩形图标"""
    
    # 打开源图片
    img = Image.open(source_path).convert("RGBA")
    
    # 调整大小为正方形
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # 创建圆角遮罩
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size, size)], corner_radius, fill=255)
    
    # 应用遮罩
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0))
    result.putalpha(mask)
    
    # 保存
    result.save(output_path, "PNG")
    print(f"✅ 圆角图标已生成: {output_path}")

def create_iconset(png_path):
    """创建macOS图标集"""
    
    iconset_dir = "icon.iconset"
    
    # 创建iconset目录
    if os.path.exists(iconset_dir):
        subprocess.run(["rm", "-rf", iconset_dir])
    os.makedirs(iconset_dir)
    
    # macOS图标尺寸
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]
    
    # 生成各种尺寸
    base_img = Image.open(png_path).convert("RGBA")
    
    for size, filename in sizes:
        # 按比例计算圆角
        corner_radius = int(size * 0.176)  # 约18%的圆角
        
        # 调整大小
        resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # 创建圆角遮罩
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (size, size)], corner_radius, fill=255)
        
        # 应用遮罩
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.paste(resized, (0, 0))
        result.putalpha(mask)
        
        # 保存到iconset
        result.save(os.path.join(iconset_dir, filename), "PNG")
    
    print(f"✅ 图标集已创建: {iconset_dir}/")
    
    # 生成.icns文件
    try:
        subprocess.run(["iconutil", "-c", "icns", iconset_dir], check=True)
        print("✅ 图标文件已生成: icon.icns")
        return "icon.icns"
    except subprocess.CalledProcessError:
        print("❌ 生成.icns失败，但.iconset已创建")
        return None

def main():
    source_file = "icon_source.png"
    
    if not os.path.exists(source_file):
        print(f"❌ 请将源图片保存为: {source_file}")
        print("💡 步骤:")
        print("   1. 右键点击图片 → 存储图像")
        print(f"   2. 保存为: {source_file}")
        print("   3. 运行此脚本")
        return
    
    try:
        # 先创建圆角版本
        rounded_path = "icon_rounded.png"
        create_rounded_icon(source_file, rounded_path)
        
        # 创建完整的图标集
        icns_path = create_iconset(rounded_path)
        
        if icns_path:
            print("\n🎉 图标创建完成！")
            print("现在可以重新打包应用了")
            
    except ImportError:
        print("❌ 需要安装Pillow库")
        print("运行: pip install Pillow")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()