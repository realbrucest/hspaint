from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QColorDialog, QWidget,
    QRadioButton, QGroupBox, QShortcut, QScrollArea, QMessageBox, QCheckBox, QPushButton, QSlider
)
from PyQt5.QtGui import QPixmap, QImage, QColor, QKeySequence
from PyQt5.QtCore import Qt, QEvent
from PIL import Image
from random import randint
import sys

from image_line import ImageLine
from palette_editor import PaletteEditor
from copper_effect_editor import Copper, CopperEffectEditor
from new_copper_widget import NewCopperWidget

from color_picker_label import ColorPickerLabel  # Importamos la nueva clase

DEFAULT_ZOOM_LEVEL = 1.0
INTERRUPTION_SPACING = 32
SCREEN_HEIGHT = 224


class ImageEditorWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        self.image_path = image_path
        self.image = Image.open(image_path)
        # Verificar que la imagen no exceda la altura de pantalla
        if self.image.height > SCREEN_HEIGHT:
            error_message = f"La imagen es demasiado grande. La altura máxima permitida es {SCREEN_HEIGHT} píxeles."
            QMessageBox.warning(self, "Error", error_message)
            sys.exit(1)

        self.edit_history = []
        self.coppers = []
        self.image_lines = []
        self.initialize_image_lines()
        self.palette_editor = PaletteEditor(self.image_lines)
        self.initial_palette = [self.palette_editor.get_palette_color(i) for i in range(16)]
        self.create_copper_zero()
        self.new_copper_widget = None
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
            color_label = ColorPickerLabel(self.palette_editor.get_palette_color(i), self)  # Usamos la nueva clase
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
        raster_group_box = QGroupBox("Raster")
        default_zoom_index = zoom_levels.index(DEFAULT_ZOOM_LEVEL)
        self.zoom_radio_buttons[default_zoom_index].setChecked(True)
        self.set_zoom_level(DEFAULT_ZOOM_LEVEL)
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo_last_change)
        main_layout = QVBoxLayout(self)
        main_layout_splitter = QHBoxLayout()
        main_layout_splitter.addWidget(self.scroll_area)
        side_panel = QWidget(self)
        side_panel.setFixedWidth(400)
        # Agregar el QScrollArea para los NewCopperWidget
        self.scroll_area_coppers = QScrollArea(self)
        self.scroll_area_coppers.setWidgetResizable(True)
        self.scroll_area_coppers.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area_coppers.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_coppers_widget = QWidget()
        self.scroll_area_coppers_layout = QVBoxLayout(self.scroll_area_coppers_widget)
        self.scroll_area_coppers.setWidget(self.scroll_area_coppers_widget)
        self.side_layout = QVBoxLayout(side_panel)
        self.x_position_label = QLabel(self)
        self.side_layout.addWidget(self.x_position_label)
        self.y_position_label = QLabel(self)
        self.side_layout.addWidget(self.y_position_label)
        self.slider_position_label = QLabel(self)
        self.side_layout.addWidget(self.slider_position_label)
        self.copper_status_label = QLabel(self)
        self.side_layout.addWidget(self.copper_status_label)
        self.side_layout.addWidget(self.scroll_area_coppers)
        self.initial_palette_group = QGroupBox("Paleta Inicial")
        self.initial_color_layout = QHBoxLayout(self.initial_palette_group)
        for i, color in enumerate(self.initial_palette):
            color_label = ColorPickerLabel(color, self)  # Usamos la nueva clase
            self.initial_color_layout.addWidget(color_label)
        self.side_layout.addWidget(self.initial_palette_group)
        main_layout_splitter.addWidget(side_panel)
        main_layout.addLayout(main_layout_splitter)
        main_layout.addWidget(color_group_box)
        main_layout.addWidget(zoom_group_box)
        main_layout.addWidget(self.copper_checkbox)
        main_layout.addWidget(raster_group_box)
        self.scroll_area.installEventFilter(self)
        self.copper_buttons = []
        self.initialize_copper_buttons()
        self.copper_effect_editor = CopperEffectEditor(
            self.image_lines,
            self.coppers,
            self.side_layout,
            self.edit_history,
            self.copper_status_label,
            sender_button=None  # No se necesita el botón en este punto
        )

    def initialize_copper_buttons(self):
        for i in range(1, SCREEN_HEIGHT // INTERRUPTION_SPACING + 1):
            new_copper_widget = NewCopperWidget(self.get_previous_copper_palette(), parent=self)
            new_copper_widget.accepted.connect(self.on_new_copper_widget_accepted)
            self.scroll_area_coppers_layout.addWidget(new_copper_widget)

        # Conectar cada botón a la función apply_copper_effect_for_button
        for button in self.copper_buttons:
            button.clicked.connect(self.apply_copper_effect_for_button)

    def apply_copper_effect_for_button(self):
        # Obtener el índice del botón que se ha presionado
        button_index = self.copper_buttons.index(self.sender())

        # Obtener la paleta actual y aplicar el efecto Copper
        current_palette = [self.palette_editor.get_palette_color(i) for i in range(16)]
        self.copper_effect_editor.apply_copper_effect(current_palette, button_index)

    def get_previous_copper_palette(self):
        if len(self.coppers) > 1:
            return self.coppers[-2].palette
        else:
            return [0] * 16

    def add_copper_instance(self, position):
        # Crear Copper en la posición especificada
        self.copper_effect_editor.add_copper_instance(position)

    def create_copper_zero(self):
        # Creamos el Copper cero con la paleta de la imagen cargada
        copper_zero_palette = [self.palette_editor.get_palette_color(i) for i in range(16)]
        self.coppers.append(Copper(position=0, palette=copper_zero_palette))

    def initialize_image_lines(self):
        for i in range(self.image.height):
            line_image = self.image.crop((0, i, self.image.width, i + 1))
            palette_index = i % 16
            self.image_lines.append(ImageLine(line_image, palette_index))

    def toggle_copper_effect(self, state):
        effect_enabled = state == Qt.Checked
        self.copper_status_label.setText(f"Efecto Copper: {'Activado' if effect_enabled else 'Desactivado'}")
        self.initial_palette_group.setVisible(True)

        if effect_enabled:
            # Ocultar los botones cuando el efecto Copper está activado
            for button in self.copper_buttons:
                button.hide()
            self.copper_effect_editor.apply_copper_effect(self.initial_palette)
            self.update_image_with_current_zoom()
            self.copper_effect_editor.show_copper_palettes()
        else:
            self.reset_copper_effect()
            # Mostrar los botones cuando el efecto Copper está desactivado
            for button in self.copper_buttons:
                button.show()


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

    def launch_new_copper_widget(self, position):
        if not self.new_copper_widget:
            self.new_copper_widget = NewCopperWidget(self.get_previous_palette(), parent=self)

        # Conectar el slot del widget para actualizar la lista y paletas cuando se acepta
        self.new_copper_widget.accepted.connect(lambda: self.on_new_copper_widget_accepted(position))

        # Mostrar el widget
        self.new_copper_widget.show()

    def on_new_copper_widget_accepted(self, position):
        new_palette = self.new_copper_widget.get_selected_palette()
        new_copper = Copper(position=position, palette=new_palette)
        self.coppers.append(new_copper)

        self.show_copper_palettes()
        self.update_copper_list_widget()

        palette_text = self.get_palette_text_from_widget()
        print(f"Nueva paleta seleccionada: {palette_text}")


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
