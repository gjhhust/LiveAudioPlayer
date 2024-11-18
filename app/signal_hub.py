from PySide6.QtCore import QObject, Signal

class SignalHub(QObject):
    """中转信号的中心类"""
    music_added = Signal(object)  # 发射音乐对象
    music_removed = Signal(object)  # 发射音乐对象

# 创建全局信号中心
signal_hub = SignalHub()