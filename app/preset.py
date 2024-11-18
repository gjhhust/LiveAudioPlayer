# coding:utf-8
import json
from pathlib import Path
from app.music import Music
import json
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QMessageBox, QLineEdit
from PySide6.QtCore import QCoreApplication


class PresetManager:
    """ 预设管理器，用于保存和加载音乐信息 """

    def __init__(self, preset_dir):
        self.preset_dir = Path(preset_dir)
        self.preset_dir.mkdir(parents=True, exist_ok=True)

    def save_preset(self, preset_name, music_list):
        """ 保存预设到文件 """
        preset_path = self.preset_dir / f"{preset_name}.json"
        data = [music.to_dict() for music in music_list]
        with open(preset_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_preset(self, preset_name):
        """ 从文件加载预设 """
        preset_path = self.preset_dir / f"{preset_name}.json"
        if not preset_path.exists():
            return []

        with open(preset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Music.from_dict(music_data) for music_data in data]

    def get_all_presets(self):
        """ 获取所有预设文件 """
        return [p.stem for p in self.preset_dir.glob("*.json")]




class PresetPanel(QWidget):
    """ 预设管理面板 """

    def __init__(self, parent, preset_dir, music_list_getter, music_list_setter):
        """
        :param parent: 父组件
        :param preset_dir: 预设文件存储目录
        :param music_list_getter: 获取当前音乐列表的函数
        :param music_list_setter: 设置音乐列表的函数
        """
        super().__init__(parent)
        self.preset_manager = PresetManager(preset_dir)
        self.get_music_list = music_list_getter
        self.set_music_list = music_list_setter

        # 初始化 UI
        self.init_ui()

    def tr(self, text):
        """ 国际化方法 """
        return QCoreApplication.translate("PresetPanel", text)

    def init_ui(self):
        """ 初始化界面 """
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # 标题
        self.title_edit = QLineEdit(self)
        self.title_edit.setPlaceholderText(self.tr("Enter preset name..."))
        self.layout.addWidget(self.title_edit)

        # 预设列表
        self.preset_list = QListWidget(self)
        self.layout.addWidget(self.preset_list)
        self.update_preset_list()

        # 按钮
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.save_button = QPushButton(self.tr("Save Preset"), self)
        self.save_button.clicked.connect(self.save_current_preset)
        self.button_layout.addWidget(self.save_button)

        self.load_button = QPushButton(self.tr("Load Preset"), self)
        self.load_button.clicked.connect(self.load_selected_preset)
        self.button_layout.addWidget(self.load_button)

        self.delete_button = QPushButton(self.tr("Delete Preset"), self)
        self.delete_button.clicked.connect(self.delete_selected_preset)
        self.button_layout.addWidget(self.delete_button)

    def update_preset_list(self):
        """ 更新预设列表 """
        self.preset_list.clear()
        presets = self.preset_manager.get_all_presets()
        self.preset_list.addItems(presets)

    def save_current_preset(self):
        """ 保存当前音乐列表为预设 """
        preset_name = self.title_edit.text().strip()
        if not preset_name:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Preset name cannot be empty"))
            return

        music_list = self.get_music_list()
        self.preset_manager.save_preset(preset_name, music_list)
        QMessageBox.information(self, self.tr("Success"), self.tr("Preset saved successfully"))
        self.update_preset_list()

    def load_selected_preset(self):
        """ 加载选中的预设 """
        selected_items = self.preset_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("No preset selected"))
            return

        preset_name = selected_items[0].text()
        music_list = self.preset_manager.load_preset(preset_name)
        self.set_music_list(music_list)
        QMessageBox.information(self, self.tr("Success"), self.tr("Preset loaded successfully"))

    def delete_selected_preset(self):
        """ 删除选中的预设 """
        selected_items = self.preset_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("No preset selected"))
            return

        preset_name = selected_items[0].text()
        confirm = QMessageBox.question(self, self.tr("Confirm"),
                                       self.tr(f"Delete preset '{preset_name}'?"))
        if confirm == QMessageBox.Yes:
            preset_path = self.preset_manager.preset_dir / f"{preset_name}.json"
            preset_path.unlink(missing_ok=True)
            QMessageBox.information(self, self.tr("Success"), self.tr("Preset deleted successfully"))
            self.update_preset_list()
