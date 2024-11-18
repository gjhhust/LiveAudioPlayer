import customtkinter
import customtkinter
import os
from tkinter import filedialog, messagebox
from PIL import Image
import pygame
import random
from tkinter import filedialog
from src.play_mode import PlayMode
from src.ImportMusicWindow import ImportMusicWindow
import os, json
import shutil
from src.music import Music, MusicManager
from src.scrollable_music_info import ScrollableMusicInfo
from src.ScrollableMusicListFrame import ScrollableMusicListFrame
            
import hashlib
# 初始化Pygame Mixer
pygame.mixer.init()


class LiveAudioPlayer(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("LiveAudioPlayer")
        self.geometry("1200x800")
        
        self.music_dir = r"E:\TRPG\音乐\LiveAudioPlayer\music"  # 工作目录
        self.filter_tag = None  # 当前筛选标签
        self.tag_library = {}  # 标签库，用于存储标签和其对应的音乐文件
        self.filter_tags = {}
        
        # 设置网格布局
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)  # 主区域占3倍宽度
        self.grid_columnconfigure(2, weight=1)  # 右侧操作栏占1倍宽度

        # 加载图标
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo.png")), size=(26, 26))
        self.import_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "import.png")), size=(20, 20))
        self.play_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "play.png")), size=(20, 20))
        self.settings_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "settings.png")), size=(20, 20))

        # 创建导航栏
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  LiveAudioPlayer", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # 导航按钮
        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.play_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.import_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Import",
                                                     fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                     image=self.import_image, anchor="w", command=self.import_music)
        self.import_button.grid(row=2, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       image=self.settings_image, anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=3, column=0, sticky="ew")

        # 模式切换菜单
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # 创建主要显示区域（如音频频谱、全局控制）
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.home_frame_label = customtkinter.CTkLabel(self.home_frame, text="Audio Visualization")
        self.home_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # 全局控制区
        self.control_frame = customtkinter.CTkFrame(self.home_frame)
        self.control_frame.grid(row=1, column=0, pady=10)

        self.play_button = customtkinter.CTkButton(self.control_frame, text="Play", command=self.global_play)
        self.play_button.grid(row=0, column=0, padx=5)

        self.pause_button = customtkinter.CTkButton(self.control_frame, text="Pause", command=self.global_pause)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.volume_slider = customtkinter.CTkSlider(self.control_frame, from_=0, to=100, command=self.set_global_volume)
        self.volume_slider.set(50)
        self.volume_slider.grid(row=0, column=2, padx=5)

        # 右侧操作栏
        self.right_panel = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=20, pady=20)
        self.right_panel.grid_rowconfigure(2, weight=1)  # 使音乐文件列表可以扩展
        self.right_panel.grid_columnconfigure(0, weight=1)  # 设置列权重，确保内部元素可水平扩展
        
        # 音乐文件列表
        self.file_list_label = customtkinter.CTkLabel(
            self.right_panel, text="Music Files", font=customtkinter.CTkFont(size=14, weight="bold")
        )
        self.file_list_label.grid(row=0, column=0, padx=10, pady=10)

        # 创建音乐文件列表框架
        self.file_list_frame = ScrollableMusicListFrame(
            self.right_panel,
            app=self,  # 将主窗口实例传递给 ScrollableMusicListFrame
        )
        self.file_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # 音乐预设管理
        self.preset_label = customtkinter.CTkLabel(self.right_panel, text="Music Presets", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.preset_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.create_preset_button = customtkinter.CTkButton(self.right_panel, text="Create Preset", command=self.create_preset)
        self.create_preset_button.grid(row=3, column=0, padx=10, pady=5)
        
        self.save_preset_button = customtkinter.CTkButton(self.right_panel, text="Save Preset", command=self.save_preset)
        self.save_preset_button.grid(row=4, column=0, padx=10, pady=5)

        self.presets_dir = os.path.join(self.music_dir, "presets") 
        if not os.path.exists(self.presets_dir):   # 如果 presets 目录不存在，则创建
            os.makedirs(self.presets_dir)
        self.load_recent_preset()    # 加载最近的预设文件
        
        # 默认选中 Home Frame
        self.select_frame_by_name("home")
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 音乐全局变量
        self.music_manager = MusicManager(self.file_list_frame)
        self.current_music_preset = "recent.json"  # 当前的预设文件名
    
    ##################################music_file管理##############################################    
    def delete_music_instance(self, music_name):
        """删除一个音乐文件"""
        self.music_manager.remove_music(music_name)

    def update_music_instance(self, music_name, new_tags=None, new_play_mode=None):
        """更新一个音乐文件"""
        self.music_manager.update_music(music_name, new_tags=new_tags, new_play_mode=new_play_mode)
    
    # self.music_manager.add_music(music)
    
    ##################################窗口开关时的函数##############################################    
    def on_close(self):
        """在关闭软件时保存当前状态到 recent.json"""
        self.save_preset()
        self.destroy()
    
    ##################################import music##############################################
    def import_music(self):
        # 选择音频文件
        file_path = filedialog.askopenfilename(filetypes=[("音频文件", "*.mp3 *.wav *.ogg")])
        if file_path:
            import_window = ScrollableMusicInfo(self, lambda *args: self.create_music_instance(file_path, *args), file_path)

    def create_music_instance(self, original_path, new_filename, tags, play_mode, start_time, end_time):
        """创建新的音乐实例并添加到文件列表"""
        new_path = os.path.join(self.music_dir, new_filename)
        if not os.path.exists(new_path):
            shutil.copy(original_path, new_path)

        # 创建音乐实例
        music = Music(
            name=new_filename,
            absolute_path=new_path,
            tags=tags,
            play_mode=play_mode,
            start_time=start_time,
            end_time=end_time
        )
        self.music_manager.add_music(music)

    def get_tag_color(self, tag):
        """固定字符串映射到唯一颜色"""
        if tag not in self.tag_library:
            # 使用 hashlib 生成稳定的哈希值
            hash_object = hashlib.md5(tag.encode("utf-8"))  # 使用 MD5 算法
            hash_hex = hash_object.hexdigest()  # 获取哈希值的十六进制字符串

            # 提取哈希值的前 6 位作为 RGB 值
            r = int(hash_hex[:2], 16)  # 前两位
            g = int(hash_hex[2:4], 16)  # 中间两位
            b = int(hash_hex[4:6], 16)  # 后两位

            # 转换为 #RRGGBB 格式
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.tag_library[tag] = color  # 存储到标签库
        return self.tag_library[tag]

    
    def select_frame_by_name(self, name):
        # 切换导航按钮状态
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.import_button.configure(fg_color=("gray75", "gray25") if name == "import" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")

        # 显示对应的 Frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    ##################################预设管理##############################################
    def save_preset(self, preset_name="recent.json"):
        """保存当前的音乐文件和相关配置到指定预设文件"""
        if preset_name is None:
            preset_name = self.current_music_preset  # 如果未指定，则保存到当前预设
        preset_path = os.path.join(self.presets_dir, preset_name)

        # 准备保存的内容
        preset_data = {
            "music_files": [music.to_dict() for music in self.music_files],  # 假设 Music 类有 to_dict 方法
            "current_preset": preset_name,
        }

        # 保存到文件
        with open(preset_path, "w", encoding="utf-8") as f:
            json.dump(preset_data, f, indent=4)
        print(f"Preset saved to {preset_path}")

    def load_preset(self, preset_name):
        """从指定的预设文件加载音乐文件和配置"""
        preset_path = os.path.join(self.presets_dir, preset_name)

        if not os.path.exists(preset_path):
            print(f"Preset {preset_name} not found.")
            return

        # 加载预设文件
        with open(preset_path, "r", encoding="utf-8") as f:
            preset_data = json.load(f)

        # 恢复音乐文件和配置
        self.music_files = [Music.from_dict(music) for music in preset_data["music_files"]]  # 假设 Music 类有 from_dict 方法
        self.current_music_preset = preset_data["current_preset"]

        # 更新音乐列表显示
        [self.music_files.append(music) for music in self.music_files]
        print(f"Preset loaded from {preset_path}")

    def load_recent_preset(self):
        """加载最近的预设文件（默认 recent.json）"""
        recent_preset_path = os.path.join(self.presets_dir, "recent.json")

        # 如果文件不存在，创建一个默认的 recent.json
        if not os.path.exists(recent_preset_path):
            with open(recent_preset_path, "w", encoding="utf-8") as f:
                json.dump({"music_files": [], "current_preset": "recent.json"}, f, indent=4)

        # 加载 recent.json
        self.load_preset("recent.json")

    def on_music_file_selected(self, file_name):
        # 处理音乐文件双击事件
        print(f"Selected music file: {file_name}")

    def settings_button_event(self):
        messagebox.showinfo("设置", "设置功能待开发")

    def global_play(self):
        print("播放所有音频")

    def global_pause(self):
        print("暂停所有音频")

    def set_global_volume(self, volume):
        pygame.mixer.music.set_volume(int(volume) / 100)

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def create_preset(self):
        # 创建一个音乐预设的逻辑
        print("Creating a new preset")

if __name__ == "__main__":
    app = LiveAudioPlayer()
    app.mainloop()
