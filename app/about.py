# coding:utf-8
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QCoreApplication

class About(QWidget):
    """ 关于界面 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 软件信息
        self.info_label = QLabel(
            QCoreApplication.translate("About", "LiveAudioPlayer\nVersion: 1.0.0\nAuthor: OpenAI\n"), self
        )
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        # 项目链接
        self.project_link = QLabel(
            QCoreApplication.translate("About", '<a href="https://github.com/gjhhust/LiveAudioPlayer">Project Homepage</a>'), 
            self
        )
        self.project_link.setOpenExternalLinks(True)
        self.project_link.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.project_link)

        # 确定按钮
        self.ok_button = QPushButton(QCoreApplication.translate("About", "OK"), self)
        self.ok_button.clicked.connect(self.close_about)
        self.layout.addWidget(self.ok_button)

    def close_about(self):
        """ 关闭关于窗口 """
        self.close()
