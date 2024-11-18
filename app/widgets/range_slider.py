# coding:utf-8
from PySide6.QtCore import QSize, Qt, Signal, QPoint, QRectF, QPropertyAnimation, Property
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath
from PySide6.QtWidgets import QProxyStyle, QSlider, QWidget, QApplication, QVBoxLayout

from qfluentwidgets import themeColor, isDarkTheme


class SliderHandle(QWidget):
    """滑块句柄"""

    pressed = Signal()
    released = Signal()

    def __init__(self, parent: QSlider):
        super().__init__(parent=parent)
        self.setFixedSize(22, 22)
        self._radius = 5
        self.radiusAni = QPropertyAnimation(self, b'radius', self)
        self.radiusAni.setDuration(100)

    @Property(int)
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, r):
        self._radius = r
        self.update()

    def enterEvent(self, e):
        self._startAni(6)

    def leaveEvent(self, e):
        self._startAni(5)

    def mousePressEvent(self, e):
        self._startAni(4)
        self.pressed.emit()

    def mouseReleaseEvent(self, e):
        self._startAni(6)
        self.released.emit()

    def _startAni(self, radius):
        self.radiusAni.stop()
        self.radiusAni.setStartValue(self.radius)
        self.radiusAni.setEndValue(radius)
        self.radiusAni.start()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # 绘制外圆
        isDark = isDarkTheme()
        painter.setPen(QColor(0, 0, 0, 90 if isDark else 25))
        painter.setBrush(QColor(69, 69, 69) if isDark else Qt.white)
        painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))

        # 绘制内圆
        painter.setBrush(themeColor())
        painter.drawEllipse(QPoint(11, 11), self.radius, self.radius)


class CursorHandle(SliderHandle):
    """游标句柄"""

    def __init__(self, parent: QSlider):
        super().__init__(parent)
        self.setFixedSize(6, 22)  # Adjust the size to make it a thin vertical line
        
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # 绘制浅蓝色竖线
        painter.setBrush(QColor(173, 216, 230))  # Light blue color
        painter.drawRect(self.rect().adjusted(2, 0, -2, 0))  # Draw a vertical rectangle



