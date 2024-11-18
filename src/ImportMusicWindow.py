import customtkinter
from src.play_mode import PlayMode
import random

class ImportMusicWindow(customtkinter.CTkToplevel):
    def __init__(self, master, on_complete_callback):
        super().__init__(master)
        
        self.title("Import Music")
        self.geometry("400x400")
        self.on_complete_callback = on_complete_callback
        
        # 初始化文件名称、标签列表和播放模式
        self.file_name = ""
        self.tags = []
        self.play_mode = PlayMode.ONCE
        
        # 文件名称标签
        self.name_label = customtkinter.CTkLabel(self, text="File Name: (Click to Edit)")
        self.name_label.pack(pady=10)
        self.name_label.bind("<Button-1>", self.edit_name)
        
        # 标签输入框和添加按钮
        self.tag_entry = customtkinter.CTkEntry(self, placeholder_text="Enter tag")
        self.tag_entry.pack(pady=5)
        self.add_tag_button = customtkinter.CTkButton(self, text="Add Tag", command=self.add_tag)
        self.add_tag_button.pack(pady=5)
        
        # 标签显示区域
        self.tags_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.tags_frame.pack(pady=10)
        
        # 播放模式选择
        self.play_mode_label = customtkinter.CTkLabel(self, text="Play Mode:")
        self.play_mode_label.pack(pady=(20, 5))
        self.play_mode_option = customtkinter.CTkOptionMenu(self, values=[PlayMode.ONCE.value, PlayMode.LOOP.value], command=self.set_play_mode)
        self.play_mode_option.pack(pady=5)
        
        # 完成和取消按钮
        self.complete_button = customtkinter.CTkButton(self, text="Complete", command=self.complete_import)
        self.complete_button.pack(pady=10, side="left")
        
        self.cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack(pady=10, side="right")
    
    def set_file_name(self, file_name):
        self.file_name = file_name
        self.name_label.configure(text=f"File Name: {file_name}")
    
    def edit_name(self, event):
        new_name = customtkinter.CTkInputDialog(text="Enter new file name:", title="Edit Name").get_input()
        if new_name:
            self.file_name = new_name
            self.name_label.configure(text=f"File Name: {new_name}")
    
    def add_tag(self):
        tag = self.tag_entry.get().strip()
        if tag and tag not in self.tags:
            color = self.get_tag_color(tag)  # 获取或分配颜色
            tag_label = customtkinter.CTkLabel(self.tags_frame, text=tag, fg_color=color, corner_radius=5, padx=5)
            tag_label.pack(side="left", padx=(0, 5))
            tag_label.bind("<Button-1>", lambda e, t=tag_label: self.remove_tag(t))
            self.tags.append(tag)
            self.tag_entry.delete(0, 'end')
    
    def get_tag_color(self, tag):
        # 随机生成颜色
        color = "#%06x" % random.randint(0, 0xFFFFFF)
        return color
    
    def remove_tag(self, tag_label):
        tag_name = tag_label.cget("text")
        if tag_name in self.tags:
            self.tags.remove(tag_name)
            tag_label.destroy()
    
    def set_play_mode(self, mode):
        self.play_mode = PlayMode(mode)
    
    def complete_import(self):
        if self.file_name:
            # 调用回调函数传递音乐信息
            self.on_complete_callback(self.file_name, self.tags, self.play_mode)
            self.destroy()
