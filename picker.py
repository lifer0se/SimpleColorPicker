#!/bin/python
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QEvent
from pynput.mouse import Controller
from screeninfo import get_monitors


class PickerWindow(QWidget):

    def __init__(self, parent):
        super(PickerWindow, self).__init__()

        self.setWindowFlags(Qt.BypassWindowManagerHint | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        width = 0
        height = 0
        largest_x = -1
        largest_y = -1
        for m in get_monitors():
            if m.x > largest_x:
                largest_x = m.x
                width = m.x + m.width
            if m.y > largest_y:
                largest_y = m.y
                height = m.y + m.height

        self.move(0, 0)
        self.resize(width, height)

        self.installEventFilter(self)
        self.setMouseTracking(True)

        self.parent = parent
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1)


    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonRelease):
            self.hide()
            self.timer.stop()
            self.parent.current_color = self.current_color
            self.parent.on_color_updated()
            return True
        if event.type() == QEvent.Show:
            self.timer.start()
            return True

        return super(PickerWindow, self).eventFilter(source, event)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        size = 221
        cursorX = Controller().position[0]
        cursorY = Controller().position[1]
        current_screen = QApplication.screenAt(QPoint(cursorX, cursorY))
        current_screen_x = cursorX - int(size * 0.1)
        if current_screen_x > current_screen.size().width():
            current_screen_x %= current_screen.size().width()
        current_screen_y = cursorY - int(size * 0.1)
        if current_screen_y > current_screen.size().height():
            current_screen_y %= current_screen.size().height()
        pixmap = current_screen.grabWindow(0, current_screen_x, current_screen_y, int(size * 0.2), int(size * 0.2))
        pixmap = pixmap.scaled(size, size)

        center_rect_size = 6
        offsetX = 20 if (cursorX + 20 + size - 20 + 40) < self.width() else -size - 40
        offsetY = 20 if (cursorY + 20 + size - 20 + 40) < self.height() else -(size - 20)
        top_rect = QRect(cursorX + offsetX + size - 20, cursorY + offsetY, 40, 30)
        center_rect = QRect(int(cursorX + offsetX + size * 0.5 - center_rect_size * 0.5) - 1,
                            int(cursorY + offsetY + size * 0.5 - center_rect_size * 0.5) - 1,
                            center_rect_size,
                            center_rect_size)

        pen = QPen(QColor("#FFFFFF"))
        pen.setWidth(2)
        painter.setPen(pen)

        self.current_color = QColor(pixmap.toImage().pixel(int(size * 0.5 - center_rect_size * 0.5), int(size * 0.5 - center_rect_size * 0.5)))
        painter.fillRect(top_rect, self.current_color)
        painter.drawRect(top_rect)

        pen = QPen(QColor("#FFFFFF"))
        pen.setWidth(1)
        painter.setPen(pen)
        circlePath = QPainterPath()
        circlePath.addEllipse(cursorX + offsetX, cursorY + offsetY, size, size)
        painter.setClipPath(circlePath)
        painter.drawPixmap(cursorX + offsetX, cursorY + offsetY, pixmap)
        painter.drawRect(center_rect)

        pen = QPen(QColor("#FFFFFF"))
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawEllipse(cursorX + offsetX, cursorY + offsetY, size, size)
