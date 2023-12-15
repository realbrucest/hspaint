from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QColorDialog, QWidget, QFileDialog, QRadioButton, QGroupBox, QShortcut, QScrollArea, QCheckBox, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QImage, QColor, QKeySequence
from PyQt5.QtCore import Qt, QEvent
from PIL import Image
from random import randint
import sys

DEFAULT_ZOOM_LEVEL = 4.0

class ImageLine:
    def __init__(self, image, palette_index):
        self.image = image
        self.palette_index = palette_index

class Copper:
    def __init__(self, position, palette):
        self.position = position
        self.palette = palette

class ImageEditorWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        # Cargar la imagen original
        self.image_path = image_path
        self.image = Image.open(image_path)

        # Historial de paletas y niveles de zoom para deshacer
        self.edit_history = []

        # Lista para almacenar las instancias de Copper
        self.coppers = []

        # Crear una etiqueta para mostrar la imagen completa con todas las líneas
        self.image_lines = []
        self.initialize_image_lines()

        # Obtener la paleta inicial
        self.initial_palette = [self.get_palette_color(i) for i in range(16)]

        # Colocar la etiqueta dentro de un QScrollArea
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(self.get_combined_image())))
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)

        # Grupo de labels para la paleta de colores
        color_group_box = QGroupBox("Paleta de Colores")
        color_layout = QHBoxLayout(color_group_box)
        color_layout.setContentsMargins(0, 0, 0, 0)
        self.color_label_group = []
        self.original_colors = []  # Almacena los colores originales de los color-pickers
        for i in range(16):
            color_label = QLabel(self)
            color_label.setFixedSize(30, 30)
            original_color = self.get_palette_color(i)
            self.original_colors.append(original_color)
            color_label.setStyleSheet(f"background-color: rgb{original_color};")
            color_label.mousePressEvent = lambda event, i=i: self.show_color_picker(event, i)
            self.color_label_group.append(color_label)
            color_layout.addWidget(color_label)

        # Grupo de radiobuttons para el nivel de zoom
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

        # Nuevo control para activar/desactivar el efecto Copper
        self.copper_checkbox = QCheckBox("Activar Copper", self)
        self.copper_checkbox.setChecked(False)
        self.copper_checkbox.stateChanged.connect(self.toggle_copper_effect)

        # Nuevo botón para generar una nueva paleta
        self.generate_palette_button = QPushButton("Generar Nueva Paleta", self)
        self.generate_palette_button.clicked.connect(self.generate_new_palette)

        # Nuevo control deslizante para seleccionar la posición del Copper
        self.copper_position_slider = QSlider(Qt.Horizontal, self)
        self.copper_position_slider.setMaximum(self.image.height - 1)
        self.copper_position_slider.setValue(0)
        self.copper_position_slider.valueChanged.connect(self.update_copper_position)

        # Establecer el zoom predeterminado
        default_zoom_index = zoom_levels.index(DEFAULT_ZOOM_LEVEL)
        self.zoom_radio_buttons[default_zoom_index].setChecked(True)
        self.set_zoom_level(DEFAULT_ZOOM_LEVEL)

        # Atajo de teclado para deshacer (Ctrl+Z)
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo_last_change)

        # Diseño del diseño principal
        main_layout = QVBoxLayout(self)

        # Dividir la ventana en dos secciones: izquierda (QScrollArea) y derecha (panel lateral)
        main_layout_splitter = QHBoxLayout()
        main_layout_splitter.addWidget(self.scroll_area)

        # Agregar el panel lateral
        side_panel = QWidget(self)
        side_panel.setFixedWidth(240)  # Ancho del panel lateral
        self.side_layout = QVBoxLayout(side_panel)

        # Nuevo QLabel para mostrar la posición X
        self.x_position_label = QLabel(self)
        self.side_layout.addWidget(self.x_position_label)

        # Nuevo QLabel para mostrar la posición Y
        self.y_position_label = QLabel(self)
        self.side_layout.addWidget(self.y_position_label)

        # Nuevo QLabel para mostrar la posición Y del slider
        self.slider_position_label = QLabel(self)
        self.side_layout.addWidget(self.slider_position_label)

        # Nuevo QLabel para mostrar si el efecto Copper está activado
        self.copper_status_label = QLabel(self)
        self.side_layout.addWidget(self.copper_status_label)

        # Grupo para la paleta inicial
        self.initial_palette_group = QGroupBox("Paleta Inicial")
        self.initial_color_layout = QHBoxLayout(self.initial_palette_group)

        for i, color in enumerate(self.initial_palette):
            color_label = QLabel(self)
            color_label.setFixedSize(30, 30)
            color_label.setStyleSheet(f"background-color: rgb{color};")
            self.initial_color_layout.addWidget(color_label)

        # Agregar el grupo de la paleta inicial al layout lateral
        self.side_layout.addWidget(self.initial_palette_group)

        main_layout_splitter.addWidget(side_panel)
        main_layout.addLayout(main_layout_splitter)

        # Agregar la paleta y el grupo de zoom debajo de QScrollArea y el panel lateral
        main_layout.addWidget(color_group_box)
        main_layout.addWidget(zoom_group_box)

        # Agregar controles para el efecto Copper
        main_layout.addWidget(self.copper_checkbox)
        main_layout.addWidget(self.generate_palette_button)
        main_layout.addWidget(self.copper_position_slider)

        # Conectar el evento de movimiento del ratón para actualizar la posición Y
        self.scroll_area.installEventFilter(self)

    def get_palettes_array(self):
        # Obtener la paleta inicial desde las líneas de la imagen
        self.initialize_image_lines()
        return [self.get_palette_color(image_line.palette_index) for image_line in self.image_lines]

    def initialize_image_lines(self):
        # Inicializar las líneas de la imagen
        for i in range(self.image.height):
            line_image = self.image.crop((0, i, self.image.width, i + 1))
            palette_index = i % 16  # Inicializar con el índice correspondiente a la paleta original
            self.image_lines.append(ImageLine(line_image, palette_index))

    def toggle_copper_effect(self, state):
        if state == Qt.Checked:
            self.apply_copper_effect()
            self.copper_status_label.setText("Efecto Copper: Activado")
            self.initial_palette_group.show()  # Mostrar el grupo de la paleta inicial
        else:
            self.reset_copper_effect()
            self.copper_status_label.setText("Efecto Copper: Desactivado")
            self.initial_palette_group.hide()  # Ocultar el grupo de la paleta inicial


    
    def convert_pil_to_qimage(self, pil_image):
        image = pil_image.convert("RGBA")
        width, height = image.size
        bytes_per_line = 4 * width
        q_image = QImage(image.tobytes("raw", "RGBA"), width, height, bytes_per_line, QImage.Format_RGBA8888)
        return q_image
    
    def set_zoom_level(self, level):
        # Guardar el estado actual en el historial
        self.edit_history.append(self.get_current_state())

        new_size = (self.image.width, int(self.image.height * level))
        for image_line in self.image_lines:
            image_line.image = image_line.image.resize(new_size)

        # Actualizar la etiqueta de la imagen con el nivel de zoom actual
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

        # Crear una nueva imagen con todas las líneas combinadas
        combined_image = self.get_combined_image()

        # Escalar la imagen de acuerdo al nivel de zoom
        new_size = (int(combined_image.width * current_zoom), int(combined_image.height * current_zoom))
        resized_image = combined_image.resize(new_size)

        # Mostrar la imagen combinada y escalada en la etiqueta
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(resized_image)))

    def undo_last_change(self):
        # Deshacer el último cambio si hay cambios en el historial
        if self.edit_history:
            last_state = self.edit_history.pop()

            # Restaurar la paleta y el nivel de zoom
            for y, palette_index in last_state['palettes'].items():
                self.image_lines[y].palette_index = palette_index

            # Actualizar la etiqueta de la imagen con el nivel de zoom actual
            self.update_image_with_current_zoom()

    def show_color_picker(self, event, index):
        # Abrir el diálogo de selección de color
        color = QColorDialog.getColor(QColor(*self.get_palette_color(index)), self)

        if color.isValid():
            # Convertir el color de QColor a RGB tuple
            new_color = (color.red(), color.green(), color.blue())

            # Guardar el estado actual en el historial
            self.edit_history.append(self.get_current_state())

            # Cambiar el color en la paleta
            self.change_palette_color_at_index(index, new_color)

            # Actualizar el color del label
            self.update_color_label(index)

            # Actualizar la etiqueta de la imagen con el nivel de zoom actual
            self.update_image_with_current_zoom()

    def change_palette(self, new_palette):
        # Cambiar los colores en la paleta
        for i in range(16):
            self.change_palette_color_at_index(i % 16, new_palette[i])

            # Actualizar el color del label
            self.update_color_label(i % 16)

    def change_palette_color_at_index(self, index, new_color):
        # Obtener la paleta actualizada
        for image_line in self.image_lines:
            palette = image_line.image.getpalette()
            palette[index * 3: (index + 1) * 3] = new_color
            image_line.image.putpalette(palette)

    def update_color_label(self, index):
        color = self.get_palette_color(index)
        self.color_label_group[index].setStyleSheet(f"background-color: rgb{color};")


    def get_combined_image(self):
        # Crear una nueva imagen con todas las líneas combinadas
        combined_image = Image.new("RGBA", (self.image.width, self.image.height))

        for y, image_line in enumerate(self.image_lines):
            combined_image.paste(image_line.image, (0, y))

        return combined_image
    
    def get_palette_color(self, index):
        # Obtener la paleta actual
        palette = self.image.getpalette()

        # Obtener el color de la paleta correspondiente al índice
        color = palette[index * 3: (index + 1) * 3]
        return tuple(color)

    def apply_copper_effect(self):
        # Guardar el estado actual en el historial
        self.edit_history.append(self.get_current_state())

        # Obtener la paleta actualizada desde las líneas de la imagen
        current_palette = [self.get_palette_color(i) for i in range(16)]

        # Crear una nueva instancia de Copper y agregarla a la lista
        new_copper = Copper(self.copper_position_slider.value(), {i: color for i, color in enumerate(current_palette)})
        self.coppers.append(new_copper)

        # Aplicar el efecto Copper cambiando las paletas de las líneas de la imagen
        for i, image_line in enumerate(self.image_lines):
            image_line.palette_index = i % 16

        # Actualizar la etiqueta de la imagen con el nivel de zoom actual
        self.update_image_with_current_zoom()

        # Actualizar el QLabel de posición del slider
        self.slider_position_label.setText(f"Posición Y del Slider: {self.copper_position_slider.value()}")

        # Actualizar el QLabel de estado del Copper
        self.copper_status_label.setText("Efecto Copper: Activado")

        # Mostrar la paleta en el panel lateral
        self.show_copper_palettes()

    def show_copper_palettes(self):
        # Limpiar los QLabel anteriores en el layout lateral
        self.clear_layout(self.side_layout)

        # Función auxiliar para crear y agregar un grupo de paleta
        def add_palette_group(title, colors):
            group = QGroupBox(title)
            layout = QHBoxLayout(group)
            for color in colors:
                label = QLabel(self)
                label.setFixedSize(30, 30)
                label.setStyleSheet(f"background-color: rgb{color};")
                layout.addWidget(label)
            self.side_layout.addWidget(group)

        # Agregar grupos para cada paleta de Copper
        for i, copper in enumerate(self.coppers):
            add_palette_group(f"Paleta de Copper {i + 1}", copper.palette.values())

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)



    def reset_copper_effect(self):
        # Restaurar el estado del efecto Copper
        self.undo_last_change()

    def generate_new_palette(self):
        # Generar una nueva paleta de colores
        new_palette = [(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(16)]

        # Guardar el estado actual en el historial
        self.edit_history.append(self.get_current_state())

        # Cambiar los colores en la paleta
        self.change_palette(new_palette)

        # Actualizar la etiqueta de la imagen con el nivel de zoom actual
        self.update_image_with_current_zoom()

    def update_copper_position(self, position):
        # Guardar el estado actual en el historial
        self.edit_history.append(self.get_current_state())

        # Obtener la paleta actual
        self.palettes_array = self.get_palettes_array()

        # Desplazar el efecto Copper cambiando las paletas de las líneas de la imagen
        for i, image_line in enumerate(self.image_lines):
            image_line.palette_index = (i + position) % 16

        # Actualizar la etiqueta de la imagen con el nivel de zoom actual
        self.update_image_with_current_zoom()

        # Actualizar el QLabel de posición del slider
        self.slider_position_label.setText(f"Posición Y del Slider: {position}")

    def update_mouse_position(self, event):
        # Obtener la posición X e Y del ratón
        x_position = int(event.x() / self.get_current_zoom_level())
        y_position = int(event.y() / self.get_current_zoom_level())

        # Actualizar los QLabel en el panel lateral
        self.x_position_label.setText(f"Posición X: {x_position}")
        self.y_position_label.setText(f"Posición Y: {y_position}")

    def eventFilter(self, watched, event):
        # Filtrar eventos, en este caso, eventos de movimiento del ratón en el área de desplazamiento
        if watched == self.scroll_area and event.type() == QEvent.MouseMove:
            self.update_mouse_position(event)
        return super().eventFilter(watched, event)

