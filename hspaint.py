from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QColorDialog, QWidget, QFileDialog, QRadioButton, QGroupBox, QShortcut, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QColor, QKeySequence
from PyQt5.QtCore import Qt, QEvent
from PIL import Image
import sys

DEFAULT_ZOOM_LEVEL = 4.0

class ImageEditorWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        # Cargar la imagen original
        self.image_path = image_path
        self.image = Image.open(image_path)

        # Historial de paletas y niveles de zoom para deshacer
        self.edit_history = []

        # Crear una etiqueta para mostrar la imagen completa con todas las líneas
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(self.image)))

        # Colocar la etiqueta dentro de un QScrollArea
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

    def eventFilter(self, source, event):
        if source == self.scroll_area and event.type() == QEvent.MouseMove:
            self.update_mouse_position(event)
        return super().eventFilter(source, event)

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
        # Obtener la paleta actual
        palette = self.image.getpalette()

        # Actualizar el color en la paleta
        palette[index * 3: (index + 1) * 3] = new_color

        # Aplicar la paleta actualizada a la imagen
        self.image.putpalette(palette)

    def set_zoom_level(self, level):
        # Guardar el estado actual en el historial
        self.edit_history.append(self.get_current_state())

        new_size = (int(self.image.width * level), int(self.image.height * level))
        resized_image = self.image.resize(new_size)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(resized_image)))

    def get_current_zoom_level(self):
        for i, radio_button in enumerate(self.zoom_radio_buttons):
            if radio_button.isChecked():
                return float(radio_button.text().replace('x', ''))

    def undo_last_change(self):
        # Deshacer el último cambio si hay cambios en el historial
        if self.edit_history:
            last_state = self.edit_history.pop()

            # Restaurar la paleta y el nivel de zoom
            self.image.putpalette(last_state['palette'])
            self.set_zoom_level(last_state['zoom_level'])

            # Revertir los colores de los color-pickers
            for i, color in enumerate(last_state['palette'][:48:3]):  # Tomar solo los valores R de la paleta
                self.color_label_group[i].setStyleSheet(f"background-color: rgb{self.original_colors[i]};")

            self.update_image_with_current_zoom()

    def update_image_with_current_zoom(self):
        current_zoom = self.get_current_zoom_level()
        new_size = (int(self.image.width * current_zoom), int(self.image.height * current_zoom))
        resized_image = self.image.resize(new_size)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(resized_image)))

    def get_current_state(self):
        return {
            'palette': self.image.getpalette().copy(),
            'zoom_level': self.get_current_zoom_level(),
        }

    def update_mouse_position(self, event):
        # Obtener la posición X e Y del ratón
        x_position = int(event.x() / self.get_current_zoom_level())
        y_position = int(event.y() / self.get_current_zoom_level())

        # Actualizar los QLabel en el panel lateral
        self.x_position_label.setText(f"Posición X: {x_position}")
        self.y_position_label.setText(f"Posición Y: {y_position}")

    def apply_copper_effect(image_widget, lines_per_group=8):
        total_lines = image_widget.image.height
        for start_line in range(0, total_lines, lines_per_group):
            # Obtener la paleta actual
            palette = image_widget.image.getpalette()

            # Modificar los cuatro primeros índices de color
            for i in range(4):
                new_color = (i * 10, i * 10, i * 10)  # Cambiar por los colores deseados
                palette[i * 3: (i + 1) * 3] = new_color

            # Aplicar la paleta modificada a las líneas correspondientes
            for line in range(start_line, min(start_line + lines_per_group, total_lines)):
                image_widget.change_palette_color_at_index(line, palette)

            # Actualizar la etiqueta de la imagen con el nivel de zoom actual
            image_widget.update_image_with_current_zoom()


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
