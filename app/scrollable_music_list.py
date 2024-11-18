from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QActionGroup
from qfluentwidgets import CommandBar, Action, IconInfoBadge, CheckableMenu, MenuIndicatorType, MenuAnimationType, FluentIcon as FIF, StrongBodyLabel
from app.music import MusicManager, Music
from app.signal_hub import signal_hub
from qfluentwidgets import TransparentDropDownPushButton, Action, CheckableMenu, FluentIcon as FIF, MenuIndicatorType, MenuAnimationType


class ScrollableMusicList(QWidget):

    def __init__(self, music_manager: MusicManager, parent=None):
        super().__init__(parent)
        self.music_manager = music_manager
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 添加顶部操作菜单栏
        self.command_bar = CommandBar(self)
        self.command_bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.layout.addWidget(self.command_bar)

        # 排序相关动作
        self._init_sort_actions()
        
        # 滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.content_widget)

        # 占位符，用于撑开剩余空间
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.content_layout.addItem(self.spacer)

        # 监听 music_manager 的变化
        signal_hub.music_removed.connect(self.remove_music_card)
        signal_hub.music_added.connect(self.add_music)

    def _init_sort_actions(self):
        """
        初始化排序相关的动作
        """

        # 创建透明下拉菜单按钮
        self.sort_button = TransparentDropDownPushButton(FIF.MENU, self.tr("Sort"))
        self.sort_button.setFixedHeight(34)

        # 创建排序菜单
        self.sort_menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)
        self.create_time_action = Action(FIF.CALENDAR, self.tr("Created Time"), checkable=True)
        self.modified_time_action = Action(FIF.EDIT, self.tr("Modified Time"), checkable=True)
        self.name_action = Action(FIF.FONT, self.tr("Name"), checkable=True)
        self.ascend_action = Action(FIF.UP, self.tr("Ascending"), checkable=True)
        self.descend_action = Action(FIF.DOWN, self.tr("Descending"), checkable=True)

        # 默认选中
        self.modified_time_action.setChecked(True)
        self.ascend_action.setChecked(True)

        # 动作组
        self.sort_group = QActionGroup(self)
        self.sort_group.addAction(self.create_time_action)
        self.sort_group.addAction(self.modified_time_action)
        self.sort_group.addAction(self.name_action)

        self.order_group = QActionGroup(self)
        self.order_group.addAction(self.ascend_action)
        self.order_group.addAction(self.descend_action)

        # 添加动作到菜单
        self.sort_menu.addActions([self.create_time_action, self.modified_time_action, self.name_action])
        self.sort_menu.addSeparator()
        self.sort_menu.addActions([self.ascend_action, self.descend_action])

        # 绑定菜单到按钮
        self.sort_button.setMenu(self.sort_menu)

        # 添加到命令栏
        self.command_bar.addWidget(self.sort_button)

    def show_sort_menu(self):
        """
        显示排序菜单
        """
        menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)
        menu.addActions([
            self.create_time_action,
            self.modified_time_action,
            self.name_action
        ])
        menu.addSeparator()
        menu.addActions([self.ascend_action, self.descend_action])

        menu.exec(self.mapToGlobal(self.command_bar.rect().bottomLeft()), aniType=MenuAnimationType.DROP_DOWN)
        self.apply_sort()

    def apply_sort(self):
        """
        根据选中的排序方式排序音乐列表
        """
        key = None
        reverse = self.descend_action.isChecked()

        if self.create_time_action.isChecked():
            key = lambda x: getattr(x, "first_time", 0)
        elif self.modified_time_action.isChecked():
            key = lambda x: getattr(x, "last_modified_time", 0)
        elif self.name_action.isChecked():
            key = lambda x: x.name.lower()

        if key:
            self._sort_layout(key, reverse=reverse)

    def _sort_layout(self, key, reverse=False):
        """
        对 layout 中的部件排序，无需重新插入
        """
        widgets = []
        for i in range(self.content_layout.count() - 1):  # 忽略 spacer
            item = self.content_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widgets.append(widget)

        # 按照指定的 key 排序 widgets
        widgets.sort(key=key, reverse=reverse)

        # 更新 widget 在 layout 中的顺序
        for i, widget in enumerate(widgets):
            self.content_layout.insertWidget(i, widget)

    def add_music(self, music: Music):
        """
        新增音乐卡片到显示列表
        """
        if music.card:
            self.content_layout.insertWidget(self.content_layout.count() - 1, music.card)

    def remove_music_card(self, music: Music):
        """
        当音乐被删除时，移除对应的卡片
        """
        for i in range(self.content_layout.count() - 1):  # 遍历 layout 中的所有卡片
            item = self.content_layout.itemAt(i)
            widget = item.widget()
            if widget and widget == music.card:  # 找到对应的卡片
                widget.setParent(None)
                widget.deleteLater()
                break
