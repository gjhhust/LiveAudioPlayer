# coding:utf-8
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog
)
from PySide6.QtCore import Signal, QCoreApplication

class Settings(QWidget):
    """ 设置界面，支持语言选择、音频设备选择、工作目录选择 """

    languageChanged = Signal(str)
    audioDeviceChanged = Signal(str)
    workDirChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 默认工作目录
        self.default_work_dir = str(Path.home() / "Documents" / "LiveAudioPlayer_work_dir")
        self.current_work_dir = self.default_work_dir

        # 语言选择
        self.language_label = QLabel(QCoreApplication.translate("Settings", "Language Selection"), self)
        self.layout.addWidget(self.language_label)
        self.language_combo = QComboBox(self)
        self.language_combo.addItems([
            QCoreApplication.translate("Settings", "Simplified Chinese"),
            QCoreApplication.translate("Settings", "English")
        ])
        self.language_combo.currentTextChanged.connect(self.change_language)
        self.layout.addWidget(self.language_combo)

        # 音频设备选择
        self.audio_device_label = QLabel(QCoreApplication.translate("Settings", "Audio Output Device"), self)
        self.layout.addWidget(self.audio_device_label)
        self.audio_device_combo = QComboBox(self)
        self.audio_device_combo.addItems(self.get_audio_devices())
        self.audio_device_combo.currentTextChanged.connect(self.change_audio_device)
        self.layout.addWidget(self.audio_device_combo)

        # 工作目录选择
        self.work_dir_label = QLabel(QCoreApplication.translate("Settings", "Working Directory"), self)
        self.layout.addWidget(self.work_dir_label)
        self.work_dir_button = QPushButton(QCoreApplication.translate("Settings", "Select Directory"), self)
        self.work_dir_button.clicked.connect(self.change_work_dir)
        self.layout.addWidget(self.work_dir_button)

    def change_language(self, language):
        """ 切换语言 """
        self.languageChanged.emit(language)

    def change_audio_device(self, device):
        """ 切换音频设备 """
        self.audioDeviceChanged.emit(device)

    def change_work_dir(self):
        """ 选择工作目录 """
        directory = QFileDialog.getExistingDirectory(
            self, QCoreApplication.translate("Settings", "Select Working Directory"),
            self.current_work_dir
        )
        if directory:
            self.current_work_dir = directory
            self.workDirChanged.emit(directory)

    @staticmethod
    def get_audio_devices():
        """ 获取系统的音频输出设备 """
        return [
            QCoreApplication.translate("Settings", "Default Device"),
            QCoreApplication.translate("Settings", "Headphones"),
            QCoreApplication.translate("Settings", "Speakers")
        ]
