from qfluentwidgets import CardWidget, FlowLayout, IconWidget, FluentIcon
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from .play_mode import PlayMode

class MusicCard(CardWidget):
    def __init__(self, music, parent=None):
        super().__init__(parent)
        self.music = music

        # 设置卡片布局
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # 名称标签
        self.name_label = QLabel(self.music.name, self)
        self.layout.addWidget(self.name_label)

        # 标签容器
        self.tag_container = QWidget(self)
        self.tag_layout = FlowLayout(self.tag_container)
        self.tag_container.setLayout(self.tag_layout)
        self.layout.addWidget(self.tag_container)

        # 播放方式图标
        self.play_mode_icon = IconWidget(
            FluentIcon.SYNC if self.music.play_mode == PlayMode.LOOP else FluentIcon.PIN,
            self
        )
        self.layout.addWidget(self.play_mode_icon)

        # 更新标签显示
        self.update_tags()

    def update_tags(self):
        # 清空现有标签
        for i in reversed(range(self.tag_layout.count())):
            widget = self.tag_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 添加新的标签
        for tag in self.music.tags:
            tag_label = QLabel(tag, self)
            tag_label.setStyleSheet(f"background-color: {self.music.get_tag_color(tag)}; color: white; border-radius: 3px; padding: 2px 5px;")
            self.tag_layout.addWidget(tag_label)

    def update_play_mode_icon(self):
        # 更新播放方式图标
        self.play_mode_icon.setIcon(
            FluentIcon.REPEAT if self.music.play_mode == PlayMode.LOOP else FluentIcon.PLAY_ONCE
        )
