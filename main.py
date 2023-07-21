#!/bin/python
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QGridLayout, QHBoxLayout, QTabWidget
from PyQt5.QtWidgets import QCheckBox, QPushButton, QLabel, QLineEdit, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QEvent
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
        self.picker_window.setWindowTitle("SimpleColorMagnifier")

        self.setWindowTitle("SimpleColorPicker")
        self.setStyleSheet("background: #383C4A; color: #CFD6DF")
        self.setWindowFlags(Qt.Tool | Qt.MSWindowsFixedSizeDialogHint)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setFixedSize(417, 578)
        self.setWindowIcon(QIcon(':picker_icon.png'))
        self.is_raw = False
        main_gradient_size = 350
        side_gradient_size = 30

        self.main_gradient = QFrame()
        self.main_gradient.setFixedSize(main_gradient_size, main_gradient_size)

        black_overlay_stylesheet = """
            background-color:
                qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 0, 0, 0),
                    stop:1 rgba(0, 0, 0, 255)
                );"""
        hue_gradient_stylesheet = """
            background-color:
                qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0,
                    stop:0 rgba(255, 0, 0, 255),
                    stop:0.166 rgba(255, 255, 0, 255),
                    stop:0.333 rgba(0, 255, 0, 255),
                    stop:0.5 rgba(0, 255, 255, 255),
                    stop:0.666 rgba(0, 0, 255, 255),
                    stop:0.833 rgba(255, 0, 255, 255),
                    stop:1 rgba(255, 0, 0, 255)
                );"""

        self.black_overlay = QFrame()
        self.black_overlay.setFixedSize(main_gradient_size, main_gradient_size)
        self.black_overlay.setStyleSheet(black_overlay_stylesheet)
        self.black_overlay.mousePressEvent = self.on_gradient_click
        self.black_overlay.mouseMoveEvent = self.on_gradient_click
        self.black_overlay.wheelEvent = self.on_gradient_scroll
        self.vertical_line = QFrame(self.black_overlay)
        self.horizontal_line = QFrame(self.black_overlay)

        self.hue_gradient = QFrame()
        self.hue_gradient.setFixedSize(side_gradient_size, main_gradient_size - 2)
        self.hue_gradient.setStyleSheet(hue_gradient_stylesheet)
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
        picker_button.setIcon(QIcon(":picker_icon.png"))
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
        bottom_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding))
        bottom_layout.addWidget(self.raw_check_box)
        bottom_layout.addWidget(self.hex_line_edit)
        bottom_layout.setAlignment(Qt.AlignCenter)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
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
        if self.current_color.hue() < 0:
            self.current_color.setHsv(0, self.current_color.saturation(), self.current_color.value())
        self.current_rgb = [ self.current_color.red(), self.current_color.green(), self.current_color.blue() ]
        self.current_hsv = [ self.current_color.hue(), self.current_color.saturation(), self.current_color.value() ]
        self.current_rgbF = [ self.current_color.redF(), self.current_color.greenF(), self.current_color.blueF() ]
        self.current_hsvF = [ self.current_color.hueF(), self.current_color.saturationF(), self.current_color.valueF() ]

        current_hue_percent = self.current_color.hue() / 359.0 * 100.0
        self.main_gradient.setStyleSheet("""background-color:
                                                qlineargradient(spread:pad, x1:1, x2:0,
                                                    stop:0 hsl({}%,100%,50%),
                                                    stop:1 rgba(255, 255, 255, 255));""".format(current_hue_percent))
        self.current_color_frame.setStyleSheet("background: {}".format(self.current_color.name().upper()))

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
        self.on_click(event.pos().x(), self.main_gradient.width(), 255, 1, self.current_hsv, False)
        self.on_click(event.pos().y(), self.main_gradient.height(), 255, 2, self.current_hsv, False, True)

    def on_hue_gradient_click(self, event):
        self.on_click(event.pos().y(), self.hue_gradient.height(), 359, 0, self.current_hsv, False, True)

    def on_red_gradient_clicked(self, event):
        self.on_click(event.pos().x(), self.rgb_tab.frames[0].width(), 255, 0, self.current_rgb, True)

    def on_green_gradient_clicked(self, event):
        self.on_click(event.pos().x(), self.rgb_tab.frames[1].width(), 255, 1, self.current_rgb, True)

    def on_blue_gradient_clicked(self, event):
        self.on_click(event.pos().x(), self.rgb_tab.frames[2].width(), 255, 2, self.current_rgb, True)

    def on_hue_gradient_clicked(self, event):
        self.on_click(event.pos().x(), self.hsv_tab.frames[0].width(), 359, 0, self.current_hsv, False)

    def on_saturation_gradient_clicked(self, event):
        self.on_click(event.pos().x(), self.hsv_tab.frames[1].width(), 255, 1, self.current_hsv, False)

    def on_value_gradient_clicked(self, event):
        self.on_click(event.pos().x(), self.hsv_tab.frames[2].width(), 255, 2, self.current_hsv, False)

    def on_click(self, pos, frame_width, max_value, changing_index, current_colors, is_rgb, invert: bool = False):
        value = int(float(pos) * max_value / frame_width)
        if invert:
            value = max_value - value
        value = max(0, min(max_value, value))
        color = self.current_color_with_value(value, changing_index, current_colors, is_rgb, False)
        if self.current_color == color:
            return

        self.current_color = color
        self.on_color_updated()


    def on_gradient_scroll(self, event):
        if event.angleDelta().y() != 0:
            self.on_scroll(event.angleDelta().y(), self.current_color.saturation(), 255, 1, self.current_hsv, False)
        if event.angleDelta().x() != 0:
            self.on_scroll(event.angleDelta().x(), self.current_color.value(), 255, 2, self.current_hsv, False)

    def on_side_hue_scroll(self, event):
        self.on_scroll(event.angleDelta().y(), self.current_color.hue(), 359, 0, self.current_hsv, False, True)

    def on_red_scroll(self, event):
        self.on_scroll(event.angleDelta().y(), self.current_color.red(), 255, 0, self.current_rgb, True)

    def on_green_scroll(self, event):
        self.on_scroll(event.angleDelta().y(), self.current_color.green(), 255, 1, self.current_rgb, True)

    def on_blue_scroll(self, event):
        self.on_scroll(event.angleDelta().y(), self.current_color.blue(), 255, 2, self.current_rgb, True)

    def on_hue_scroll(self, event):
        self.on_scroll(event.angleDelta().y(), self.current_color.hue(), 359, 0, self.current_hsv, False)

    def on_saturation_scroll(self, event):
        self.on_scroll(event.angleDelta().y(), self.current_color.saturation(), 255, 1, self.current_hsv, False)

    def on_value_scroll(self, event):
        self.on_scroll(event.angleDelta().y(), self.current_color.value(), 255, 2, self.current_hsv, False)

    def on_scroll(self, angleDelta, current_value, max_value, changing_index, current_colors, is_rgb, invert_scroll: bool = False):
        delta = 1 if angleDelta > 0 else -1
        if invert_scroll:
            delta = -delta
        value = current_value - int(delta)
        value = max(0, min(max_value, value))
        color = self.current_color_with_value(value, changing_index, current_colors, is_rgb, False)
        if self.current_color == color:
            return

        self.current_color = color
        self.on_color_updated()


    def on_red_text_changed(self):
        self.on_text_changed(self.rgb_tab.textboxes[0], 255, self.current_rgbF if self.is_raw else self.current_rgb, 0, True)

    def on_green_text_changed(self):
        self.on_text_changed(self.rgb_tab.textboxes[1], 255, self.current_rgbF if self.is_raw else self.current_rgb, 1, True)

    def on_blue_text_changed(self):
        self.on_text_changed(self.rgb_tab.textboxes[2], 255, self.current_rgbF if self.is_raw else self.current_rgb, 2, True)

    def on_hue_text_changed(self):
        self.on_text_changed(self.hsv_tab.textboxes[0], 359, self.current_hsvF if self.is_raw else self.current_hsv, 0, False)

    def on_saturation_text_changed(self):
        self.on_text_changed(self.hsv_tab.textboxes[1], 255, self.current_hsvF if self.is_raw else self.current_hsv, 1, False)

    def on_value_text_changed(self):
        self.on_text_changed(self.hsv_tab.textboxes[2], 255, self.current_hsvF if self.is_raw else self.current_hsv, 2, False)

    def on_text_changed(self, textbox, max_value, current_colors, changing_index, is_rgb):
        try:
            value = float(textbox.text())
        except:
            return

        max = 1.0 if self.is_raw else max_value
        if value < 0:
            value = 0
            textbox.blockSignals(True)
            textbox.setText("0")
            textbox.blockSignals(False)
        elif value > max:
            value = max
            textbox.blockSignals(True)
            textbox.setText(str(max))
            textbox.blockSignals(False)

        color = self.current_color_with_value(value, changing_index, current_colors, is_rgb, True)
        if self.current_color == color:
            return

        self.current_color = color
        textbox.blockSignals(True)
        self.on_color_updated()


    def current_color_with_value(self, value, changing_index, current_colors, is_rgb, check_raw) -> QColor:
        v = [ 0, 0, 0 ]
        for i in range(3):
            if changing_index == i:
                v[i] = value
                continue
            v[i] = current_colors[i]

        if self.is_raw and check_raw:
            if is_rgb:
                color = QColor.fromRgbF(v[0], v[1], v[2])
            else:
                if v[0] == 1.0:
                    v[0] = 0.999
                color = QColor.fromHsvF(v[0], v[1], v[2])
        else:
            if is_rgb:
                color = QColor.fromRgb(int(v[0]), int(v[1]), int(v[2]))
            else:
                color = QColor.fromHsv(int(v[0]), int(v[1]), int(v[2]))
        return color


    def update_rgb_tab(self):
        c1 = "stop:0 rgba(0, {}, {}, 255), stop:1 rgba(255, {}, {}, 255)".format(
            self.current_color.green(), self.current_color.blue(), self.current_color.green(), self.current_color.blue())
        c2 = "stop:0 rgba({}, 0, {}, 255), stop:1 rgba({}, 255, {}, 255)".format(
            self.current_color.red(), self.current_color.blue(), self.current_color.red(), self.current_color.blue())
        c3 = "stop:0 rgba({}, {}, 0, 255), stop:1 rgba({}, {}, 255, 255)".format(
            self.current_color.red(), self.current_color.green(), self.current_color.red(), self.current_color.green())
        arr = [ c1, c2, c3 ]
        tarr = self.current_rgbF if self.is_raw else self.current_rgb
        self.update_tab(self.rgb_tab, arr, tarr)


    def update_hsv_tab(self):
        c1 = """
            stop:0 rgba(255, 0, 0, 255),
            stop:0.166 rgba(255, 255, 0, 255),
            stop:0.333 rgba(0, 255, 0, 255),
            stop:0.5 rgba(0, 255, 255, 255),
            stop:0.666 rgba(0, 0, 255, 255),
            stop:0.833 rgba(255, 0, 255, 255),
            stop:1 rgba(255, 0, 0, 255)
        """

        saturated = QColor(self.current_color)
        unsaturated = QColor(self.current_color)
        saturated.setHsv(saturated.hue(), 255, saturated.value())
        unsaturated.setHsv(unsaturated.hue(), 0, unsaturated.value())
        c2 = "stop:0 rgba({}, {}, {}, 255), stop:1 rgba({}, {}, {}, 255)".format(
            unsaturated.red(), unsaturated.green(), unsaturated.blue(), saturated.red(), saturated.green(), saturated.blue())

        valued = QColor(self.current_color)
        unvalued = QColor(self.current_color)
        valued.setHsv(valued.hue(), valued.saturation(), 255)
        unvalued.setHsv(unvalued.hue(), unvalued.saturation(), 0)
        c3 = "stop:0 rgba({}, {}, {}, 255), stop:1 rgba({}, {}, {}, 255)".format(
            unvalued.red(), unvalued.green(), unvalued.blue(), valued.red(), valued.green(), valued.blue())

        arr = [ c1, c2, c3 ]
        tarr = self.current_hsvF if self.is_raw else self.current_hsv
        self.update_tab(self.hsv_tab, arr, tarr)


    def update_tab(self, tab, arr, tarr):
        stylesheet_start = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0"
        for i in range(len(tab.frames)):
            if tab.textboxes[i].signalsBlocked():
                tab.textboxes[i].blockSignals(False)
                continue
            stylesheet = stylesheet_start + ", {});".format(arr[i])
            tab.frames[i].setStyleSheet(stylesheet)
            tab.textboxes[i].blockSignals(True)
            if self.is_raw:
                tab.textboxes[i].setText("{:.2f}".format(tarr[i]))
            else:
                tab.textboxes[i].setText(str(tarr[i]))
            tab.textboxes[i].blockSignals(False)


    def update_lines(self):
        inverted_color = QColor(self.current_color)
        inverted_color.setHsv(
            (inverted_color.hue() + 180) % 359,
            min(inverted_color.saturation(), inverted_color.value()),
            max(inverted_color.saturation(), 255 - inverted_color.value()))
        inverted_color.setHsv(inverted_color.hue(), 255, 255)

        stylesheet = "background-color: rgba({},{},{},185)".format(
            inverted_color.red(), inverted_color.green(), inverted_color.blue())
        self.vertical_line.setStyleSheet(stylesheet)
        self.horizontal_line.setStyleSheet(stylesheet)
        self.hue_line.setStyleSheet(stylesheet)

        self.vertical_line.setGeometry(
            int(self.current_color.saturation() * self.main_gradient.width() / 255.0) - 1,
            0,
            2,
            self.main_gradient.height())

        self.horizontal_line.setGeometry(
            0,
            int((255 - self.current_color.value()) * self.main_gradient.height() / 255.0) - 1,
            self.main_gradient.width(),
            2)

        self.hue_line.setGeometry(
            0,
            int((359 - self.current_color.hue()) * self.hue_gradient.height() / 359.0) - 1,
            self.hue_gradient.width(),
            2)

        self.update_tab_lines(self.rgb_tab, self.current_rgb, stylesheet)
        self.update_tab_lines(self.hsv_tab, self.current_hsv, stylesheet)


    def update_tab_lines(self, tab, current_colors, stylesheet):
        for i in range(len(tab.line_indicators)):
            ax = int(current_colors[i] / 255.0 * tab.frames[i].width())
            if tab.label == "HSV" and i == 0:
                ax = int(ax * 255.0 / 359.0)
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
            label = QLabel(name[i:i + 1])
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
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
