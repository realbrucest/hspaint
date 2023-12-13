from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QColorDialog, QWidget, QFileDialog, QRadioButton, QGroupBox, QShortcut, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QColor, QKeySequence
from PyQt5.QtCore import Qt, QEvent
from PIL import Image
import sys


DEFAULT_ZOOM_LEVEL = 4.0


class ImageLine:
    def __init__(self, image, palette_index):
        self.image = image
        self.palette_index = palette_index


class ImageEditorWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        # Cargar la imagen original
        self.image_path = image_path
        self.image = Image.open(image_path)

        # Historial de paletas y niveles de zoom para deshacer
        self.edit_history = []

        # Crear una etiqueta para mostrar la imagen completa con todas las líneas
        self.image_lines = []
        self.initialize_image_lines()

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
        side_layout = QVBoxLayout(side_panel)

        # Nuevo QLabel para mostrar la posición X
        self.x_position_label = QLabel(self)
        side_layout.addWidget(self.x_position_label)

        # Nuevo QLabel para mostrar la posición Y
        self.y_position_label = QLabel(self)
        side_layout.addWidget(self.y_position_label)

        main_layout_splitter.addWidget(side_panel)
        main_layout.addLayout(main_layout_splitter)

        # Agregar la paleta y el grupo de zoom debajo de QScrollArea y el panel lateral
        main_layout.addWidget(color_group_box)
        main_layout.addWidget(zoom_group_box)

        # Conectar el evento de movimiento del ratón para actualizar la posición Y
        self.scroll_area.installEventFilter(self)

    def initialize_image_lines(self):
        # Crear una línea para cada fila de la imagen original
        for y in range(self.image.height):
            line_image = self.image.crop((0, y, self.image.width, y + 1))
            palette_index = 0  # Inicializar con la paleta original
            image_line = ImageLine(line_image, palette_index)
            self.image_lines.append(image_line)

    def convert_pil_to_qimage(self, pil_image):
        image = pil_image.convert("RGBA")
        width, height = image.size
        bytes_per_line = 4 * width
        q_image = QImage(image.tobytes("raw", "RGBA"), width, height, bytes_per_line, QImage.Format_RGBA8888)
        return q_image

    def get_palette_color(self, index):
        # Obtener la paleta actual
        palette = self.image.getpalette()

        # Obtener el color de la paleta correspondiente al índice
        color = palette[index * 3: (index + 1) * 3]
        return tuple(color)

    def get_combined_image(self):
        # Crear una nueva imagen con todas las líneas combinadas
        combined_image = Image.new("RGBA", (self.image.width, self.image.height))

        for y, image_line in enumerate(self.image_lines):
            combined_image.paste(image_line.image, (0, y))

        return combined_image

    def update_color_label(self, index):
        color = self.get_palette_color(index)
        self.color_label_group[index].setStyleSheet(f"background-color: rgb{color};")

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

    def change_palette_color_at_index(self, index, new_color):
        # Obtener la paleta actualizada
        for image_line in self.image_lines:
            palette = image_line.image.getpalette()
            palette[index * 3: (index + 1) * 3] = new_color
            image_line.image.putpalette(palette)

    def set_zoom_level(self, level):
        # Guardar el estado actual en el historial
        self.edit_history.append(self.get_current_state())

        new_size = (self.image.width, int(self.image.height * level))
        for image_line in self.image_lines:
            image_line.image = image_line.image.resize(new_size)

        # Actualizar la etiqueta de la imagen con el nivel de zoom actual
        self.update_image_with_current_zoom()

    def get_current_zoom_level(self):
        for i, radio_button in enumerate(self.zoom_radio_buttons):
            if radio_button.isChecked():
                return float(radio_button.text().replace('x', ''))

    def undo_last_change(self):
        # Deshacer el último cambio si hay cambios en el historial
        if self.edit_history:
            last_state = self.edit_history.pop()

            # Restaurar la paleta y el nivel de zoom
            for y, palette_index in last_state['palettes'].items():
                self.image_lines[y].palette_index = palette_index

            # Actualizar la etiqueta de la imagen con el nivel de zoom actual
            self.update_image_with_current_zoom()

    def update_image_with_current_zoom(self):
        current_zoom = self.get_current_zoom_level()

        # Crear una nueva imagen con todas las líneas combinadas
        combined_image = self.get_combined_image()

        # Escalar la imagen de acuerdo al nivel de zoom
        new_size = (int(combined_image.width * current_zoom), int(combined_image.height * current_zoom))
        resized_image = combined_image.resize(new_size)

        # Mostrar la imagen combinada y escalada en la etiqueta
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(resized_image)))

    def get_current_state(self):
        return {
            'palettes': {y: image_line.palette_index for y, image_line in enumerate(self.image_lines)},
            'zoom_level': self.get_current_zoom_level(),
        }

    def update_mouse_position(self, event):
        # Obtener la posición X e Y del ratón
        x_position = int(event.x() / self.get_current_zoom_level())
        y_position = int(event.y() / self.get_current_zoom_level())

        # Actualizar los QLabel en el panel lateral
        self.x_position_label.setText(f"Posición X: {x_position}")
        self.y_position_label.setText(f"Posición Y: {y_position}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Abre un cuadro de diálogo para seleccionar una imagen
    file_dialog = QFileDialog()
    image_path, _ = file_dialog.getOpenFileName(None, "Seleccionar Imagen", "", "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)")

    if not image_path:
        sys.exit()

    # Crea y muestra la ventana principal de la aplicación maximizada
    window = QMainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle("Editor de Imágenes")
    window.showMaximized()  # Mostrar maximizado

    image_editor = ImageEditorWidget(image_path)
    window.setCentralWidget(image_editor)

    sys.exit(app.exec_())
