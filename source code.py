import sys
import os
import fitz  # PyMuPDF 
import platform
import subprocess
import re  # 引入正则表达式模块
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QFileDialog, QMessageBox, QSpinBox, QHBoxLayout, QDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont


def is_dark_mode():
    """
    检测系统是否处于深色模式。
    目前支持 Windows 和 macOS。
    """
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            key = winreg.OpenKey(registry, key_path)
            # 0: Dark mode, 1: Light mode
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception as e:
            print(f"无法检测 Windows 主题: {e}")
            return False  # 默认浅色模式
    elif system == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() == "Dark"
        except Exception as e:
            print(f"无法检测 macOS 主题: {e}")
            return False  # 默认浅色模式
    else:
        # 其他系统默认浅色模式
        return False


def set_global_font(app):
    """
    根据操作系统设置全局字体。
    Windows: Segoe UI
    macOS: Helvetica
    其他系统: Arial
    """
    system = platform.system()
    if system == "Windows":
        font_family = "Segoe UI"
    elif system == "Darwin":
        font_family = "Helvetica"
    else:
        font_family = "Arial"

    app.setFont(QFont(font_family, 10))


class ErrorDialog(QDialog):
    """
    自定义对话框，用于显示错误信息。
    包含一个只读的 QTextEdit，支持滚动。
    """

    def __init__(self, errors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("错误报告")
        self.resize(600, 400)
        layout = QVBoxLayout()

        label = QLabel("以下是处理过程中遇到的错误：")
        label.setFont(QFont("", 12))  # 使用全局字体
        layout.addWidget(label)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText("\n".join(errors))
        layout.addWidget(self.text_edit)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

        self.setLayout(layout)


class PDFOutlineTool(QWidget):
    BUTTON_YELLOW = "#FF9800"  # 与“添加大纲”按钮相同的黄色

    def __init__(self):
        super().__init__()
        self.setWindowTitle('(❁´◡`❁)(❀^‿^)')
        self.resize(800, 600)
        self.setAcceptDrops(True)
        self.init_ui()
        self.current_theme = is_dark_mode()
        self.apply_system_theme()
        self.init_theme_checker()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 20, 30, 20)

        # 标题
        title_label = QLabel("PDF 大纲添加工具")
        title_font = QFont()  # 使用全局字体
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 输入 PDF 文件部分
        input_layout = QVBoxLayout()
        self.input_label = QLabel("PDF 要放在这里")
        self.input_label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.input_label)
        self.input_label.setFixedHeight(150)

        self.input_line_edit = QLabel("")
        self.input_line_edit.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.input_line_edit)

        browse_button = QPushButton("浏览 PDF 文件")
        browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.BUTTON_YELLOW};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #FFA726;
            }}
        """)
        browse_button.clicked.connect(self.browse_input_pdf)
        input_layout.addWidget(browse_button, alignment=Qt.AlignCenter)
        main_layout.addLayout(input_layout)

        # 页码偏移设置
        offset_layout = QHBoxLayout()
        offset_layout.setSpacing(10)
        offset_label = QLabel("页码偏移量：")
        offset_label.setFont(QFont())  # 使用全局字体
        self.offset_spin_box = QSpinBox()
        self.offset_spin_box.setRange(-1000, 1000)
        self.offset_spin_box.setValue(0)  # 默认值为 0
        self.offset_spin_box.setFixedWidth(80)
        offset_layout.addWidget(offset_label)
        offset_layout.addWidget(self.offset_spin_box)
        offset_layout.addStretch()
        main_layout.addLayout(offset_layout)

        # 目录内容部分
        toc_layout = QVBoxLayout()
        toc_label = QLabel("目录内容：")
        toc_label.setFont(QFont())  # 使用全局字体
        self.toc_text_edit = QTextEdit()
        self.toc_text_edit.setPlaceholderText("目录会出现在这里\n你可以改它....")
        toc_layout.addWidget(toc_label)
        toc_layout.addWidget(self.toc_text_edit)
        main_layout.addLayout(toc_layout)

        # 添加大纲按钮
        process_button = QPushButton("✅ 添加大纲")
        process_button.setFixedHeight(40)
        process_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.BUTTON_YELLOW};
                color: white;
                border: none;
                padding: 10px 30px;
                font-size: 16px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #FFA726;
            }}
        """)
        process_button.clicked.connect(self.process)
        main_layout.addWidget(process_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def apply_system_theme(self):
        """
        根据系统主题应用相应的样式表。
        """
        if self.current_theme:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def apply_light_mode(self):
        """
        应用浅色模式的样式表。
        """
        light_palette = QPalette()

        # 设置窗口背景颜色
        light_palette.setColor(QPalette.Window, QColor(255, 255, 255))
        light_palette.setColor(QPalette.WindowText, QColor(33, 33, 33))
        light_palette.setColor(QPalette.Base, QColor(245, 245, 245))
        light_palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ToolTipText, QColor(33, 33, 33))
        light_palette.setColor(QPalette.Text, QColor(33, 33, 33))
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ButtonText, QColor(33, 33, 33))
        light_palette.setColor(QPalette.BrightText, Qt.red)

        light_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        light_palette.setColor(QPalette.HighlightedText, Qt.white)

        self.setPalette(light_palette)

        # 应用样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                color: #24292E;
                font-family: inherit;
            }
            QLabel {
                font-size: 14px;
                color: #24292E;
            }
            QTextEdit {
                font-size: 14px;
                color: #24292E;
                background-color: #FFFFFF;
                border: 1px solid #D0D7DE;
                border-radius: 6px;
            }
            QPushButton {
                font-size: 14px;
            }
        """)

        # 设置 input_label 和 toc_text_edit 的样式
        self.input_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {self.BUTTON_YELLOW};
                border-radius: 6px;
                background-color: #F6F8FA;
                color: #57606A;
                font-size: 16px;
            }}
        """)
        self.toc_text_edit.setStyleSheet(f"""
            QTextEdit {{
                font-size: 14px;
                color: #24292E;
                background-color: #FFFFFF;
                border: 1px solid #D0D7DE;
                border-radius: 6px;
            }}
        """)

    def apply_dark_mode(self):
        """
        应用深色模式的样式表。
        """
        dark_palette = QPalette()

        # 设置窗口背景颜色
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, Qt.red)

        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

        # 应用样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                font-family: inherit;
            }
            QLabel {
                font-size: 14px;
                color: #FFFFFF;
            }
            QTextEdit {
                font-size: 14px;
                color: #FFFFFF;
                background-color: #3C3C3C;
                border: 1px solid #5C5C5C;
                border-radius: 6px;
            }
            QPushButton {
                font-size: 14px;
            }
        """)

        # 设置 input_label 和 toc_text_edit 的样式
        self.input_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {self.BUTTON_YELLOW};
                border-radius: 6px;
                background-color: #424242;
                color: #FFA726;
                font-size: 16px;
            }}
        """)
        self.toc_text_edit.setStyleSheet(f"""
            QTextEdit {{
                font-size: 14px;
                color: #FFFFFF;
                background-color: #3C3C3C;
                border: 1px solid #5C5C5C;
                border-radius: 6px;
            }}
        """)

    def init_theme_checker(self):
        """
        初始化定时器，定期检查系统主题是否变化。
        """
        self.theme_timer = QTimer()
        self.theme_timer.timeout.connect(self.check_theme_change)
        self.theme_timer.start(1000)  # 每秒检查一次

    def check_theme_change(self):
        """
        检查系统主题是否变化，如果变化则应用相应的样式。
        """
        current = is_dark_mode()
        if current != self.current_theme:
            self.current_theme = current
            self.apply_system_theme()

    def dragEnterEvent(self, event):
        """
        处理拖入事件，接受拖入的 PDF 文件。
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()
                if self.current_theme:
                    # 深色模式拖放样式
                    self.input_label.setStyleSheet(f"""
                        QLabel {{
                            border: 2px dashed {self.BUTTON_YELLOW};
                            border-radius: 6px;
                            background-color: #424242;
                            color: {self.BUTTON_YELLOW};
                            font-size: 16px;
                        }}
                    """)
                else:
                    # 浅色模式拖放样式
                    self.input_label.setStyleSheet(f"""
                        QLabel {{
                            border: 2px dashed {self.BUTTON_YELLOW};
                            border-radius: 6px;
                            background-color: #E7F0FF;
                            color: {self.BUTTON_YELLOW};
                            font-size: 16px;
                        }}
                    """)
                self.input_label.setText("释放鼠标以导入 PDF 文件")
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """
        当拖放操作离开窗口时，恢复样式。
        """
        self.reset_input_label_style()

    def dropEvent(self, event):
        """
        处理文件拖放事件，自动识别并加载 PDF 文件。
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith('.pdf'):
                    self.load_pdf(file_path)
        # 恢复样式
        self.reset_input_label_style()

    def reset_input_label_style(self):
        """
        重置拖放区域的样式和文本。
        """
        if self.current_theme:
            # 深色模式样式
            self.input_label.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {self.BUTTON_YELLOW};
                    border-radius: 6px;
                    background-color: #2D2D2D;
                    color: #57606A;
                    font-size: 16px;
                }}
            """)
            self.toc_text_edit.setStyleSheet(f"""
                QTextEdit {{
                    font-size: 14px;
                    color: #FFFFFF;
                    background-color: #3C3C3C;
                    border: 1px solid #5C5C5C;
                    border-radius: 6px;
                }}
            """)
        else:
            # 浅色模式样式
            self.input_label.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {self.BUTTON_YELLOW};
                    border-radius: 6px;
                    background-color: #F6F8FA;
                    color: #57606A;
                    font-size: 16px;
                }}
            """)
            self.toc_text_edit.setStyleSheet(f"""
                QTextEdit {{
                    font-size: 14px;
                    color: #24292E;
                    background-color: #FFFFFF;
                    border: 1px solid #D0D7DE;
                    border-radius: 6px;
                }}
            """)
        self.input_label.setText("拖放 PDF 文件到此窗口")

    def browse_input_pdf(self):
        """
        浏览选择输入的 PDF 文件，并加载现有目录。
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择输入 PDF 文件", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        """
        加载 PDF 文件并读取其目录。
        """
        self.input_line_edit.setText(file_path)
        self.input_label.setText(f"已加载文件：{os.path.basename(file_path)}")
        self.input_pdf_path = file_path
        self.load_existing_toc(file_path)

    def load_existing_toc(self, file_path):
        """
        读取并显示 PDF 文件中现有的目录（如果有）。
        """
        try:
            doc = fitz.open(file_path)
            toc = doc.get_toc()
            doc.close()
            if toc:
                toc_text = self.toc_to_text(toc)
                self.toc_text_edit.setPlainText(toc_text)
            else:
                self.toc_text_edit.clear()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取 PDF 文件的目录：{str(e)}")

    def toc_to_text(self, toc):
        """
        将 PyMuPDF 获取的目录列表转换为文本格式，便于显示和编辑。
        """
        lines = []
        for entry in toc:
            level, title, page = entry
            indent = ' ' * 4 * (level - 1)  # 每级缩进 4 个空格
            line = f"{indent}{title}  {page}"
            lines.append(line)
        return '\n'.join(lines)

    def process(self):
        """
        处理添加大纲的主要逻辑。
        """
        try:
            input_pdf = self.input_pdf_path
        except AttributeError:
            QMessageBox.warning(self, "输入缺失", "请先拖放或选择一个 PDF 文件。")
            return

        page_offset = self.offset_spin_box.value()
        toc_text = self.toc_text_edit.toPlainText().strip()

        # 验证输入文件
        if not os.path.isfile(input_pdf):
            QMessageBox.warning(self, "文件错误", "输入的 PDF 文件不存在。")
            return
        if not toc_text:
            QMessageBox.warning(self, "目录缺失", "请输入目录内容。")
            return

        # 自动生成输出文件路径
        output_pdf = self.generate_output_path(input_pdf)

        # 初始化错误列表
        errors = []

        # 解析目录
        outline = self.parse_outline(toc_text, page_offset, errors)
        if not outline and not errors:
            QMessageBox.warning(self, "解析错误", "无法解析目录内容，请检查格式。")
            return

        # 添加大纲到 PDF
        try:
            self.add_outline_to_pdf(input_pdf, output_pdf, outline, errors)
            if errors:
                # 如果有错误，显示所有错误在一个滚动窗口
                error_dialog = ErrorDialog(errors, self)
                error_dialog.exec_()
                QMessageBox.information(self, "完成（含错误）", f"大纲已部分添加到\n{output_pdf}")
            else:
                QMessageBox.information(self, "完成", f"大纲已成功添加到\n{output_pdf}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理 PDF 时发生错误：{str(e)}")

    def generate_output_path(self, input_pdf):
        """
        根据输入文件路径生成输出文件路径。
        """
        dir_name, base_name = os.path.split(input_pdf)
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_含目录{ext}"
        output_pdf = os.path.join(dir_name, new_name)
        return output_pdf

    def parse_outline(self, text, page_offset, errors):
        """
        解析用户输入的目录文本，调整页码，并生成大纲列表。
        收集所有解析错误到 errors 列表。
        将每行最后的部分作为页码。
        """
        outline = []
        for idx, line in enumerate(text.split('\n'), start=1):
            line = line.rstrip()
            if not line:
                continue
            # 计算缩进以确定层级
            stripped_line = line.lstrip(' ')
            indent = len(line) - len(stripped_line)
            level = indent // 4 + 1  # 每 4 个空格为一个层级

            # 方法一：使用正则表达式提取页码
            match = re.match(r'^(.*\S)\s+(\d+)$', stripped_line)
            if match:
                title = match.group(1)
                page = match.group(2)
                try:
                    page_number = int(page) + page_offset - 1  # 调整页码，考虑 0 起始索引
                    if page_number < 0:
                        errors.append(f"行 {idx} 页码调整后小于 0：{title}")
                        continue
                except ValueError:
                    errors.append(f"行 {idx} 无法解析页码：{page}，标题：{title}")
                    continue
                outline.append({'level': level, 'title': title, 'page': page_number})
            else:
                # 方法二：按空白字符拆分，取最后一个作为页码
                tokens = stripped_line.split()
                if len(tokens) < 2:
                    errors.append(f"行 {idx} 格式错误，缺少页码：{line}")
                    continue
                page = tokens[-1]
                title = ' '.join(tokens[:-1])
                try:
                    page_number = int(page) + page_offset - 1
                    if page_number < 0:
                        errors.append(f"行 {idx} 页码调整后小于 0：{title}")
                        continue
                except ValueError:
                    errors.append(f"行 {idx} 无法解析页码：{page}，标题：{title}")
                    continue
                outline.append({'level': level, 'title': title, 'page': page_number})
        return outline

    def add_outline_to_pdf(self, input_pdf, output_pdf, outline, errors):
        """
        将大纲添加到 PDF 中并保存为新文件。
        如果 PDF 已有大纲，将其替换。
        收集所有添加大纲时的错误到 errors 列表。
        """
        doc = fitz.open(input_pdf)
        # 删除已有大纲（通过设置新的 TOC 会自动替换旧的）
        # doc.set_toc([])  # 可选：清空现有 TOC

        toc = []
        for item in outline:
            if 0 <= item['page'] < len(doc):
                toc.append([item['level'], item['title'], item['page']])
            else:
                errors.append(f"标题“{item['title']}”的页码 {item['page'] + 1} 超出 PDF 页数范围，将被忽略。")

        if toc:
            doc.set_toc(toc)
        else:
            errors.append("没有有效的大纲项被添加。")

        try:
            doc.save(output_pdf)
        except Exception as e:
            errors.append(f"保存新 PDF 文件时出错：{str(e)}")
        finally:
            doc.close()

    def mousePressEvent(self, event):
        """
        当用户点击窗口空白处时，恢复样式。
        """
        self.reset_input_label_style()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    set_global_font(app)  # 设置全局字体
    window = PDFOutlineTool()
    window.show()
    sys.exit(app.exec_())
