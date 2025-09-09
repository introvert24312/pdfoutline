#!/usr/bin/env python3
"""
PDF目录工具 - macOS打包脚本
使用PyInstaller将Python应用打包成macOS .app文件
"""

import os
import subprocess
import sys

def build_app():
    """构建macOS应用"""
    
    # 应用配置
    app_name = "Outline"
    script_name = "source code.py"
    
    # 检查图标文件
    icon_path = "app_icon.icns"
    if not os.path.exists(icon_path):
        print(f"⚠️  图标文件不存在: {icon_path}")
        icon_args = []
    else:
        print(f"🎨 使用图标: {icon_path}")
        icon_args = [f"--icon={icon_path}"]
    
    # PyInstaller参数（使用onedir模式提高启动速度）
    pyinstaller_args = [
        "pyinstaller",
        "--onedir",                     # 打包成文件夹（更快启动）
        "--windowed",                   # 无控制台窗口
        f"--name={app_name}",          # 应用名称
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 不询问覆盖
        "--optimize=2",                 # 优化Python字节码
        "--exclude-module=matplotlib",  # 排除不需要的模块
        "--exclude-module=numpy",       # 排除不需要的模块
        "--exclude-module=scipy",       # 排除不需要的模块
        *icon_args,                     # 添加图标参数
        script_name
    ]
    
    print(f"🚀 开始打包 {app_name}...")
    print(f"📁 源文件: {script_name}")
    
    try:
        # 执行打包
        result = subprocess.run(pyinstaller_args, check=True, capture_output=True, text=True)
        
        print("✅ 打包成功！")
        print(f"📦 应用位置: dist/{app_name}.app")
        print("\n💡 使用说明:")
        print(f"   双击 dist/{app_name}.app 运行应用")
        print("   可以将.app文件移动到Applications文件夹")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    if not os.path.exists("source code.py"):
        print("❌ 找不到源文件 'source code.py'")
        sys.exit(1)
    
    build_app()