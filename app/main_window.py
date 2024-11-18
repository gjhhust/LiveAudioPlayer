# coding:utf-8
from pathlib import Path
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFileDialog
from qfluentwidgets import NavigationInterface, NavigationItemPosition, FluentIcon as FIF

from app.scrollable_music_list import ScrollableMusicList
from app.preset import PresetPanel
from app.keyboard_view import KeyboardView
from app.settings import Settings
from app.about import About
from app.music import MusicManager
from app.import_music_window import ImportMusicWindow


class MainWindow(QMainWindow):
    """ 主窗口 """

    def __init__(self):
        super().__init__()

        # 初始化窗口
        self.setWindowTitle(QCoreApplication.translate("MainWindow", "LiveAudioPlayer"))
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        # 初始化工作目录和音乐管理器
        self.init_work_dir()
        self.music_manager = MusicManager(
            preset_path=Path(self.work_dir) / "presets/recent.json",
            work_dir=Path(self.work_dir) / "music"
        )

        # 主布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧导航栏
        self.init_navigation()

        # 中间区域和右侧区域
        self.init_main_and_right()
        
        # 加载预设音乐
        self.music_manager.load_from_preset()

    def init_work_dir(self):
        """ 初始化工作目录 """
        self.settings_view = Settings(self)
        self.work_dir = self.settings_view.default_work_dir
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)

        # 监听工作目录变更信号
        self.settings_view.workDirChanged.connect(self.set_work_dir)

    def set_work_dir(self, new_dir):
        """ 更新工作目录 """
        self.work_dir = new_dir
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)

    def init_navigation(self):
        """ 初始化左侧导航栏 """
        self.navigation_interface = NavigationInterface(self)
        self.navigation_interface.setFixedWidth(200)
        self.main_layout.addWidget(self.navigation_interface)

        # 添加导航项
        self.navigation_interface.addItem(
            routeKey="keyboard",
            icon=FIF.ROBOT,
            text=self.tr("Keyboard"),
            onClick=lambda: self.switch_to("keyboard"),
            position=NavigationItemPosition.SCROLL
        )
        self.navigation_interface.addItem(
            routeKey="settings",
            icon=FIF.SETTING,
            text=self.tr("Settings"),
            onClick=lambda: self.switch_to("settings"),
            position=NavigationItemPosition.SCROLL
        )
        self.navigation_interface.addItem(
            routeKey="import_music",
            icon=FIF.MUSIC,
            text=self.tr("Import Music"),
            onClick=self.import_music,
            position=NavigationItemPosition.SCROLL
        )
        self.navigation_interface.addItem(
            routeKey="about",
            icon=FIF.INFO,
            text=self.tr("About"),
            onClick=lambda: self.switch_to("about"),
            position=NavigationItemPosition.BOTTOM
        )

    def init_main_and_right(self):
        """ 初始化中间区域和右侧区域 """
        # 中间区域
        self.center_widget = QWidget(self)
        self.center_layout = QVBoxLayout(self.center_widget)
        self.center_layout.setContentsMargins(0, 0, 0, 0)

        # 子界面
        self.keyboard_view = KeyboardView(self)
        self.about_view = About(self)

        # 默认显示键盘界面
        self.center_layout.addWidget(self.keyboard_view)
        self.center_layout.addWidget(self.settings_view)
        self.center_layout.addWidget(self.about_view)
        self.switch_to("keyboard")

        # 右侧区域
        self.right_widget = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        # 音乐列表
        self.music_list_widget = ScrollableMusicList(self.music_manager, self)
        self.right_layout.addWidget(self.music_list_widget)

        # 初始化预设管理面板
        # self.preset_panel = PresetPanel(
        #     self,
        #     preset_dir=Path(self.work_dir) / "presets",
        #     music_list_getter=lambda: self.music_manager.music_list,
        #     music_list_setter=self.music_manager.set_music_list
        # )
        # self.right_layout.addWidget(self.preset_panel)

        # 分隔布局
        self.splitter_layout = QSplitter(Qt.Horizontal, self)
        self.splitter_layout.addWidget(self.center_widget)
        self.splitter_layout.addWidget(self.right_widget)
        self.splitter_layout.setSizes([800, 400])  # 初始分隔比例
        self.main_layout.addWidget(self.splitter_layout)

    def switch_to(self, route_key):
        """ 切换到指定子界面 """
        self.keyboard_view.setVisible(route_key == "keyboard")
        self.settings_view.setVisible(route_key == "settings")
        self.about_view.setVisible(route_key == "about")

    def closeEvent(self, event):
        """重写关闭事件，在关闭时保存预设"""
        # 调用保存方法
        if self.music_manager:
            self.music_manager.save_to_preset()
            
        event.accept()  # 接受关闭事件
            
    def import_music(self):
        """ 打开导入音乐窗口 """
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self,
            self.tr("Select Music File"),
            str(Path.home()),
            "Audio Files (*.mp3 *.wav *.ogg *.flac)"
        )
        if file_path:
            ImportMusicWindow(self, file_path, self.music_manager).exec()
