# coding:utf-8
import os
import shutil
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout
from PySide6.QtGui import QColor
from app.signal_hub import signal_hub
from app.music import MusicCard
from .play_mode import PlayMode
import hashlib

class Music(QObject):
    """ 音乐类，用于存储和管理单个音频文件的信息 """
    updated = Signal()  # 当音乐信息更新时发射信号

    TAG_COLOR_MAP = {}  # 全局标签颜色映射

    def __init__(self, name, source_path, work_dir, tags=None, play_mode=PlayMode.LOOP, start_time=0, end_time=None):
        """
        初始化音乐类
        :param name: 音乐文件名称
        :param source_path: 原始音频文件路径
        :param work_dir: 工作目录，用于存储重命名后的音频文件
        :param tags: 音乐标签（列表）
        :param play_mode: 播放方式（PlayMode 枚举值）
        :param start_time: 起始播放时间（秒）
        :param end_time: 结束播放时间（秒）
        """
        super().__init__()
        self.name = name
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.copy_to_work_dir(source_path) #abspath = os.path.join(work_dir, self.path)
        self.tags = tags or []
        self.play_mode = play_mode
        self.start_time = start_time
        self.end_time = end_time

        # 创建 MusicCard 实例
        self.card = MusicCard(self)

        # 绑定更新信号
        self.updated.connect(self.card.update_tags)
        self.updated.connect(self.card.update_play_mode_icon)

    def copy_to_work_dir(self, source_path):
        """ 将音频文件复制到工作目录，并重命名为指定名称 """
        target_path = self.work_dir / self.name
        if not target_path.exists():
            shutil.copy(source_path, target_path)

    def update(self, **kwargs):
        """
        更新音乐信息，并发射更新信号
        :param kwargs: 要更新的属性和值
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated.emit()

    def to_dict(self):
        """ 转换为字典格式，用于保存预设 """
        return {
            "name": self.name,
            "tags": self.tags,
            "play_mode": self.play_mode.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @staticmethod
    def from_dict(data, work_dir):
        """ 从字典创建音乐实例 """
        return Music(
            name=data["name"],
            source_path=Path(work_dir)/data["name"],
            work_dir=work_dir,
            tags=data.get("tags", []),
            play_mode=PlayMode(data.get("play_mode", PlayMode.ONCE.value)),
            start_time=data.get("start_time", 0),
            end_time=data.get("end_time")
        )

    def get_tag_color(self, tag):
        """固定字符串映射到唯一颜色"""
        if tag not in self.TAG_COLOR_MAP:
            # 使用 hashlib 生成稳定的哈希值
            hash_object = hashlib.md5(tag.encode("utf-8"))  # 使用 MD5 算法
            hash_hex = hash_object.hexdigest()  # 获取哈希值的十六进制字符串

            # 提取哈希值的前几位并将其映射到清新的 RGB 范围
            r = int(hash_hex[:2], 16) % 136 + 120  # 映射到 120-255
            g = int(hash_hex[2:4], 16) % 136 + 120  # 映射到 120-255
            b = int(hash_hex[4:6], 16) % 136 + 120  # 映射到 120-255

            # 转换为 #RRGGBB 格式
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.TAG_COLOR_MAP[tag] = color  # 存储到标签库
        return self.TAG_COLOR_MAP[tag]

    def create_visual_component(self):
        """
        创建音乐的可视化组件，用于展示在列表中。
        :return: QWidget 包含音乐信息的可视化组件
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # 名称标签
        self.name_label = QLabel(self.name)
        layout.addWidget(self.name_label)

        # 标签显示
        self.tag_container = QWidget()
        self.tag_layout = QHBoxLayout(self.tag_container)
        for tag in self.tags:
            self._add_tag_to_layout(tag)
        layout.addWidget(self.tag_container)

        # 播放方式按钮
        self.play_mode_button = QPushButton(self.play_mode.value)
        self.play_mode_button.clicked.connect(self.toggle_play_mode)
        layout.addWidget(self.play_mode_button)

        widget.setLayout(layout)
        return widget

    def _add_tag_to_layout(self, tag):
        """ 向标签布局中添加标签组件 """
        tag_color = self.get_tag_color(tag)
        tag_label = QLabel(tag)
        tag_label.setStyleSheet(f"background-color: {tag_color}; border-radius: 3px; padding: 2px 5px;")
        self.tag_layout.addWidget(tag_label)

    def _bind_widget_signals(self):
        """ 绑定音乐属性与可视化组件的更新逻辑 """
        self.updated.connect(self._update_visual_component)

    def _update_visual_component(self):
        """ 根据属性更新可视化组件 """
        # 更新名称
        self.name_label.setText(self.name)

        # 更新标签
        for i in reversed(range(self.tag_layout.count())):
            widget = self.tag_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        for tag in self.tags:
            self._add_tag_to_layout(tag)

        # 更新播放方式按钮
        self.play_mode_button.setText(self.play_mode.value)

    def toggle_play_mode(self):
        """ 切换播放方式 """
        self.play_mode = PlayMode.LOOP if self.play_mode == PlayMode.ONCE else PlayMode.ONCE
        self.updated.emit()

