# music.py

from src.play_mode import PlayMode
from src.ScrollableMusicListFrame import ScrollableMusicListFrame

class MusicManager:
    """管理音乐文件的增删改和同步显示"""

    def __init__(self, file_list_frame:ScrollableMusicListFrame):
        self._music_files = []  # 内部存储的音乐文件列表
        self.file_list_frame = file_list_frame  # 与显示组件关联

    def add_music(self, music):
        """添加一个音乐文件"""
        self._music_files.append(music)
        self.file_list_frame.add_item(music)

    def remove_music(self, music_name):
        """移除一个音乐文件"""
        self._music_files = [music for music in self._music_files if music.name != music_name]
        # 查找对应的显示项并移除
        item_to_remove = next((item for item in self.file_list_frame.items if item["name"] == music_name), None)
        if item_to_remove:
            self.file_list_frame.remove_item(item_to_remove)

    def update_music(self, music_name, new_tags=None, new_play_mode=None):
        """更新一个音乐文件的属性"""
        for music in self._music_files:
            if music.name == music_name:
                if new_tags:
                    music.tags = new_tags
                if new_play_mode:
                    music.play_mode = new_play_mode
                # 同步更新显示内容
                self.file_list_frame.update_item(music)
                break

    def get_all_music(self):
        """获取所有音乐文件"""
        return self._music_files

    def clear(self):
        """清空所有音乐文件"""
        self._music_files.clear()
        self.file_list_frame.set_items([])



class Music:
    def __init__(self, name, absolute_path, tags=None, play_mode=PlayMode.ONCE, start_time=0, end_time=None):
        self.name = name  # 音乐名称
        self.absolute_path = absolute_path  # 音乐的绝对路径
        self.tags = tags if tags else []  # 音乐标签列表
        self.play_mode = play_mode  # 播放方式
        self.start_time = start_time  # 播放片段的起始时间（秒）
        self.end_time = end_time  # 播放片段的结束时间（秒）

    def create_item(self):
        # 返回一个可以插入 `ScrollableMusicListFrame` 的条目信息
        return {
            "name": self.name,
            "tags": self.tags,
            "play_mode": self.play_mode,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "absolute_path": self.absolute_path
        }
        
    def to_dict(self):
        """将 Music 实例转换为字典"""
        return {
            "name": self.name,
            "absolute_path": self.absolute_path,
            "tags": self.tags,
            "play_mode": self.play_mode.value,  # 假设 play_mode 是 PlayMode 枚举
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @classmethod
    def from_dict(cls, data):
        """从字典恢复 Music 实例"""
        return cls(
            name=data["name"],
            absolute_path=data["absolute_path"],
            tags=data["tags"],
            play_mode=PlayMode(data["play_mode"]),  # 假设 PlayMode 枚举支持从字符串创建
            start_time=data["start_time"],
            end_time=data["end_time"],
        )
