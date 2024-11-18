# ScrollableMusicListFrame.py

import customtkinter
from tkinter import HORIZONTAL
from src.play_mode import PlayMode

class ScrollableMusicListFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, app, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app  # 保存 LiveAudioPlayer 实例引用
        self.command = command
        self.items = []  # 存储所有行的内容和控件

        # 筛选条件
        self.selected_tags = []  # 选中的标签
        self.selected_play_mode = None  # 选中的播放模式

        # 设置 ScrollableMusicListFrame 自身的网格布局
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 创建 content_frame 作为内容容器
        self.content_frame = customtkinter.CTkFrame(self, fg_color="white")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        # 创建列标题和筛选按钮
        self.create_column_headers()

    def create_column_headers(self):
        """创建顶部的列标题"""
        name_label = customtkinter.CTkLabel(
            self.content_frame, text="名称", font=("Arial", 10, "bold"),
            anchor="center", padx=5, pady=5, fg_color="#e0e0e0", corner_radius=5
        )
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.update_tag_filter_menu()

        self.play_mode_filter_menu = customtkinter.CTkOptionMenu(
            self.content_frame,
            values=["所有方式", PlayMode.ONCE.value, PlayMode.LOOP.value],
            command=self.apply_play_mode_filter,
            font=("Arial", 10)
        )
        self.play_mode_filter_menu.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        self.play_mode_filter_menu.set("所有方式")

        self.content_frame.grid_columnconfigure(0, weight=2)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.content_frame.grid_columnconfigure(2, weight=1)

    def apply_tag_filter(self, selected_tag):
        """应用标签筛选条件"""
        if selected_tag == "所有标签":
            self.selected_tags = []  # 清空筛选条件，显示所有
        else:
            self.selected_tags = [selected_tag]
        self.update_displayed_items()  # 更新显示的音乐列表

    def update_tag_filter_menu(self):
        """动态更新标签筛选菜单"""
        # 如果已有 tag_filter_menu，先销毁旧控件
        if hasattr(self, 'tag_filter_menu') and self.tag_filter_menu is not None:
            self.tag_filter_menu.destroy()

        # 获取最新的标签列表
        tag_options = ["所有标签"] + sorted(self.app.tag_library.keys())

        # 创建新的 tag_filter_menu
        self.tag_filter_menu = customtkinter.CTkOptionMenu(
            self.content_frame,
            values=tag_options,
            command=self.apply_tag_filter,
            font=("Arial", 10)
        )
        self.tag_filter_menu.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.tag_filter_menu.set("所有标签")  # 重置默认选项

    def apply_play_mode_filter(self, selected_mode):
        """应用播放方式筛选条件"""
        if selected_mode == "所有方式":
            self.selected_play_mode = None  # 清空筛选条件，显示所有
        else:
            self.selected_play_mode = selected_mode
        self.update_displayed_items()  # 更新显示的音乐列表

    def add_item(self, music):
        item_name = music.name  # 音乐名称
        tags = music.tags  # 标签列表
        play_mode = music.play_mode  # 播放方式
        
        """添加音乐文件到显示列表并存储为item"""
        row_idx = len(self.items) + 1

        # 第一列：音乐名称
        name_label = customtkinter.CTkLabel(self.content_frame, text=item_name, anchor="w", padx=5, pady=5)

        # 第二列：标签
        tags_frame = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")
        tag_labels = []
        if tags:
            for tag in tags:
                tag_color = self.app.get_tag_color(tag)
                tag_label = customtkinter.CTkLabel(tags_frame, text=tag, fg_color=tag_color, corner_radius=5, padx=5, pady=2)
                tag_label.pack(side="left", padx=5)
                tag_labels.append(tag_label)

        # 第三列：播放方式
        play_mode_label = customtkinter.CTkLabel(self.content_frame, text=play_mode.value, anchor="w", padx=5, pady=5)

        # 存储控件和数据
        item = {
            "name": item_name,
            "tags": tags or [],
            "play_mode": play_mode,
            "hidden": False,  # 初始未隐藏
            "widgets": {
                "row_idx": row_idx,
                "name_label": name_label,
                "tags_frame": tags_frame,
                "tag_labels": tag_labels,
                "play_mode_label": play_mode_label
            }
        }
        self.items.append(item)

        # 显示在界面
        self.show_item(item)

        # 更新标签筛选菜单
        self.update_tag_filter_menu()

    def update_item(self, music):
        """更新现有音乐文件的显示"""
        for item in self.items:
            if item["name"] == music.name:
                # 更新标签内容
                for tag_label in item["widgets"]["tag_labels"]:
                    tag_label.destroy()  # 删除旧的标签
                item["widgets"]["tag_labels"].clear()

                for tag in music.tags:
                    tag_color = self.app.get_tag_color(tag)
                    tag_label = customtkinter.CTkLabel(
                        item["widgets"]["tags_frame"], text=tag, fg_color=tag_color, corner_radius=5, padx=5, pady=2
                    )
                    tag_label.pack(side="left", padx=5)
                    item["widgets"]["tag_labels"].append(tag_label)

                # 更新播放方式
                item["widgets"]["play_mode_label"].configure(text=music.play_mode.value)

                # 更新其他属性
                item["tags"] = music.tags
                item["play_mode"] = music.play_mode
                break

    def remove_item(self, item):
        """从显示和内存中移除一行"""
        widgets = item["widgets"]
        widgets["name_label"].grid_forget()
        widgets["tags_frame"].grid_forget()
        widgets["play_mode_label"].grid_forget()
        for tag_label in widgets["tag_labels"]:
            tag_label.destroy()

        self.items.remove(item)  # 从列表中删除

    def show_item(self, item):
        """显示行内容"""
        widgets = item["widgets"]
        if item["hidden"]:
            return  # 跳过隐藏的项目

        widgets["name_label"].grid(row=widgets["row_idx"], column=0, padx=5, pady=2, sticky="nsew")
        widgets["tags_frame"].grid(row=widgets["row_idx"], column=1, padx=5, pady=2, sticky="nsew")
        widgets["play_mode_label"].grid(row=widgets["row_idx"], column=2, padx=5, pady=2, sticky="nsew")

    def hide_item(self, item):
        """隐藏行内容"""
        widgets = item["widgets"]
        item["hidden"] = True
        widgets["name_label"].grid_forget()
        widgets["tags_frame"].grid_forget()
        widgets["play_mode_label"].grid_forget()

    def update_displayed_items(self):
        """更新显示的音乐文件，基于筛选条件显示或隐藏项目"""
        current_row_idx = 1  # 从第1行开始（第0行是表头）

        for item in self.items:
            # 检查是否匹配当前筛选条件
            match_tags = not self.selected_tags or any(tag in self.selected_tags for tag in item["tags"])
            match_play_mode = not self.selected_play_mode or item["play_mode"].value == self.selected_play_mode

            if match_tags and match_play_mode:
                # 显示项目并更新行索引
                item["hidden"] = False
                item["widgets"]["row_idx"] = current_row_idx
                self.show_item(item)
                current_row_idx += 1
            else:
                # 隐藏项目
                item["hidden"] = True
                self.hide_item(item)

    def set_items(self, music_files):
        """根据 music_files 更新 items 和界面显示"""
        self.items = []  # 清空当前存储的项目
        self.clear_displayed_items()  # 清空界面显示

        for music in music_files:
            self.add_item(music)  # 添加到 items 并更新显示

