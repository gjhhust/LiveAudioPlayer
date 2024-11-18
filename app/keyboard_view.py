# coding:utf-8
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QCoreApplication

class KeyboardView(QWidget):
    """ 键盘按键绑定的可视化界面 """

    keyBound = Signal(str)  # 按键绑定信号，传递按键对应的音乐名称

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        self.title_label = QLabel(QCoreApplication.translate("KeyboardView", "Keyboard Binding"), self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # 键盘网格布局
        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        # 初始化键盘显示
        self.init_keyboard()

    def init_keyboard(self):
        """ 初始化键盘按键显示 """
        keys = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"]
        ]

        for row_idx, row_keys in enumerate(keys):
            for col_idx, key in enumerate(row_keys):
                key_button = QPushButton(QCoreApplication.translate("KeyboardView", key), self)
                key_button.setFixedSize(40, 40)
                key_button.clicked.connect(lambda _, k=key: self.bind_key(k))
                self.grid_layout.addWidget(key_button, row_idx, col_idx)

    def bind_key(self, key):
        """ 绑定按键到音乐 """
        self.keyBound.emit(key)
