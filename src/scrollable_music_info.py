# scrollable_music_info.py

import customtkinter
from src.play_mode import PlayMode
from src.music_range_slider import MusicRangeSlider
import os

class ScrollableMusicInfo(customtkinter.CTkToplevel):
    def __init__(self, master, on_complete_callback, audio_path):
        super().__init__(master)
        
        self.master = master  # 保存 LiveAudioPlayer 实例引用
        self.title("Music Information")
        self.geometry("600x700")
        self.on_complete_callback = on_complete_callback
        self.audio_path = audio_path

        # 提取文件名主体和扩展名
        self.file_name_base, self.file_extension = os.path.splitext(os.path.basename(self.audio_path))

        # 音乐名称输入框，仅显示文件名主体
        self.name_entry = customtkinter.CTkEntry(self, placeholder_text="Enter music name", width=500)
        self.name_entry.insert(0, self.file_name_base)  # 仅插入文件名主体
        self.name_entry.pack(pady=10)
        
        # 标签输入框和添加按钮
        self.tag_entry = customtkinter.CTkEntry(self, placeholder_text="Enter tag",width=200)
        self.tag_entry.pack(pady=10)
        self.tags = []
        self.add_tag_button = customtkinter.CTkButton(self, text="Add Tag", command=self.add_tag)
        self.add_tag_button.pack(pady=5)

        # 标签显示区域
        self.tags_frame = customtkinter.CTkScrollableFrame(self, height=50)
        self.tags_frame.pack(pady=10)

        # 播放模式选择
        self.play_mode_option = customtkinter.CTkOptionMenu(self, values=[PlayMode.ONCE.value, PlayMode.LOOP.value], command=self.set_play_mode)
        self.play_mode_option.pack(pady=10)
        self.play_mode = PlayMode.ONCE

        # 音乐范围滑块
        self.range_slider = MusicRangeSlider(self, self.audio_path, on_update_callback=self.update_range)
        self.range_slider.pack(pady=10, fill="x")

        # 完成和取消按钮
        self.complete_button = customtkinter.CTkButton(self, text="Complete", command=self.complete)
        self.complete_button.pack(pady=10)
        
        self.cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.close_window)
        self.cancel_button.pack(pady=5)

        # 在关闭窗口时停止音乐播放
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def get_tag_color(self, tag):
        return self.master.get_tag_color(tag)

    def add_tag(self):
        tag = self.tag_entry.get().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            color = self.get_tag_color(tag)  # 获取标签颜色

            tag_label = customtkinter.CTkLabel(self.tags_frame, text=tag, corner_radius=5, fg_color=color, padx=5)
            tag_label.pack(side="left", padx=5, pady=5)
            self.tag_entry.delete(0, 'end')

    def set_play_mode(self, mode):
        self.play_mode = PlayMode(mode)

    def update_range(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def complete(self):
        # 获取名称输入框中的内容，并添加回扩展名
        name = self.name_entry.get().strip()
        if name:
            full_name = f"{name}{self.file_extension}"  # 加上扩展名
            start_time = self.range_slider.get_start_time()
            end_time = self.range_slider.get_end_time()
            self.on_complete_callback(full_name, self.tags, self.play_mode, start_time, end_time)
            self.close_window()

    def close_window(self):
        """关闭窗口并停止音乐播放"""
        self.range_slider.stop_music()
        self.destroy()
