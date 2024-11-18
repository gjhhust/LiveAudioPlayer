# music_range_slider.py

import customtkinter
import pygame

class MusicRangeSlider(customtkinter.CTkFrame):
    def __init__(self, master, audio_path, on_update_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # 初始化 Pygame 音乐播放器
        pygame.mixer.init()
        self.audio_path = audio_path
        self.on_update_callback = on_update_callback
        
        # 加载音乐并获取总长度
        pygame.mixer.music.load(self.audio_path)
        self.total_duration = pygame.mixer.Sound(self.audio_path).get_length()

        # 使用 grid 布局放置标签和滑块
        self.grid_columnconfigure(1, weight=1)  # 使滑块扩展以占满可用空间

        # 创建开始标签和滑块
        self.start_label = customtkinter.CTkLabel(self, text="Start")
        self.start_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.start_slider = customtkinter.CTkSlider(self, from_=0, to=self.total_duration, command=self.on_start_slider_change)
        self.start_slider.set(0)
        self.start_slider.grid(row=0, column=1, pady=10, sticky="ew")

        # 创建结束标签和滑块
        self.end_label = customtkinter.CTkLabel(self, text="End")
        self.end_label.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.end_slider = customtkinter.CTkSlider(self, from_=0, to=self.total_duration, command=self.on_end_slider_change)
        self.end_slider.set(self.total_duration)
        self.end_slider.grid(row=1, column=1, pady=10, sticky="ew")

        # 初始化开始和结束时间
        self.start_time = 0
        self.end_time = self.total_duration

        # 创建 tooltip 标签，但默认隐藏
        self.tooltip = customtkinter.CTkLabel(self, text="", fg_color="gray", text_color="white", corner_radius=5)
        self.tooltip.place_forget()  # 隐藏提示标签

        # 绑定悬浮事件到标签上
        self.start_label.bind("<Enter>", lambda e: self.show_tooltip(e, "调整音乐播放起始位置"))
        self.start_label.bind("<Leave>", self.hide_tooltip)
        self.end_label.bind("<Enter>", lambda e: self.show_tooltip(e, "调整音乐中止位置"))
        self.end_label.bind("<Leave>", self.hide_tooltip)

        # 标记拖动状态
        self.is_dragging = False

    def show_tooltip(self, event, text):
        """显示悬浮提示文本"""
        self.tooltip.configure(text=text)
        self.tooltip.place(x=event.x_root - self.winfo_rootx(), y=event.y_root - self.winfo_rooty() - 30)  # 放置在鼠标上方

    def hide_tooltip(self, event):
        """隐藏提示文本"""
        self.tooltip.place_forget()

    def on_start_slider_change(self, value):
        self.start_time = value
        self.is_dragging = True  # 标记为拖动中
        if self.on_update_callback:
            self.on_update_callback(self.start_time, self.end_time)
        self.after(100, self.check_drag_stop, 'start')

    def on_end_slider_change(self, value):
        self.end_time = value
        self.is_dragging = True  # 标记为拖动中
        if self.on_update_callback:
            self.on_update_callback(self.start_time, self.end_time)
        self.after(100, self.check_drag_stop, 'end')

    def check_drag_stop(self, slider_type):
        if self.is_dragging:
            self.is_dragging = False
            if slider_type == 'start':
                self.play_segment(self.start_time)
            elif slider_type == 'end':
                self.play_segment(self.end_time - 1)

    def play_segment(self, start_time):
        pygame.mixer.music.play(start=start_time)
        pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)

    def stop_music(self):
        pygame.mixer.music.stop()

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time
