#!/bin/python
from PyQt5.QtWidgets import QSpacerItem, QWidget, QApplication, QFrame, QGridLayout, QPushButton, QTabWidget, QLabel, QLineEdit, QHBoxLayout, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.Qt import QColor, QIcon, QEvent, QPoint, QSpacerItem, QSizePolicy
import sys
import os
import picker
import images_qr

class Tab:
    widget: QWidget
    label: str
    frames = []
    textboxes = []
    line_indicators = []
    def __init__(self, widget, label):
        self.widget = widget
        self.label = label
        self.frames = []
        self.textboxes = []
        self.line_indicators = []


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.picker_window = picker.PickerWindow(self)
        self.picker_window.setWindowTitle("QtPicker")

        self.setWindowTitle("QtPicker")
        self.setStyleSheet("background: #383C4A; color: #CFD6DF")
        self.setWindowFlags(Qt.Tool | Qt.MSWindowsFixedSizeDialogHint);
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setFixedSize(417, 578)
        self.is_raw = False
        main_gradient_size = 350
        side_gradient_size = 30

        self.main_gradient = QFrame()
        self.main_gradient.setFixedSize(main_gradient_size, main_gradient_size)

        self.black_overlay = QFrame()
        self.black_overlay.setFixedSize(main_gradient_size, main_gradient_size)
        self.black_overlay.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 0, 0, 0), stop:1 rgba(0, 0, 0, 255));")
        self.black_overlay.mousePressEvent = self.on_gradient_click
        self.black_overlay.mouseMoveEvent = self.on_gradient_click
        self.black_overlay.wheelEvent = self.on_gradient_scroll
        self.vertical_line = QFrame(self.black_overlay)
        self.horizontal_line = QFrame(self.black_overlay)

        self.hue_gradient = QFrame()
        self.hue_gradient.setFixedSize(side_gradient_size, main_gradient_size - 2)
        self.hue_gradient.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255));")
        self.hue_gradient.mousePressEvent = self.on_hue_gradient_click
        self.hue_gradient.mouseMoveEvent = self.on_hue_gradient_click
        self.hue_gradient.wheelEvent = self.on_side_hue_scroll
        self.hue_line = QFrame(self.hue_gradient)


        rgb_gradient_click_functions = [ self.on_red_gradient_clicked, self.on_green_gradient_clicked, self.on_blue_gradient_clicked ]
        hsv_gradient_click_functions = [ self.on_hue_gradient_clicked, self.on_saturation_gradient_clicked, self.on_value_gradient_clicked ]
        rgb_wheel_scroll_functions = [ self.on_red_scroll, self.on_green_scroll, self.on_blue_scroll ]
        hsv_wheel_scroll_functions = [ self.on_hue_scroll, self.on_saturation_scroll, self.on_value_scroll ]
        rgb_text_change_functions = [ self.on_red_text_changed, self.on_green_text_changed, self.on_blue_text_changed ]
        hsv_text_change_functions = [ self.on_hue_text_changed, self.on_saturation_text_changed, self.on_value_text_changed ]
        self.rgb_tab = self.generate_tab_widget("RGB", rgb_gradient_click_functions, rgb_wheel_scroll_functions, rgb_text_change_functions)
        self.hsv_tab = self.generate_tab_widget("HSV", hsv_gradient_click_functions, hsv_wheel_scroll_functions, hsv_text_change_functions)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tab_widget.addTab(self.rgb_tab.widget, self.rgb_tab.label)
        self.tab_widget.addTab(self.hsv_tab.widget, self.hsv_tab.label)

        self.current_color_frame = QFrame()
        self.current_color_frame.setFixedSize(int(main_gradient_size * 0.3), side_gradient_size)

        picker_button = QPushButton("")
        picker_button.setFixedSize(side_gradient_size, side_gradient_size)
        picker_button.setIcon(QIcon(":picker_icon.svg"))
        picker_button.pressed.connect(self.show_picker)

        self.hex_line_edit = QLineEdit()
        self.hex_line_edit.setFixedWidth(70)
        self.hex_line_edit.setAlignment(Qt.AlignRight)
        self.hex_line_edit.textChanged.connect(self.on_hex_value_changed)

        self.raw_check_box = QCheckBox("RAW")
        self.raw_check_box.setFixedSize(50, 20)
        self.raw_check_box.stateChanged.connect(self.on_raw_changed)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.current_color_frame)
        bottom_layout.addWidget(picker_button)
        bottom_layout.addSpacerItem(QSpacerItem(20,10, QSizePolicy.Expanding))
        bottom_layout.addWidget(self.raw_check_box)
        bottom_layout.addWidget(self.hex_line_edit)
        bottom_layout.setAlignment(Qt.AlignCenter)
        bottom_layout.setContentsMargins(0,0,0,0)
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)

        layout = QGridLayout(self)
        layout.setSpacing(15)
        layout.addWidget(self.main_gradient, 0, 0, 1, 1)
        layout.addWidget(self.black_overlay, 0, 0, 1, 1)
        layout.addWidget(self.hue_gradient, 0, 1)
        layout.addWidget(self.tab_widget, 2, 0, 1, 2)
        layout.addWidget(bottom_widget, 3, 0, 1, 2)
        self.setLayout(layout)

        self.current_color = QColor(23, 23, 33)
        self.show()
        self.on_color_updated()


    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.update_lines()
                return True
        if event.type() == QEvent.Show:
            self.on_color_updated()
            return True
        return False


    def on_color_updated(self):
        current_hue_percent = self.current_color.hue() / 360.0 * 100.0
        self.main_gradient.setStyleSheet("background-color: qlineargradient(spread:pad, x1:1, x2:0, stop:0 hsl({}%,100%,50%), stop:1 rgba(255, 255, 255, 255));".format(current_hue_percent))
        self.current_color_frame.setStyleSheet("background: {}".format(self.current_color.name().upper()))
        self.current_rgb = [ self.current_color.red(), self.current_color.green(), self.current_color.blue() ]
        self.current_hsv = [ self.current_color.hue(), self.current_color.saturation(), self.current_color.value() ]
        self.update_rgb_tab()
        self.update_hsv_tab()
        self.update_lines()
        self.hex_line_edit.blockSignals(True)
        self.hex_line_edit.setText(self.current_color.name().upper())
        self.hex_line_edit.blockSignals(False)


    def on_raw_changed(self):
        self.is_raw = self.raw_check_box.checkState()
        self.update_rgb_tab()
        self.update_hsv_tab()


    def show_picker(self):
        self.picker_window.show()


    def on_hex_value_changed(self):
        if len(self.hex_line_edit.text()) > 0:
            self.hex_line_edit.setText(self.hex_line_edit.text().upper())
        if self.hex_line_edit.text()[0] != '#':
            self.hex_line_edit.setText('#' + self.hex_line_edit.text())
        if len(self.hex_line_edit.text()) < 7:
            return
        self.current_color = QColor(self.hex_line_edit.text())
        self.on_color_updated()


    def on_gradient_click(self, event):
        cursor_x = event.pos().x()
        cursor_y = event.pos().y()
        saturation = int(cursor_x / self.black_overlay.width() * 255.0)
        value = 255 - int(cursor_y / self.black_overlay.height() * 255.0)
        if saturation < 0:
            saturation = 0
        elif saturation > 255:
            saturation = 255
        if value < 0:
            value = 0
        elif value > 255:
            value = 255

        self.current_color.setHsv(self.current_color.hue(), saturation, value)
        self.on_color_updated()


    def on_hue_gradient_click(self, event):
        cursor_y = event.pos().y()
        hue = 360 - int(cursor_y / self.hue_gradient.height() * 360.0)
        if hue < 0:
            hue = 0
        elif hue > 360:
            hue = 360

        self.current_color.setHsv(hue, self.current_color.saturation(), self.current_color.value())
        self.on_color_updated()


    def on_red_gradient_clicked(self, event):
        red = int(event.pos().x() * 255.0 / self.rgb_tab.frames[0].width())
        if red < 0:
            red = 0
        elif red > 255:
            red = 255
        self.current_color.setRgb(red, self.current_color.green(), self.current_color.blue())
        self.on_color_updated()


    def on_green_gradient_clicked(self, event):
        green = int(event.pos().x() * 255.0 / self.rgb_tab.frames[0].width())
        if green < 0:
            green = 0
        elif green > 255:
            green = 255
        self.current_color.setRgb(self.current_color.red(), green, self.current_color.blue())
        self.on_color_updated()


    def on_blue_gradient_clicked(self, event):
        blue = int(event.pos().x() * 255.0 / self.rgb_tab.frames[0].width())
        if blue < 0:
            blue = 0
        elif blue > 255:
            blue = 255
        self.current_color.setRgb(self.current_color.red(), self.current_color.green(), blue)
        self.on_color_updated()


    def on_hue_gradient_clicked(self, event):
        hue = int(event.pos().x() * 360.0 / self.rgb_tab.frames[0].width())
        if hue < 0:
            hue = 0
        elif hue > 360:
            hue = 360

        self.current_color.setHsv(hue, self.current_color.saturation(), self.current_color.value())
        self.on_color_updated()


    def on_saturation_gradient_clicked(self, event):
        saturation = int(event.pos().x() * 255.0 / self.rgb_tab.frames[0].width())
        if saturation < 0:
            saturation = 0
        elif saturation > 255:
            saturation = 255
        self.current_color.setHsv(self.current_color.hue(), saturation, self.current_color.value())
        self.on_color_updated()


    def on_value_gradient_clicked(self, event):
        value = int(event.pos().x() * 255.0 / self.rgb_tab.frames[0].width())
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self.current_color.setHsv(self.current_color.hue(), self.current_color.saturation(), value)
        self.on_color_updated()


    def on_gradient_scroll(self, event):
        if event.angleDelta().x() > 0 :
            deltaX = 1
        elif event.angleDelta().x() < 0:
            deltaX = -1
        else:
            deltaX = 0
        if event.angleDelta().y() > 0 :
            deltaY = 1
        elif event.angleDelta().y() < 0:
            deltaY = -1
        else:
            deltaY = 0
        value = self.current_color.value() + deltaX
        saturation = self.current_color.saturation() + deltaY
        if saturation < 0:
            saturation = 0
        elif saturation > 255:
            saturation = 255
        if value < 0:
            value = 0
        elif value > 255:
            value = 255

        self.current_color.setHsv(self.current_color.hue(), saturation, value)
        self.on_color_updated()


    def on_side_hue_scroll(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        hue = self.current_color.hue() + int(delta)
        if hue < 0:
            hue = 0
        elif hue > 360:
            hue = 360

        self.current_color.setHsv(hue, self.current_color.saturation(), self.current_color.value())
        self.on_color_updated()


    def on_red_scroll(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        red = self.current_color.red() - int(delta)
        if red < 0:
            red = 0
        elif red > 255:
            red = 255

        self.current_color.setRgb(red, self.current_color.green(), self.current_color.blue())
        self.on_color_updated()


    def on_green_scroll(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        green = self.current_color.green() - int(delta)
        if green < 0:
            green = 0
        elif green > 255:
            green = 255

        self.current_color.setRgb(self.current_color.red(), green, self.current_color.blue())
        self.on_color_updated()


    def on_blue_scroll(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        blue = self.current_color.blue() - int(delta)
        if blue < 0:
            blue = 0
        elif blue > 255:
            blue = 255

        self.current_color.setRgb(self.current_color.red(), self.current_color.green(), blue)
        self.on_color_updated()


    def on_hue_scroll(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        hue = self.current_color.hue() - int(delta)
        if hue < 0:
            hue = 0
        elif hue > 360:
            hue = 360

        self.current_color.setHsv(hue, self.current_color.saturation(), self.current_color.value())
        self.on_color_updated()


    def on_saturation_scroll(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        saturation = self.current_color.saturation() - int(delta)
        if saturation < 0:
            saturation = 0
        elif saturation > 255:
            saturation = 255

        self.current_color.setHsv(self.current_color.hue(), saturation, self.current_color.value())
        self.on_color_updated()


    def on_value_scroll(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        value = self.current_color.value() - int(delta)
        if value < 0:
            value = 0
        elif value > 255:
            value = 255

        self.current_color.setHsv(self.current_color.hue(), self.current_color.saturation(), value)
        self.on_color_updated()


    def on_red_text_changed(self):
        try:
            red = int(self.rgb_tab.textboxes[0].text())
        except:
            return
        if red < 0:
            red = 0
        elif red > 255:
            red = 255
        self.current_color.setRgb(red, self.current_color.green(), self.current_color.blue())
        self.on_color_updated()


    def on_green_text_changed(self):
        try:
            green = int(self.rgb_tab.textboxes[1].text())
        except:
            return
        if green < 0:
            green = 0
        elif green > 255:
            green = 255
        self.current_color.setRgb(self.current_color.red(), green, self.current_color.blue())
        self.on_color_updated()


    def on_blue_text_changed(self):
        try:
            blue = int(self.rgb_tab.textboxes[2].text())
        except:
            return
        if blue < 0:
            blue = 0
        elif blue > 255:
            blue = 255
        self.current_color.setRgb(self.current_color.red(), self.current_color.green(), blue)
        self.on_color_updated()


    def on_hue_text_changed(self):
        try:
            hue = int(self.hsv_tab.textboxes[0].text())
        except:
            return
        if hue < 0:
            hue = 0
        elif hue > 360:
            hue = 360
        self.current_color.setHsv(hue, self.current_color.saturation(), self.current_color.value())
        self.on_color_updated()


    def on_saturation_text_changed(self):
        try:
            saturation = int(self.hsv_tab.textboxes[1].text())
        except:
            return
        if saturation < 0:
            saturation = 0
        elif saturation > 255:
            saturation = 255
        self.current_color.setHsv(self.current_color.hue(), saturation, self.current_color.value())
        self.on_color_updated()


    def on_value_text_changed(self):
        try:
            value = int(self.hsv_tab.textboxes[2].text())
        except:
            return
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self.current_color.setHsv(self.current_color.hue(), self.current_color.saturation(), value)
        self.on_color_updated()


    def update_rgb_tab(self):
        c1 = "stop:0 rgba(0, {}, {}, 255), stop:1 rgba(255, {}, {}, 255)".format(self.current_color.green(), self.current_color.blue(), self.current_color.green(), self.current_color.blue())
        c2 = "stop:0 rgba({}, 0, {}, 255), stop:1 rgba({}, 255, {}, 255)".format(self.current_color.red(), self.current_color.blue(), self.current_color.red(), self.current_color.blue())
        c3 = "stop:0 rgba({}, {}, 0, 255), stop:1 rgba({}, {}, 255, 255)".format(self.current_color.red(), self.current_color.green(), self.current_color.red(), self.current_color.green())
        arr = [ c1, c2, c3 ]
        tarr = [ self.current_color.red(), self.current_color.green(), self.current_color.blue() ]
        self.update_tab(self.rgb_tab, arr, tarr)


    def update_hsv_tab(self):
        c1 = "stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255)"

        saturated = QColor(self.current_color)
        unsaturated = QColor(self.current_color)
        saturated.setHsv(saturated.hue(), 255, saturated.value())
        unsaturated.setHsv(unsaturated.hue(), 0, unsaturated.value())
        c2 = "stop:0 rgba({}, {}, {}, 255), stop:1 rgba({}, {}, {}, 255)".format(unsaturated.red(), unsaturated.green(), unsaturated.blue(), saturated.red(), saturated.green(), saturated.blue())

        valued = QColor(self.current_color)
        unvalued = QColor(self.current_color)
        valued.setHsv(valued.hue(), valued.saturation(), 255)
        unvalued.setHsv(unvalued.hue(), unvalued.saturation(), 0)
        c3 = "stop:0 rgba({}, {}, {}, 255), stop:1 rgba({}, {}, {}, 255)".format(unvalued.red(), unvalued.green(), unvalued.blue(), valued.red(), valued.green(), valued.blue())

        arr = [ c1, c2, c3 ]
        tarr = [ self.current_color.hue(), self.current_color.saturation(), self.current_color.value() ]
        self.update_tab(self.hsv_tab, arr, tarr)


    def update_tab(self, tab, arr, tarr):
        stylesheet_start = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0"
        for i in range(len(tab.frames)):
            stylesheet = stylesheet_start + ", {});".format(arr[i])
            tab.frames[i].setStyleSheet(stylesheet)
            tab.textboxes[i].blockSignals(True)
            if self.is_raw:
                tab.textboxes[i].setText("{:.2f}".format(tarr[i] / (255.0 if i > 0 else 360.0)))
            else:
                tab.textboxes[i].setText(str(tarr[i]))
            tab.textboxes[i].blockSignals(False)


    def update_lines(self):
        inverted_color = QColor(self.current_color)
        inverted_color.setHsv((inverted_color.hue() + 180) % 360, min(inverted_color.saturation(), inverted_color.value()), max(inverted_color.saturation(), 255 - inverted_color.value()))
        inverted_color.setHsv(inverted_color.hue(), 255, 255)

        stylesheet = "background-color: rgba({},{},{},185)".format(inverted_color.red(), inverted_color.green(), inverted_color.blue())
        self.vertical_line.setStyleSheet(stylesheet)
        self.horizontal_line.setStyleSheet(stylesheet)
        self.hue_line.setStyleSheet(stylesheet)

        self.vertical_line.setGeometry(int(self.current_color.saturation() * self.black_overlay.width() / 255.0) - 1, 0, 2, self.black_overlay.height())
        self.horizontal_line.setGeometry(0, int((255 - self.current_color.value()) * self.black_overlay.height() / 255.0) - 1, self.black_overlay.width(), 2)
        self.hue_line.setGeometry(0, int((360 - self.current_color.hue()) * self.hue_gradient.height() / 360.0) - 1, self.hue_gradient.width(), 2)

        self.update_tab_lines(self.rgb_tab, self.current_rgb, stylesheet)
        self.update_tab_lines(self.hsv_tab, self.current_hsv, stylesheet)


    def update_tab_lines(self, tab, current_colors, stylesheet):
        for i in range(len(tab.line_indicators)):
            ax = int(current_colors[i] / 255.0 * tab.frames[i].width())
            if tab.label == "HSV" and i == 0:
                ax = int(ax * 255.0 / 360.0)
            tab.line_indicators[i].setGeometry(ax - 1, 0, 2, tab.frames[i].height())
            tab.line_indicators[i].setStyleSheet(stylesheet)


    def generate_tab_widget(self, name, gradient_click_functions, gradient_scroll_functions, text_change_functions) -> Tab:
        layout = QGridLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 20, 0, 15)
        widget = QWidget()
        widget.setLayout(layout)
        tab = Tab(widget, name)
        for i in range(3):
            label = QLabel(name[i:i+1])
            label.setFixedWidth(10)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(label, i, 0)

            frame = QFrame()
            frame.setFixedSize(310, 20)
            frame.mousePressEvent = gradient_click_functions[i]
            frame.mouseMoveEvent = gradient_click_functions[i]
            frame.wheelEvent = gradient_scroll_functions[i]
            layout.addWidget(frame, i, 1)
            tab.frames.append(frame)

            textbox = QLineEdit()
            textbox.setFixedSize(45, 20)
            textbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            textbox.textChanged.connect(text_change_functions[i])
            textbox.wheelEvent = gradient_scroll_functions[i]
            layout.addWidget(textbox, i, 2)
            tab.textboxes.append(textbox)

            line_indicator = QFrame(frame)
            tab.line_indicators.append(line_indicator)

        return tab


    def closeEvent(self, event):
        app.quit()


    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
