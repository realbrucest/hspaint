from PyQt5.QtWidgets import QLabel, QColorDialog
from PyQt5.QtGui import QColor

class ColorPickerLabel(QLabel):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setStyleSheet(f"background-color: rgb{color};")
        self.color = color
        self.mousePressEvent = self.show_color_picker

    def show_color_picker(self, event):
        color_dialog = QColorDialog(self)
        color_dialog.setCurrentColor(QColor(*self.color))
        color_dialog.colorSelected.connect(self.update_color)
        color_dialog.exec_()

    def update_color(self, color):
        new_color = (color.red(), color.green(), color.blue())
        self.setStyleSheet(f"background-color: rgb{new_color};")
        self.color = new_color
