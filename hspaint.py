from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QColorDialog, QWidget, QFileDialog, QRadioButton, QGroupBox, QShortcut, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QColor, QKeySequence
from PIL import Image
import sys

class ImageEditorWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        # Cargar la imagen original
        self.image_path = image_path
        self.image = Image.open(image_path)

        # Historial de paletas y niveles de zoom para deshacer
        self.edit_history = []

        # Crear una etiqueta para mostrar la imagen
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(self.image)))

        # Colocar la etiqueta dentro de un QScrollArea
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.image_label)

        # Grupo de labels para la paleta de 16 colores
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

        # Establecer 4x como el zoom inicial
        self.zoom_radio_buttons[4].setChecked(True)  # Índice 4 corresponde a 4.0 en la lista de niveles de zoom
        self.set_zoom_level(4.0)

        # Atajo de teclado para deshacer (Ctrl+Z)
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo_last_change)

        # Diseño del diseño principal
        main_layout = QVBoxLayout(self)
        
        # Dividir la ventana en dos secciones: izquierda (QScrollArea) y derecha (panel lateral)
        main_layout_splitter = QHBoxLayout()
        main_layout_splitter.addWidget(scroll_area)
        
        # Agregar el panel lateral
        side_panel = QWidget(self)
        side_panel.setFixedWidth(240)  # Ancho del panel lateral
        side_layout = QVBoxLayout(side_panel)
        side_layout.addWidget(QLabel("Placeholder Text"))  # Contenido del panel lateral
        
        main_layout_splitter.addWidget(side_panel)
        main_layout.addLayout(main_layout_splitter)
        
        # Agregar la paleta y el grupo de zoom debajo de QScrollArea y el panel lateral
        main_layout.addWidget(color_group_box)
        main_layout.addWidget(zoom_group_box)

        self.updateGeometry()

    def convert_pil_to_qimage(self, pil_image):
        image = pil_image.convert("RGBA")
        width, height = image.size
        bytes_per_line = 4 * width
        q_image = QImage(image.tobytes("raw", "RGBA"), width, height, bytes_per_line, QImage.Format_RGBA8888)
        return q_image

    def convert_qimage_to_pil(self, q_image):
        buffer = q_image.bits().asstring(q_image.width() * q_image.height() * 4)
        pil_image = Image.frombytes("RGBA", (q_image.width(), q_image.height()), buffer, "raw", "RGBA", 0, 1)
        return pil_image

    def get_palette_color(self, index):
        # Obtener la paleta actual
        palette = self.image.getpalette()

        # Obtener el color de la paleta correspondiente al índice
        color = palette[index * 3 : (index + 1) * 3]
        return tuple(color)

    def update_color_label(self, index):
        color = self.get_palette_color(index)
        self.color_label_group[index].setStyleSheet(f"background-color: rgb{color};")

    def show_color_picker(self, event, index):
        # Guardar la paleta y el nivel de zoom actual en el historial
        current_state = {
            'palette': self.image.getpalette().copy(),
            'zoom_level': self.get_current_zoom_level(),
        }
        self.edit_history.append(current_state)

        # Abrir el diálogo de selección de color
        color = QColorDialog.getColor(QColor(*self.get_palette_color(index)), self)

        if color.isValid():
            # Convertir el color de QColor a RGB tuple
            new_color = (color.red(), color.green(), color.blue())

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
        palette[index * 3 : (index + 1) * 3] = new_color

        # Aplicar la paleta actualizada a la imagen
        self.image.putpalette(palette)

    def set_zoom_level(self, level):
        # Guardar la paleta y el nivel de zoom actual en el historial
        current_state = {
            'palette': self.image.getpalette().copy(),
            'zoom_level': self.get_current_zoom_level(),
        }
        self.edit_history.append(current_state)

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
