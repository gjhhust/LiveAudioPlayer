# LiveAudioPlayer
LiveAudioPlayer is a simple audio player that can play audio files in real-time. It is written in Python and uses the PyAudio library to access the microphone and speakers.

## Features
- Play audio files in real-time
- Adjust volume
- Pause and resume playback
- Seek to a specific time in the audio file
- Loop playback
- Save playback position

### 项目目录结构设计

根据功能需求和 PySide6-Fluent-Widgets 风格，以下是设计的项目文件目录结构及其内容：

```
LiveAudioPlayer/
├── main.py                     # 主入口文件
├── requirements.txt            # 项目依赖列表
├── resources/                  # 资源文件夹（图标、样式等）
│   ├── icons/
│   ├── styles/
│   └── translations/
├── app/
│   ├── __init__.py
│   ├── import_music_window.py              # 音乐导入窗口
│   ├── music.py                            # 音乐和音乐管理类定义
│   ├── scrollable_music_list.py            # 音乐可视乎组件（右侧栏）
│   ├── keyboard_view.py                    # 键盘按键绑定可视化界面
│   ├── preset.py                           # 预设管理
│   ├── settings.py                         # 设置界面
│   ├── about.py                            # 关于界面
│   └── main_window.py                      # 主窗口文件
```

---

### 各文件功能描述

1. **`main.py`**：  
   - 项目入口，初始化 PySide6 应用程序。
   - 设置语言国际化和 DPI 缩放。
   - 启动主窗口 `MainWindow`。

2. **`app/config.py`**：  
   - 项目配置管理，包括语言、工作目录、主题等。

3. **`app/music.py`**：  
   - 定义 `Music` 类，包含音频的元信息（标签、播放方式、播放区间等）。

4. **`app/music_list.py`**：  
   - 定义 `ScrollableMusicList` 类，用于管理和显示音乐列表（右侧栏）。

5. **`app/keyboard_view.py`**：  
   - 定义键盘按键绑定的可视化界面，支持拖拽绑定音频文件。

6. **`app/preset.py`**：  
   - 管理预设文件（JSON 格式），支持保存和加载音乐类信息及快捷键绑定。

7. **`app/settings.py`**：  
   - 定义设置界面，包括选择音频输出设备等。

8. **`app/about.py`**：  
   - 显示软件的使用说明和版本信息。

9. **`app/main_window.py`**：  
   - 定义主窗口，集成菜单栏、导航栏、主要显示区域和右侧操作栏。

---

