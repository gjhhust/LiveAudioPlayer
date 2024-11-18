from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import LineEdit, TransparentToolButton, FluentIcon, Action, RoundMenu
import difflib
import hashlib


def get_tag_color(tag):
    """固定字符串映射到唯一颜色"""
    hash_object = hashlib.md5(tag.encode("utf-8"))
    hash_hex = hash_object.hexdigest()
    r = int(hash_hex[:2], 16) % 136 + 120
    g = int(hash_hex[2:4], 16) % 136 + 120
    b = int(hash_hex[4:6], 16) % 136 + 120
    return f"#{r:02x}{g:02x}{b:02x}"


class TagLabel(QWidget):
    tag_removed = Signal(str)

    def __init__(self, tag, parent=None):
        super().__init__(parent)
        self.tag = tag

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 2, 5, 2)  # 标签内边距
        self.layout.setSpacing(5)

        # 标签文本
        self.label = QLabel(tag, self)
        self.label.setStyleSheet(f"color: white;")
        self.layout.addWidget(self.label)

        # 右上角的删除按钮
        self.cancel_button = TransparentToolButton(FluentIcon.CLOSE, self)
        self.cancel_button.setFixedSize(12, 12)
        self.cancel_button.clicked.connect(self.remove_tag)
        self.layout.addWidget(self.cancel_button)

        self.setStyleSheet(f"background-color: {get_tag_color(tag)}; border-radius: 10px;")

    def remove_tag(self):
        self.tag_removed.emit(self.tag)
        self.deleteLater()


class TagsLineEdit(QWidget):
    tag_added = Signal(str)
    tag_removed = Signal(str)

    def __init__(self, tags_library=None, parent=None):
        super().__init__(parent)
        self.tags_show = []  # 当前显示的标签
        self.tags_library = tags_library or []  # 全部标签库

        # 主布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # 标签显示区域
        self.tags_layout = QHBoxLayout()
        self.tags_layout.setSpacing(5)

        # 输入框
        self.line_edit = LineEdit(self)
        self.line_edit.setPlaceholderText("")
        self.line_edit.textChanged.connect(self.update_menu)
        self.line_edit.returnPressed.connect(self.add_tag_from_input)

        self.layout.addLayout(self.tags_layout)
        self.layout.addWidget(self.line_edit)

        # Accept 按钮
        self.accept_button = TransparentToolButton(FluentIcon.ACCEPT, self)
        self.accept_button.setFixedSize(20, 20)
        self.accept_button.clicked.connect(self.add_tag_from_input)
        self.layout.addWidget(self.accept_button)

        # 搜索结果菜单
        self.round_menu = RoundMenu(self)
        self.round_menu.triggered.connect(self.on_menu_action_triggered)

    def add_tag(self, tag):
        """添加一个标签到显示区域和标签库"""
        if tag not in self.tags_show:
            tag_label = TagLabel(tag, self)
            tag_label.tag_removed.connect(self.remove_tag)

            # 插入到标签显示区域
            self.tags_layout.addWidget(tag_label)
            self.tags_show.append(tag)

            # 如果新标签不在标签库中，添加进去
            if tag not in self.tags_library:
                self.tags_library.append(tag)

            self.tag_added.emit(tag)

    def remove_tag(self, tag):
        """从显示区域和标签列表中移除一个标签"""
        if tag in self.tags_show:
            self.tags_show.remove(tag)
            self.tag_removed.emit(tag)

    def update_menu(self):
        """根据输入内容更新 RoundMenu"""
        input_text = self.line_edit.text().strip().lower()
        if not input_text:
            self.round_menu.hide()
            return

        matching_tags = self.get_matching_tags(input_text)
        self.round_menu.clear()

        # 插入匹配结果
        actions = [Action(FluentIcon.TAG, tag, triggered=lambda t=tag: self.add_tag(t)) for tag in matching_tags]
        self.round_menu.addActions(actions)

        if actions:
            # 设置 RoundMenu 的位置并显示
            self.round_menu.move(self.mapToGlobal(self.line_edit.geometry().bottomLeft()))
            self.round_menu.show()


    def get_matching_tags(self, input_text):
        """获取与输入匹配的标签列表"""
        return sorted(
            self.tags_library,
            key=lambda tag: difflib.SequenceMatcher(None, input_text, tag).ratio(),
            reverse=True
        )

    def add_tag_from_input(self):
        """从输入框中添加标签"""
        tag = self.line_edit.text().strip()
        if tag:
            self.add_tag(tag)
        self.line_edit.clear()

    def on_menu_action_triggered(self, action):
        """选择菜单中的标签时触发"""
        tag = action.text()
        self.add_tag(tag)
        self.round_menu.hide()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("TagsLineEdit Test")
            self.resize(600, 200)

            tags_library = ["Python", "JavaScript", "Machine Learning", "Data Science", "AI"]

            main_widget = QWidget(self)
            layout = QVBoxLayout(main_widget)

            self.tags_line_edit = TagsLineEdit(tags_library, self)
            layout.addWidget(self.tags_line_edit)

            self.setCentralWidget(main_widget)

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
