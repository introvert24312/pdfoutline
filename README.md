# Outline - PDF目录工具 📖

一个简单易用的PDF目录添加工具，支持拖放操作和可视化界面。

![应用界面](https://img.shields.io/badge/Platform-macOS-lightgrey?style=for-the-badge&logo=apple)
![Python版本](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ 功能特色

- 🖱️ **拖放支持** - 直接拖拽PDF文件到窗口
- 📋 **模板功能** - 一键插入标准目录格式
- ❓ **详细帮助** - 完整的格式说明和使用指南
- 🎨 **系统主题** - 自动适配明暗主题
- ⚡ **实时预览** - 显示现有PDF目录结构
- 🛠️ **页码偏移** - 灵活的页码调整功能
- 🚀 **原生体验** - 完全独立的macOS应用

## 🎯 格式要求

### 目录格式规则

```
标题 页码
```

- **层级缩进**：每4个空格代表一个层级
- **标题页码**：标题后跟空格和页码数字
- **支持中英文**：完全支持中英文混合标题

### 示例格式

```
第一章 营养学基础  1
一、概述  1
    1.1 食物成分  1
        1.1.1 营养素种类及分类  1
        1.1.2 水及其他膳食成分  1
    1.2 人体营养需要  2
        1.2.1 营养素的代谢及生理功能  2
        1.2.2 营养对人体构成的影响  2
二、营养素的代谢及生理功能  1
    2.1 营养素的代谢  1
    2.2 营养素的生理功能  2
```

## 🚀 快速开始

### 方法一：下载已打包应用（推荐）

1. 前往 [Releases](https://github.com/introvert24312/pdfoutline/releases) 页面
2. 下载最新版本的 `Outline.app.zip`
3. 解压后双击 `Outline.app` 运行
4. 可选：拖拽到Applications文件夹安装

> **⚠️ 启动提示**：由于macOS安全机制，第一次打开可能失败，请再次双击启动。如遇问题，请右键点击应用选择"打开"。

### 方法二：从源码运行

#### 环境要求

- macOS 10.14+
- Python 3.8+
- PyQt5
- PyMuPDF (fitz)

#### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/introvert24312/pdfoutline.git
cd pdfoutline

# 创建虚拟环境
python3 -m venv pdf_env
source pdf_env/bin/activate

# 安装依赖
pip install PyMuPDF PyQt5

# 运行应用
python "source code.py"
```

## 📖 使用指南

### 基本操作

1. **加载PDF文件**
   - 方式一：拖拽PDF文件到窗口
   - 方式二：点击"浏览PDF文件"按钮选择

2. **编辑目录内容**
   - 点击"📋 使用模板"获取格式示例
   - 点击"❓ 格式说明"查看详细规则
   - 在文本框中编辑目录内容

3. **设置页码偏移**
   - 根据需要调整"页码偏移量"
   - 用于匹配PDF实际页码

4. **生成目录PDF**
   - 点击"✅ 添加大纲"按钮
   - 自动生成带目录的新PDF文件

### 高级功能

- **现有目录读取**：自动读取PDF中已有的目录结构
- **错误报告**：详细的格式错误提示和处理建议
- **容错处理**：部分错误不会阻止整体处理过程

## 🔧 常见问题

### 应用无法启动？

macOS可能阻止未签名应用运行：

1. **方法一**：再次双击应用图标
2. **方法二**：右键点击应用 → 选择"打开"
3. **方法三**：系统偏好设置 → 安全性与隐私 → 允许从以下位置下载的应用 → 任何来源

### 转换格式工具

如需转换其他格式的目录，可以使用 [这个工具](https://github.com/introvert24312/dingzhen)

## 🛠️ 开发构建

### 打包为macOS应用

```bash
# 激活虚拟环境
source pdf_env/bin/activate

# 安装打包工具
pip install pyinstaller

# 执行打包
python build_app.py
```

打包后的应用位于 `dist/Outline.app`

### 自定义图标

将图标文件命名为 `app_icon.icns` 并放在项目根目录，重新运行打包脚本即可。

## 📁 项目结构

```
pdfoutline/
├── source code.py          # 主程序文件
├── build_app.py           # 打包脚本
├── create_icon.py         # 图标生成脚本
├── app_icon.icns          # 应用图标
├── pdf_env/               # Python虚拟环境
├── dist/                  # 打包输出目录
│   └── Outline.app       # 打包后的应用
└── README.md              # 项目说明
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF处理库
- [PyQt5](https://pypi.org/project/PyQt5/) - GUI框架
- [PyInstaller](https://pyinstaller.org/) - 应用打包工具

## 📞 支持

如遇到问题或有建议，请：

1. 查看 [Issues](https://github.com/introvert24312/pdfoutline/issues) 页面
2. 创建新的Issue描述问题
3. 参考应用内的"❓ 格式说明"

---

<div align="center">

**[⬆ 回到顶部](#outline---pdf目录工具-)**

Made with ❤️ by [introvert24312](https://github.com/introvert24312)

</div>

