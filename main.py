# coding:utf-8
import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()

    app.exec()
    
    # 执行应用
    # sys.exit(app.exec())
