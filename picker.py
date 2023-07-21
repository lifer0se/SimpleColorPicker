#!/bin/python
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QEvent
from pynput.mouse import Controller
from pynput.keyboard import Listener


class PickerWindow(QWidget):

    def __init__(self, parent):
        super(PickerWindow, self).__init__()

        self.setWindowFlags(Qt.BypassWindowManagerHint | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        width = 0
        height = 0
        largest_x = -1
        largest_y = -1
        for m in QApplication.screens():
            if m.availableGeometry().x() > largest_x:
                largest_x = m.availableGeometry().x()
                width = m.availableGeometry().x() + m.availableGeometry().width()
            if m.availableGeometry().y() > largest_y:
                largest_y = m.availableGeometry().y()
                height = m.availableGeometry().y() + m.availableGeometry().height()

        self.move(0, 0)
        self.resize(width, height)

        self.installEventFilter(self)
        self.setMouseTracking(True)

        self.parent = parent
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_painter)
        self.timer.start(1)
        self.running = True
        self.magnifier_size = 221
        self.cursorX = -1
        self.cursorY = -1


    def keyReleaseEvent(self, key):
        if not self.isVisible():
            return

        self.running = False
        self.hide()


    def closeEvent(self, event):
        self.running = False
        self.listener.stop()
        self.timer.stop()


    def update_painter(self):
        if not self.running:
            self.listener.stop()
            self.timer.stop()
            self.hide()
            return

        self.cursorX = Controller().position[0]
        self.cursorY = Controller().position[1]
        self.update()


    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.listener.stop()
            self.timer.stop()
            self.running = False
            self.hide()
            if event.button() != Qt.LeftButton:
                return False
            self.parent.current_color = self.current_color
            self.parent.on_color_updated()
            return True
        if event.type() == QEvent.Show:
            self.listener = Listener(on_release=self.keyReleaseEvent)
            self.listener.start()
            self.running = True
            self.timer.start()
            return True

        return super(PickerWindow, self).eventFilter(source, event)


    def paintEvent(self, event):
        current_screen = QApplication.screenAt(QPoint(self.cursorX, self.cursorY))
        current_screen_x = self.cursorX
        if current_screen_x > current_screen.size().width():
            current_screen_x %= current_screen.size().width()
        current_screen_y = self.cursorY
        if current_screen_y > current_screen.size().height():
            current_screen_y %= current_screen.size().height()

        center_rect_size = 6
        offsetX = 20 if (self.cursorX + 20 + self.magnifier_size - 20 + 40) < self.width() else -self.magnifier_size - 40
        offsetY = 20 if (self.cursorY + 20 + self.magnifier_size - 20 + 40) < self.height() else -(self.magnifier_size + 10)
        top_rect = QRect(self.cursorX + offsetX + self.magnifier_size - 20, self.cursorY + offsetY, 40, 30)
        center_rect = QRect(int(self.cursorX + offsetX + self.magnifier_size * 0.5 - center_rect_size * 0.5) - 1,
                            int(self.cursorY + offsetY + self.magnifier_size * 0.5 - center_rect_size * 0.5) - 1,
                            center_rect_size,
                            center_rect_size)

        image_size = self.magnifier_size * 0.2
        image_half_size = self.magnifier_size * 0.1
        pixmap = current_screen.grabWindow(0, current_screen_x - int(image_half_size), current_screen_y - int(image_half_size), int(image_size), int(image_size))

        if self.cursorX - image_half_size < 0:
            pixmap = self.black_out_pixmap(pixmap, 0, image_size - int(self.cursorX + image_half_size), 0, image_size)
        elif self.cursorX + image_half_size > self.width():
            pixmap = self.black_out_pixmap(pixmap, self.width() - int(self.cursorX - image_half_size + 2), image_size, 0, image_size)
        if self.cursorY - image_half_size < 0:
            pixmap = self.black_out_pixmap(pixmap, 0, image_size, 0, image_size - int(self.cursorY + image_half_size))
        elif self.cursorY + image_half_size > self.height():
            pixmap = self.black_out_pixmap(pixmap, 0, image_size, self.height() - int(self.cursorY - image_half_size + 2), image_size)
        pixmap = pixmap.scaled(self.magnifier_size, self.magnifier_size)

        self.current_color = QColor(pixmap.toImage().pixel(int(self.magnifier_size * 0.5 - center_rect_size * 0.5),
                                                           int(self.magnifier_size * 0.5 - center_rect_size * 0.5)))

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        pen = QPen(QColor("#FFF"))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.fillRect(top_rect, self.current_color)
        painter.drawRect(top_rect)

        pen.setWidth(1)
        painter.setPen(pen)
        circlePath = QPainterPath()
        circlePath.addEllipse(self.cursorX + offsetX, self.cursorY + offsetY, self.magnifier_size, self.magnifier_size)
        painter.setClipPath(circlePath)
        painter.drawPixmap(self.cursorX + offsetX, self.cursorY + offsetY, pixmap)
        painter.drawRect(center_rect)

        pen.setWidth(6)
        painter.setPen(pen)
        painter.drawEllipse(self.cursorX + offsetX, self.cursorY + offsetY, self.magnifier_size, self.magnifier_size)


    def black_out_pixmap(self, pixmap, from_width, to_width, from_height, to_height):
        image = pixmap.toImage()
        for x in range(int(from_width), int(to_width)):
            for y in range(int(from_height), int(to_height)):
                image.setPixelColor(x, y, QColor("#000"))
        return QPixmap.fromImage(image)