class RangeSlider(QSlider):
    """范围滑块"""

    lowerValueChanged = Signal(int)
    upperValueChanged = Signal(int)
    cursorValueChanged = Signal(int)

    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal, parent: QWidget = None):
        super().__init__(orientation, parent)
        self.setOrientation(orientation)
        self.setMinimumHeight(22) if orientation == Qt.Horizontal else self.setMinimumWidth(22)

        self.lowerHandle = SliderHandle(self)
        self.upperHandle = SliderHandle(self)
        self.cursorHandle = CursorHandle(self)

        self.lowerValue = self.minimum()
        self.upperValue = self.maximum()
        self.cursorValue = (self.lowerValue + self.upperValue) // 2

        self.lowerHandle.pressed.connect(self._lowerPressed)
        self.upperHandle.pressed.connect(self._upperPressed)
        self.cursorHandle.pressed.connect(self._cursorPressed)

        self.lowerHandle.released.connect(self._handleReleased)
        self.upperHandle.released.connect(self._handleReleased)
        self.cursorHandle.released.connect(self._handleReleased)

        self._activeHandle = None
        self._pressedPos = QPoint()

        self._updateHandlePositions()

    def setLowerValue(self, value):
        """Set the lower value."""
        value = max(self.minimum(), min(value, self.upperValue))  # Ensure value is within bounds
        if self.lowerValue != value:
            self.lowerValue = value
            self.lowerValueChanged.emit(value)
            self._updateHandlePositions()
            self.update()

    def setUpperValue(self, value):
        """Set the upper value."""
        value = min(self.maximum(), max(value, self.lowerValue))  # Ensure value is within bounds
        if self.upperValue != value:
            self.upperValue = value
            self.upperValueChanged.emit(value)
            self._updateHandlePositions()
            self.update()


    def _lowerPressed(self):
        self._activeHandle = 'lower'

    def _upperPressed(self):
        self._activeHandle = 'upper'

    def _cursorPressed(self):
        self._activeHandle = 'cursor'

    def _handleReleased(self):
        self._activeHandle = None

    def mousePressEvent(self, e: QMouseEvent):
        self._pressedPos = e.pos()
        self._moveHandle(e.pos())
        self.update()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._activeHandle:
            self._moveHandle(e.pos())
            self.update()

    def _moveHandle(self, pos: QPoint):
        """Move the active handle to a new position, constrained within range."""
        value = self._posToValue(pos)

        if self._activeHandle == 'lower':
            # Constrain lower handle within the minimum and upper handle
            if self.minimum() <= value < self.upperValue:
                self.lowerValue = value
                self.lowerValueChanged.emit(self.lowerValue)
        elif self._activeHandle == 'upper':
            # Constrain upper handle within the lower handle and maximum
            if self.lowerValue < value <= self.maximum():
                self.upperValue = value
                self.upperValueChanged.emit(self.upperValue)
        elif self._activeHandle == 'cursor':
            # Constrain cursor handle within lower and upper handles
            if self.minimum() <= value <= self.maximum():
                self.cursorValue = value
                self.cursorValueChanged.emit(self.cursorValue)

        self._updateHandlePositions()


    def _posToValue(self, pos: QPoint):
        if self._activeHandle == 'lower':
            pd = self.lowerHandle.width() / 2
        elif self._activeHandle == 'upper':
            pd = self.upperHandle.width() / 2
        elif self._activeHandle == 'cursor':
            pd = self.cursorHandle.width() / 2
        else:
            pd = self.cursorHandle.width() / 2
            
        gs = max(self.grooveLength, 1)
        v = pos.x() if self.orientation() == Qt.Horizontal else pos.y()
        return int((v - pd) / gs * (self.maximum() - self.minimum()) + self.minimum())

    @property
    def grooveLength(self):
        l = self.width() if self.orientation() == Qt.Horizontal else self.height()
        return l - self.lowerHandle.width()

    def _updateHandlePositions(self):
        total = max(self.maximum() - self.minimum(), 1)
        lowerDelta = int((self.lowerValue - self.minimum()) / total * self.grooveLength)
        upperDelta = int((self.upperValue - self.minimum()) / total * self.grooveLength)
        cursorDelta = int((self.cursorValue - self.minimum()) / total * self.grooveLength)

        if self.orientation() == Qt.Vertical:
            self.lowerHandle.move(0, lowerDelta)
            self.upperHandle.move(0, upperDelta)
            self.cursorHandle.move(0, cursorDelta)
        else:
            self.lowerHandle.move(lowerDelta, 0)
            self.upperHandle.move(upperDelta, 0)
            self.cursorHandle.move(cursorDelta, 0)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 115) if isDarkTheme() else QColor(0, 0, 0, 100))

        if self.orientation() == Qt.Horizontal:
            self._drawHorizonGroove(painter)
        else:
            self._drawVerticalGroove(painter)

    def _drawHorizonGroove(self, painter: QPainter):
        """绘制水平槽道"""
        groove_rect = QRectF(
            self.lowerHandle.width() / 2, 
            self.height() / 2 - 2, 
            self.width() - self.lowerHandle.width(), 
            4
        )
        painter.setBrush(QColor(200, 200, 200))
        painter.drawRoundedRect(groove_rect, 2, 2)

        # 绘制选中范围
        selected_rect = QRectF(
            self._valueToPos(self.lowerValue),
            self.height() / 2 - 2,
            self._valueToPos(self.upperValue) - self._valueToPos(self.lowerValue),
            4
        )
        painter.setBrush(themeColor())
        painter.drawRoundedRect(selected_rect, 2, 2)

    def _drawVerticalGroove(self, painter: QPainter):
        """绘制垂直槽道"""
        groove_rect = QRectF(
            self.width() / 2 - 2,
            self.lowerHandle.height() / 2,
            4,
            self.height() - self.lowerHandle.height()
        )
        painter.setBrush(QColor(200, 200, 200))
        painter.drawRoundedRect(groove_rect, 2, 2)

        # 绘制选中范围
        selected_rect = QRectF(
            self.width() / 2 - 2,
            self._valueToPos(self.lowerValue),
            4,
            self._valueToPos(self.upperValue) - self._valueToPos(self.lowerValue)
        )
        painter.setBrush(themeColor())
        painter.drawRoundedRect(selected_rect, 2, 2)

    def _valueToPos(self, value):
        """将值转换为像素位置"""
        total_range = max(self.maximum() - self.minimum(), 1)
        if self.orientation() == Qt.Horizontal:
            return (
                self.lowerHandle.width() / 2
                + (value - self.minimum()) / total_range * self.grooveLength
            )
        else:
            return (
                self.lowerHandle.height() / 2
                + (value - self.minimum()) / total_range * self.grooveLength
            )


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    range_slider = RangeSlider(Qt.Horizontal)
    range_slider.setMinimum(0)
    range_slider.setMaximum(100)
    range_slider.setLowerValue(20)
    range_slider.setUpperValue(80)

    range_slider.lowerValueChanged.connect(
        lambda value: print(f"Lower Value: {value}")
    )
    range_slider.upperValueChanged.connect(
        lambda value: print(f"Upper Value: {value}")
    )
    range_slider.cursorValueChanged.connect(
        lambda value: print(f"Cursor Value: {value}")
    )

    main_layout.addWidget(range_slider)
    main_widget.setMinimumSize(500, 100)
    main_widget.show()

    sys.exit(app.exec())