# coding:utf-8
import json
from pathlib import Path

class MusicManager(QObject):
    """ 音乐统一管理类 """
    def __init__(self, preset_path, work_dir):
        super().__init__()  # 调用父类构造函数
        """
        初始化 MusicManager
        :param preset_path: 预设文件路径
        :param work_dir: 工作目录，用于存储音乐文件
        """
        self.preset_path = Path(preset_path)
        self.work_dir = Path(work_dir)
        self.music_list = []

    def load_from_preset(self):
        """
        从预设文件加载音乐
        :return: None
        """
        if not self.preset_path.exists():
            return

        with open(self.preset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.music_list = [
                self.add_music_from_dict(music_data) for music_data in data
            ]

    def save_to_preset(self):
        """
        保存当前音乐列表到预设文件
        :return: None
        """
        self.preset_path.parent.mkdir(parents=True, exist_ok=True)
        data = [music.to_dict() for music in self.music_list]
        with open(self.preset_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_music_from_params(self, name, source_path, tags=None, play_mode=PlayMode.LOOP, start_time=0, end_time=None):
        """
        通过参数添加音乐
        """
        new_music = Music(
            name=name,
            source_path=source_path,
            work_dir=self.work_dir,
            tags=tags,
            play_mode=play_mode,
            start_time=start_time,
            end_time=end_time
        )
        self.music_list.append(new_music)
        signal_hub.music_added.emit(new_music)
        return new_music

    def add_music_from_dict(self, music_data: dict):
        """
        通过字典数据添加音乐
        """
        new_music = Music.from_dict(music_data, self.work_dir)
        self.music_list.append(new_music)
        signal_hub.music_added.emit(new_music)
        return new_music


    def remove_music(self, music):
        """
        移除音乐
        :param music: 要移除的 Music 对象
        :return: None
        """
        if music in self.music_list:
            self.music_list.remove(music)
            signal_hub.music_removed.emit(music)  # 发射信号

    def update_music(self, music, **kwargs):
        """
        更新音乐信息
        :param music: 要更新的 Music 对象
        :param kwargs: 更新的属性和值
        :return: None
        """
        if music in self.music_list:
            music.update(**kwargs)

    def get_music_by_name(self, name):
        """
        根据名称获取音乐
        :param name: 音乐名称
        :return: Music 对象或 None
        """
        return next((m for m in self.music_list if m.name == name), None)

    def clear(self):
        """ 清空所有音乐 """
        self.music_list.clear()

    def __iter__(self):
        """ 支持迭代 """
        return iter(self.music_list)

    def __len__(self):
        """ 支持 len() 获取数量 """
        return len(self.music_list)

