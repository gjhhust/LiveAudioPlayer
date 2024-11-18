from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea, QWidget, QGridLayout, QRadioButton, QButtonGroup
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from qfluentwidgets import PushButton, LineEdit, FluentIcon as FIF, TeachingTip, InfoBarIcon, TeachingTipTailPosition
from PySide6.QtGui import QColor
from app.widgets import RangeSlider  # 引入自定义 RangeSlider
from app.music import MusicManager, PlayMode, Music
from PySide6.QtCore import QObject, QEvent

class ImportMusicWindow(QDialog):
    """ 导入音乐窗口 """

    def __init__(self, parent, file_path, music_manager:MusicManager):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Import Music"))
        self.file_path = file_path
        self.music_manager = music_manager

        # 解析文件名和后缀
        self.file_name, self.file_extension = self.file_path.split("/")[-1].rsplit(".", 1)

        # 初始化音频播放器
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setSource(file_path)

        # 初始化标签列表
        self.tags = []
        # 初始化界面
        self.init_ui()

        # 设置滑块范围
        self.media_player.durationChanged.connect(self.set_slider_range)

    def init_ui(self):
        """ 初始化界面 """
        layout = QVBoxLayout(self)

        # 文件名称输入框（不包含后缀）
        name_label = QLabel(self.tr("Music Name"))
        layout.addWidget(name_label)
        self.add_teaching_tip(name_label, self.tr("Enter the name of the music file without the extension."))

        self.name_input = LineEdit(self)
        self.name_input.setText(self.file_name)  # 设置初始值
        layout.addWidget(self.name_input)

        # 标签输入和展示
        self.tag_input_layout = QVBoxLayout()

        # 标签标题
        tag_label = QLabel(self.tr("Tags"))
        layout.addWidget(tag_label)
        self.add_teaching_tip(tag_label, self.tr("Add tags to organize and categorize your music."))

        self.tags_input = LineEdit(self)
        self.tags_input.setPlaceholderText(self.tr("Enter tag and press 'Add Tag'"))
        self.add_tag_button = PushButton(FIF.ADD, self.tr("Add Tag"))
        self.add_tag_button.clicked.connect(self.add_tag)

        tag_input_row = QHBoxLayout()
        tag_input_row.addWidget(self.tags_input)
        tag_input_row.addWidget(self.add_tag_button)
        self.tag_input_layout.addLayout(tag_input_row)

        # 标签展示容器（网格布局）
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        self.tag_display_frame = QWidget(self)
        self.tag_display_grid = QGridLayout(self.tag_display_frame)
        self.tag_display_grid.setSpacing(5)
        self.tag_display_grid.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidget(self.tag_display_frame)

        # 将滚动区域添加到标签输入布局中
        self.tag_input_layout.addWidget(scroll_area)
        layout.addLayout(self.tag_input_layout)

        # 播放方式 - 使用单选按钮
        play_mode_label = QLabel(self.tr("Play Mode"))
        layout.addWidget(play_mode_label)
        self.add_teaching_tip(play_mode_label, self.tr("Choose the playback mode: Once or Loop."))

        self.play_mode_group = QButtonGroup(self)

        self.once_radio = QRadioButton(self.tr("Once"))
        self.once_radio.setChecked(True)  # 默认选中
        self.play_mode_group.addButton(self.once_radio)

        self.loop_radio = QRadioButton(self.tr("Loop"))
        self.play_mode_group.addButton(self.loop_radio)

        play_mode_layout = QHBoxLayout()
        play_mode_layout.addWidget(self.once_radio)
        play_mode_layout.addWidget(self.loop_radio)
        layout.addLayout(play_mode_layout)

        # 播放区间
        playback_label = QLabel(self.tr("Playback Range"))
        layout.addWidget(playback_label)
        self.add_teaching_tip(playback_label, self.tr("Set the playback range for the music."))

        self.range_slider = RangeSlider(Qt.Horizontal, self)
        self.range_slider.setSingleStep(1)
        self.range_slider.lowerValueChanged.connect(self.update_start_time)
        self.range_slider.upperValueChanged.connect(self.update_end_time)
        self.range_slider.cursorValueChanged.connect(self.preview_audio)  # 游走条播放
        layout.addWidget(self.range_slider)

        # 确认和取消按钮
        button_layout = QHBoxLayout()
        self.ok_button = PushButton(FIF.ACCEPT, self.tr("OK"))
        self.cancel_button = PushButton(FIF.CLOSE, self.tr("Cancel"))
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # 信号连接
        self.ok_button.clicked.connect(self.add_music)
        self.cancel_button.clicked.connect(self.close_window)

        self.setLayout(layout)

    def add_teaching_tip(self, widget, text):
        """ 为 Label 添加鼠标悬浮提示 """
        widget.setProperty("tipText", text)  # 保存提示内容到属性中
        widget.installEventFilter(self)  # 为目标部件安装事件过滤器

    def eventFilter(self, obj: QObject, event: QEvent):
        """ 事件过滤器，处理鼠标悬浮事件 """
        if event.type() == QEvent.Enter and obj.property("tipText"):
            # 鼠标进入部件区域时显示 TeachingTip
            TeachingTip.create(
                target=obj,
                icon=InfoBarIcon.INFORMATION,
                title='',
                content=obj.property("tipText"),  # 动态获取提示内容
                isClosable=True,
                duration = 2000,  # 持续时间为 0 表示一直显示
                tailPosition=TeachingTipTailPosition.LEFT_TOP,
                parent=self
            )
        return super().eventFilter(obj, event)


    def add_music(self):
        """ 添加音乐到管理器 """
        name = self.name_input.text().strip()
        if not name:
            name = self.file_name
        name = f"{name}.{self.file_extension}"  # 恢复后缀

        # 根据单选按钮设置播放模式
        if self.once_radio.isChecked():
            play_mode = PlayMode.ONCE
        elif self.loop_radio.isChecked():
            play_mode = PlayMode.LOOP
        else:
            play_mode = PlayMode.ONCE  # 默认值

        start_time = self.range_slider.lowerValue
        end_time = self.range_slider.upperValue
        
        self.music_manager.add_music_from_params(
            name=name,
            source_path=self.file_path,
            tags=self.tags,
            play_mode=play_mode,
            start_time=start_time,
            end_time=end_time
        )
        self.accept()

    
    def set_slider_range(self, duration):
        """ 设置滑块范围，单位为秒 """
        if duration > 0:
            duration_in_seconds = duration // 1000  # 将毫秒转换为秒
            self.range_slider.setRange(0, duration_in_seconds)

    def add_tag(self):
        """ 添加标签到展示区域 """
        tag_text = self.tags_input.text().strip()
        if not tag_text or tag_text in self.tags:
            return

        # 创建按钮作为标签
        tag_color = Music.get_tag_color(tag_text)
        tag_button = QPushButton(tag_text, self)
        tag_button.setStyleSheet(f"background-color: {tag_color}; color: white; border-radius: 3px; padding: 2px 5px;")
        tag_button.clicked.connect(lambda: self.remove_tag(tag_button, tag_text))

        # 计算网格位置
        row = len(self.tags) // 3  # 假设每行放 4 个标签
        col = len(self.tags) % 3
        self.tag_display_grid.addWidget(tag_button, row, col)

        # 添加标签
        self.tags.append(tag_text)
        self.tags_input.clear()


    def remove_tag(self, tag_button, tag_text):
        """ 从展示区域移除标签 """
        self.tags.remove(tag_text)
        self.tag_display_frame.layout().removeWidget(tag_button)
        tag_button.deleteLater()

    def preview_audio(self, value):
        """ 根据游走条位置播放音乐 """
        self.media_player.setPosition(value * 1000)  # 毫秒单位
        self.media_player.play()

    def update_start_time(self, value):
        """ 更新开始时间并播放 """
        self.media_player.setPosition(value * 1000)  # 毫秒单位
        self.media_player.play()

    def update_end_time(self, value):
        """ 更新结束时间并播放 """
        self.media_player.setPosition(value * 1000)  # 毫秒单位
        self.media_player.play()

    def close_window(self):
        """ 关闭窗口并停止播放 """
        self.media_player.stop()
        self.reject()
