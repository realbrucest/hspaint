from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QColorDialog, QWidget, QFileDialog, QRadioButton, QGroupBox, QShortcut, QScrollArea, QCheckBox, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QImage, QColor, QKeySequence
from PyQt5.QtCore import Qt, QEvent
from PIL import Image
from random import randint
import sys

from image_line import ImageLine
from palette_editor import PaletteEditor
from copper_effect_editor import Copper, CopperEffectEditor

DEFAULT_ZOOM_LEVEL = 4.0





class ImageEditorWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        self.image_path = image_path
        self.image = Image.open(image_path)
        self.edit_history = []
        self.coppers = []
        self.image_lines = []
        self.initialize_image_lines()
        self.palette_editor = PaletteEditor(self.image_lines)
        self.initial_palette = [self.palette_editor.get_palette_color(i) for i in range(16)]
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(self.get_combined_image())))
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        color_group_box = QGroupBox("Paleta de Colores")
        color_layout = QHBoxLayout(color_group_box)
        color_layout.setContentsMargins(0, 0, 0, 0)
        self.color_label_group = []
        self.original_colors = []
        for i in range(16):
            color_label = QLabel(self)
            color_label.setFixedSize(30, 30)
            original_color = self.palette_editor.get_palette_color(i)
            self.original_colors.append(original_color)
            color_label.setStyleSheet(f"background-color: rgb{original_color};")
            color_label.mousePressEvent = lambda event, i=i: self.show_color_picker(event, i)
            self.color_label_group.append(color_label)
            color_layout.addWidget(color_label)
        zoom_group_box = QGroupBox("Niveles de Zoom")
        zoom_layout = QHBoxLayout(zoom_group_box)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        self.zoom_radio_buttons = []
        zoom_levels = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0]
        for level in zoom_levels:
            radio_button = QRadioButton(f"{level}x", self)
            radio_button.clicked.connect(lambda _, level=level: self.set_zoom_level(level))
            self.zoom_radio_buttons.append(radio_button)
            zoom_layout.addWidget(radio_button)
        self.copper_checkbox = QCheckBox("Activar Copper", self)
        self.copper_checkbox.setChecked(False)
        self.copper_checkbox.stateChanged.connect(self.toggle_copper_effect)
        self.generate_palette_button = QPushButton("Generar Nueva Paleta", self)
        self.generate_palette_button.clicked.connect(self.generate_new_palette)
        self.copper_position_slider = QSlider(Qt.Horizontal, self)
        self.copper_position_slider.setMaximum(self.image.height - 1)
        self.copper_position_slider.setValue(0)
        self.copper_position_slider.valueChanged.connect(self.update_copper_position)
        default_zoom_index = zoom_levels.index(DEFAULT_ZOOM_LEVEL)
        self.zoom_radio_buttons[default_zoom_index].setChecked(True)
        self.set_zoom_level(DEFAULT_ZOOM_LEVEL)
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo_last_change)
        main_layout = QVBoxLayout(self)
        main_layout_splitter = QHBoxLayout()
        main_layout_splitter.addWidget(self.scroll_area)
        side_panel = QWidget(self)
        side_panel.setFixedWidth(240)
        self.side_layout = QVBoxLayout(side_panel)
        self.x_position_label = QLabel(self)
        self.side_layout.addWidget(self.x_position_label)
        self.y_position_label = QLabel(self)
        self.side_layout.addWidget(self.y_position_label)
        self.slider_position_label = QLabel(self)
        self.side_layout.addWidget(self.slider_position_label)
        self.copper_status_label = QLabel(self)
        self.side_layout.addWidget(self.copper_status_label)
        self.initial_palette_group = QGroupBox("Paleta Inicial")
        self.initial_color_layout = QHBoxLayout(self.initial_palette_group)
        for i, color in enumerate(self.initial_palette):
            color_label = QLabel(self)
            color_label.setFixedSize(30, 30)
            color_label.setStyleSheet(f"background-color: rgb{color};")
            self.initial_color_layout.addWidget(color_label)
        self.side_layout.addWidget(self.initial_palette_group)
        main_layout_splitter.addWidget(side_panel)
        main_layout.addLayout(main_layout_splitter)
        main_layout.addWidget(color_group_box)
        main_layout.addWidget(zoom_group_box)
        main_layout.addWidget(self.copper_checkbox)
        main_layout.addWidget(self.generate_palette_button)
        main_layout.addWidget(self.copper_position_slider)
        self.scroll_area.installEventFilter(self)
        self.copper_effect_editor = CopperEffectEditor(
            self.image_lines,
            self.coppers,
            self.copper_position_slider,
            self.slider_position_label,
            self.side_layout,
            self.edit_history
        )

    def initialize_image_lines(self):
        for i in range(self.image.height):
            line_image = self.image.crop((0, i, self.image.width, i + 1))
            palette_index = i % 16
            self.image_lines.append(ImageLine(line_image, palette_index))

    def toggle_copper_effect(self, state):
        effect_enabled = state == Qt.Checked
        self.copper_status_label.setText(f"Efecto Copper: {'Activado' if effect_enabled else 'Desactivado'}")
        self.initial_palette_group.setVisible(effect_enabled)
        if effect_enabled:
            self.copper_effect_editor.apply_copper_effect(self.initial_palette)
            self.update_image_with_current_zoom()
        else:
            self.reset_copper_effect()

    def convert_pil_to_qimage(self, pil_image):
        image = pil_image.convert("RGBA")
        width, height = image.size
        bytes_per_line = 4 * width
        q_image = QImage(image.tobytes("raw", "RGBA"), width, height, bytes_per_line, QImage.Format_RGBA8888)
        return q_image

    def set_zoom_level(self, level):
        self.edit_history.append(self.get_current_state())
        new_size = (self.image.width, int(self.image.height * level))
        for image_line in self.image_lines:
            image_line.image = image_line.image.resize(new_size)
        self.update_image_with_current_zoom()

    def get_current_state(self):
        return {
            'palettes': {y: image_line.palette_index for y, image_line in enumerate(self.image_lines)},
            'zoom_level': self.get_current_zoom_level(),
        }

    def get_current_zoom_level(self):
        for i, radio_button in enumerate(self.zoom_radio_buttons):
            if radio_button.isChecked():
                return float(radio_button.text().replace('x', ''))

    def update_image_with_current_zoom(self):
        current_zoom = self.get_current_zoom_level()
        combined_image = self.get_combined_image()
        new_size = (int(combined_image.width * current_zoom), int(combined_image.height * current_zoom))
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(combined_image.resize(new_size))))

    def undo_last_change(self):
        if self.edit_history:
            last_state = self.edit_history.pop()
            for y, palette_index in last_state['palettes'].items():
                self.image_lines[y].palette_index = palette_index
            self.update_image_with_current_zoom()

    def show_color_picker(self, event, index):
        color = QColorDialog.getColor(QColor(*self.palette_editor.get_palette_color(index)), self)
        if color.isValid():
            new_color = (color.red(), color.green(), color.blue())
            self.edit_history.append(self.get_current_state())
            self.palette_editor.change_palette_color_at_index(index, new_color)
            self.update_color_label(index)
            self.update_image_with_current_zoom()

    def change_palette(self, new_palette):
        for i in range(16):
            self.palette_editor.change_palette_color_at_index(i % 16, new_palette[i])
            self.update_color_label(i % 16)

    def update_color_label(self, index):
        color = self.palette_editor.get_palette_color(index)
        self.color_label_group[index].setStyleSheet(f"background-color: rgb{color};")

    def get_combined_image(self):
        combined_image = Image.new("RGBA", (self.image.width, self.image.height))
        for y, image_line in enumerate(self.image_lines):
            combined_image.paste(image_line.image, (0, y))
        return combined_image

    def reset_copper_effect(self):
        self.undo_last_change()

    def generate_new_palette(self):
        position = self.copper_position_slider.value()
        new_palette = [(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(16)]
        self.edit_history.append(self.get_current_state())

        # Crear un nuevo objeto Copper
        new_copper = Copper(position, {i: color for i, color in enumerate(new_palette)})

        # Añadir el nuevo objeto Copper a la lista
        self.coppers.append(new_copper)

        # Actualizar la interfaz gráfica
        self.update_image_with_current_zoom()
        self.copper_effect_editor.show_copper_palettes()

    def update_copper_position(self, position):
        self.edit_history.append(self.get_current_state())
        self.palettes_array = self.palette_editor.get_palettes_array()
        for i, image_line in enumerate(self.image_lines):
            image_line.palette_index = (i + position) % 16
        self.update_image_with_current_zoom()
        self.slider_position_label.setText(f"Posición Y del Slider: {position}")

    def update_mouse_position(self, event):
        x_position = int(event.x() / self.get_current_zoom_level())
        y_position = int(event.y() / self.get_current_zoom_level())
        self.x_position_label.setText(f"Posición X: {x_position}")
        self.y_position_label.setText(f"Posición Y: {y_position}")

    def eventFilter(self, watched, event):
        if watched == self.scroll_area and event.type() == QEvent.MouseMove:
            self.update_mouse_position(event)
        return super().eventFilter(watched, event)
