#!/bin/python
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QGridLayout, QHBoxLayout, QTabWidget
from PyQt5.QtWidgets import QCheckBox, QPushButton, QLabel, QLineEdit, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon, QColor, QRegExpValidator, QMouseEvent
from PyQt5.QtCore import Qt, QEvent, QRegExp
from functools import partial
import sys
import picker
import images_qr


class Tab:
    widget: QWidget
    label: str
    frames = []
    line_edits = []
    line_indicators = []

    def __init__(self, widget, label):
        self.widget = widget
        self.label = label
        self.frames = []
        self.line_edits = []
        self.line_indicators = []


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.picker_window = picker.PickerWindow(self)
        self.picker_window.setWindowTitle("SimpleColorMagnifier")

        self.setWindowTitle("SimpleColorPicker")
        self.setStyleSheet("background: #383C4A; color: #CFD6DF")
        self.setWindowFlags(Qt.WindowType.Tool)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setFixedSize(437, 598)
        self.setWindowIcon(QIcon(':picker_icon.png'))
        main_gradient_size = 370
        side_gradient_size = 30


        self.current_rgb = []
        self.current_hsv = []

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
        self.black_overlay.mousePressEvent = self.on_main_gradient_click
        self.black_overlay.mouseMoveEvent = self.on_main_gradient_click
        self.black_overlay.wheelEvent = self.on_main_gradient_scroll
        self.vertical_line = QFrame(self.black_overlay)
        self.horizontal_line = QFrame(self.black_overlay)

        self.hue_gradient = QFrame()
        self.hue_gradient.setFixedSize(side_gradient_size, main_gradient_size - 2)
        self.hue_gradient.setStyleSheet(hue_gradient_stylesheet)

        click_func = partial(self.on_gradient_click, self.hue_gradient.height(), 359, 0, False, True, True)
        scroll_func = partial(self.on_gradient_scroll, 359, 0, False, False, True)
        self.hue_gradient.mousePressEvent = click_func
        self.hue_gradient.mouseMoveEvent = click_func
        self.hue_gradient.wheelEvent = scroll_func
        self.hue_line = QFrame(self.hue_gradient)

        self.rgb_tab = self.generate_tab_widget("RGB", [ 255, 255, 255 ], True)
        self.hsv_tab = self.generate_tab_widget("HSV", [ 360, 255, 255 ], False)
        self.values_tab = self.generate_values_tab()

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tab_widget.addTab(self.rgb_tab.widget, "RGB")
        self.tab_widget.addTab(self.hsv_tab.widget, "HSV")
        self.tab_widget.addTab(self.values_tab, "Values")

        self.current_color_frame = QFrame()
        self.current_color_frame.setFixedSize(int(main_gradient_size * 0.3), side_gradient_size)

        picker_button = QPushButton("")
        picker_button.setFixedSize(side_gradient_size, side_gradient_size)
        picker_button.setIcon(QIcon(":picker_icon.png"))
        picker_button.released.connect(self.show_picker)

        self.hex_line_edit = QLineEdit()
        self.hex_line_edit.setFixedWidth(70)
        self.hex_line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.hex_line_edit.mouseReleaseEvent = lambda a0: self.on_line_edit_clicked(self.hex_line_edit, a0)
        self.hex_line_edit.textChanged.connect(self.on_hex_value_changed)
        reg_ex = QRegExp("^#?([A-Fa-f0-9]){,6}$")
        input_validator = QRegExpValidator(reg_ex, self.hex_line_edit)
        self.hex_line_edit.setValidator(input_validator)

        self.raw_check_box = QCheckBox("RAW")
        self.raw_check_box.setFixedSize(50, 20)
        self.raw_check_box.stateChanged.connect(self.on_raw_changed)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.current_color_frame)
        bottom_layout.addWidget(picker_button)
        bottom_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding))
        bottom_layout.addWidget(self.raw_check_box)
        bottom_layout.addWidget(self.hex_line_edit)
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        if event.type() == QEvent.Type.Show:
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
        self.update_values_tab()
        self.update_lines()

        if self.hex_line_edit.text() != self.current_color.name().upper():
            self.set_text_with_blocked_signals(self.hex_line_edit, self.current_color.name().upper())


    def on_raw_changed(self):
        for line_edit in self.rgb_tab.line_edits:
            if self.raw_check_box.checkState():
                self.set_raw_validator(line_edit)
            else:
                self.set_non_raw_validator(line_edit)

        self.update_rgb_tab()
        self.update_hsv_tab()


    def show_picker(self):
        self.picker_window.show()


    def on_hex_value_changed(self):
        text = self.hex_line_edit.text()
        if len(text) == 0:
            text = self.set_text_with_blocked_signals(self.hex_line_edit, '#')
            self.hex_line_edit.setCursorPosition(1)
        else:
            text = self.set_text_with_blocked_signals(self.hex_line_edit, text.upper())

        if text[0] != '#':
            text = self.set_text_with_blocked_signals(self.hex_line_edit, '#' + self.hex_line_edit.text())
        if len(text) < 7:
            return

        self.current_color = QColor(self.hex_line_edit.text())
        self.on_color_updated()


    def set_text_with_blocked_signals(self, line_edit, text) -> str:
        pos = line_edit.cursorPosition()
        line_edit.blockSignals(True)
        line_edit.setText(text)
        line_edit.setCursorPosition(pos)
        line_edit.blockSignals(False)
        return text


    def on_main_gradient_click(self, a0: QMouseEvent):
        self.on_gradient_click(self.main_gradient.width(), 255, 1, False, False, False, a0)
        self.on_gradient_click(self.main_gradient.height(), 255, 2, False, True, True, a0)


    def on_gradient_click(self, frame_size, max_value, changing_index, is_rgb, is_vertical, should_invert, a0):
        value = float(a0.pos().x() if not is_vertical else a0.pos().y())
        value = int(value * max_value / frame_size)
        if should_invert:
            value = max_value - value
        value = max(0, min(max_value, value))
        current_colors = self.current_rgb if is_rgb else self.current_hsv
        color = self.current_color_with_value(value, changing_index, current_colors, is_rgb, False)
        if self.current_color == color:
            return

        self.current_color = color
        self.on_color_updated()


    def on_line_edit_clicked(self, line_edit, a0):
        line_edit.setSelection(0, len(line_edit.text()))


    def on_main_gradient_scroll(self, a0):
        if a0.angleDelta().y() != 0:
            self.on_gradient_scroll(255, 1, False, False, True, a0)
        if a0.angleDelta().x() != 0:
            self.on_gradient_scroll(255, 2, False, True, False, a0)


    def on_gradient_scroll(self, max_value, changing_index, is_rgb, is_horizontal, invert_scroll, a0):
        current_colors = self.current_rgb if is_rgb else self.current_hsv
        current_value = current_colors[changing_index]
        angle = a0.angleDelta().x() if is_horizontal else a0.angleDelta().y()
        delta = 1 if angle > 0 else -1
        if invert_scroll:
            delta = -delta
        value = current_value - int(delta)
        value = max(0, min(max_value, value))
        color = self.current_color_with_value(value, changing_index, current_colors, is_rgb, False)
        if self.current_color == color:
            return

        self.current_color = color
        self.on_color_updated()


    def on_text_changed(self, line_edit, max_value, changing_index, is_rgb):
        try:
            value = float(line_edit.text())
        except:
            return

        max = 1.0 if self.raw_check_box.checkState() else max_value
        if value < 0:
            value = 0
            line_edit.blockSignals(True)
            line_edit.setText("0")
            line_edit.blockSignals(False)
        elif value > max:
            value = max
            line_edit.blockSignals(True)
            line_edit.setText(str(max))
            line_edit.blockSignals(False)

        current_colors = self.current_rgb if is_rgb else self.current_hsv
        color = self.current_color_with_value(value, changing_index, current_colors, is_rgb, True)
        if self.current_color == color:
            return

        self.current_color = color
        line_edit.blockSignals(True)
        self.on_color_updated()



    def current_color_with_value(self, value, changing_index, current_colors, is_rgb, check_raw) -> QColor:
        v = [ 0.0, 0.0, 0.0 ]
        for i in range(3):
            if changing_index == i:
                v[i] = value
                continue
            v[i] = current_colors[i]

        if self.raw_check_box.checkState() and check_raw:
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
        tarr = self.current_rgbF if self.raw_check_box.checkState() else self.current_rgb
        self.update_color_tab(self.rgb_tab, arr, tarr)


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
        tarr = self.current_hsvF if self.raw_check_box.checkState() else self.current_hsv
        self.update_color_tab(self.hsv_tab, arr, tarr)


    def update_color_tab(self, tab, arr, tarr):
        stylesheet_start = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0"
        for i in range(len(tab.frames)):
            if tab.line_edits[i].signalsBlocked():
                tab.line_edits[i].blockSignals(False)
                continue
            stylesheet = stylesheet_start + ", {});".format(arr[i])
            tab.frames[i].setStyleSheet(stylesheet)
            tab.line_edits[i].blockSignals(True)
            if self.raw_check_box.checkState():
                tab.line_edits[i].setText("{:.3f}".format(tarr[i]))
            else:
                tab.line_edits[i].setText(str(tarr[i]))
            tab.line_edits[i].blockSignals(False)


    def update_values_tab(self):
        self.values_hex_line_edit.setText("{}".format(self.current_color.name().upper()))
        self.values_rgb_line_edit.setText("{}, {}, {}".format(self.current_color.red(), self.current_color.green(), self.current_color.blue()))
        self.values_rgbf_line_edit.setText("{:.3f}, {:.3f}, {:.3f}".format(self.current_color.redF(), self.current_color.greenF(), self.current_color.blueF()))
        self.values_hsv_line_edit.setText("{}, {}, {}".format(self.current_color.hue(), self.current_color.saturation(), self.current_color.value()))
        self.values_hsvf_line_edit.setText("{:.3f}, {:.3f}, {:.3f}".format(self.current_color.hueF(), self.current_color.saturationF(), self.current_color.valueF()))


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


    def generate_tab_widget(self, name, max_values, is_rgb) -> Tab:
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(7)
        layout.setContentsMargins(0, 20, 0, 15)
        widget = QWidget()
        widget.setLayout(layout)
        tab = Tab(widget, name)
        for i in range(3):
            label = QLabel(name[i:i + 1])
            label.setFixedWidth(10)
            label.setAlignment(Qt.AlignmentFlag(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
            layout.addWidget(label, i, 0)

            frame_width = 310
            frame = QFrame()
            frame.setFixedSize(frame_width, 20)
            layout.addWidget(frame, i, 1)
            tab.frames.append(frame)

            line_edit = QLineEdit()
            line_edit.setFixedSize(55, 20)
            line_edit.setAlignment(Qt.AlignmentFlag(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
            self.set_non_raw_validator(line_edit)
            layout.addWidget(line_edit, i, 2)
            tab.line_edits.append(line_edit)

            click_func = partial(self.on_gradient_click, frame_width, max_values[i], i, is_rgb, False, False)
            scroll_func = partial(self.on_gradient_scroll, max_values[i], i, is_rgb, False, True)
            text_change_func = partial(self.on_text_changed, line_edit, max_values[i], i, is_rgb)

            frame.mousePressEvent = click_func
            frame.mouseMoveEvent = click_func
            frame.wheelEvent = scroll_func
            line_edit.wheelEvent = scroll_func
            line_edit.textChanged.connect(text_change_func)

            line_indicator = QFrame(frame)
            tab.line_indicators.append(line_indicator)

        return tab


    def generate_values_tab(self):
        values_hex_label = QLabel("HEX:")
        values_rgb_label = QLabel("RGB:")
        values_rgbf_label = QLabel("RGBF:")
        values_hsv_label = QLabel("HSV:")
        values_hsvf_label = QLabel("HSVF:")

        self.values_hex_line_edit = QLineEdit()
        self.values_hex_line_edit.setReadOnly(True)
        self.values_hex_line_edit.mouseReleaseEvent = partial(self.on_line_edit_clicked, self.values_hex_line_edit)
        self.values_rgb_line_edit = QLineEdit()
        self.values_rgb_line_edit.setReadOnly(True)
        self.values_rgb_line_edit.mouseReleaseEvent = partial(self.on_line_edit_clicked, self.values_rgb_line_edit)
        self.values_rgbf_line_edit = QLineEdit()
        self.values_rgbf_line_edit.setReadOnly(True)
        self.values_rgbf_line_edit.mouseReleaseEvent = partial(self.on_line_edit_clicked, self.values_rgbf_line_edit)
        self.values_hsv_line_edit = QLineEdit()
        self.values_hsv_line_edit.setReadOnly(True)
        self.values_hsv_line_edit.mouseReleaseEvent = partial(self.on_line_edit_clicked, self.values_hsv_line_edit)
        self.values_hsvf_line_edit = QLineEdit()
        self.values_hsvf_line_edit.setReadOnly(True)
        self.values_hsvf_line_edit.mouseReleaseEvent = partial(self.on_line_edit_clicked, self.values_hsvf_line_edit)

        values_layout = QGridLayout()
        values_layout.setContentsMargins(0, 20, 0, 15)
        values_layout.setHorizontalSpacing(6)
        values_layout.setVerticalSpacing(6)
        values_layout.setColumnStretch(1, 6)
        values_layout.setColumnStretch(2, 1)
        values_layout.setColumnStretch(4, 6)
        values_layout.addWidget(values_hex_label, 0, 0)
        values_layout.addWidget(self.values_hex_line_edit, 0, 1)
        values_layout.addWidget(values_rgb_label, 1, 0)
        values_layout.addWidget(self.values_rgb_line_edit, 1, 1)
        values_layout.addWidget(values_rgbf_label, 2, 0)
        values_layout.addWidget(self.values_rgbf_line_edit, 2, 1)
        values_layout.addWidget(values_hsv_label, 1, 3)
        values_layout.addWidget(self.values_hsv_line_edit, 1, 4)
        values_layout.addWidget(values_hsvf_label, 2, 3)
        values_layout.addWidget(self.values_hsvf_line_edit, 2, 4)
        values_widget = QWidget()
        values_widget.setLayout(values_layout)
        return values_widget


    def set_raw_validator(self, line_edit):
        reg_ex = QRegExp("^([01.]{,1}|[01].)[0-9]{,3}")
        input_validator = QRegExpValidator(reg_ex, line_edit)
        line_edit.setValidator(input_validator)


    def set_non_raw_validator(self, line_edit):
        reg_ex = QRegExp("[0-9]{,3}")
        input_validator = QRegExpValidator(reg_ex, line_edit)
        line_edit.setValidator(input_validator)


    def closeEvent(self, event):
        app.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
