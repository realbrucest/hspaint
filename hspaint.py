from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QColorDialog, QWidget, QFileDialog, QRadioButton, QGroupBox
from PyQt5.QtGui import QPixmap, QImage, QColor
from PIL import Image
import sys

class ImageEditorWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        # Cargar la imagen original
        self.image_path = image_path
        self.image = Image.open(image_path)

        # Crear una etiqueta para mostrar la imagen
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(self.image)))

        # Grupo de labels para la paleta de 16 colores
        color_group_box = QGroupBox("Paleta de Colores")
        color_layout = QHBoxLayout(color_group_box)
        color_layout.setContentsMargins(0, 0, 0, 0)
        self.color_label_group = []
        for i in range(16):
            color_label = QLabel(self)
            color_label.setFixedSize(30, 30)
            color_label.setStyleSheet(f"background-color: rgb{self.get_palette_color(i)};")
            color_label.mousePressEvent = lambda event, i=i: self.show_color_picker(event, i)
            self.color_label_group.append(color_label)
            color_layout.addWidget(color_label)

        # Grupo de radiobuttons para el nivel de zoom
        zoom_group_box = QGroupBox("Niveles de Zoom")
        zoom_layout = QHBoxLayout(zoom_group_box)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        self.zoom_radio_buttons = []
        zoom_levels = [1.0, 1.5, 2.0, 3.0, 4.0]
        for level in zoom_levels:
            radio_button = QRadioButton(f"{level}x", self)
            radio_button.clicked.connect(lambda _, level=level: self.set_zoom_level(level))
            self.zoom_radio_buttons.append(radio_button)
            zoom_layout.addWidget(radio_button)

        # Diseño del diseño principal
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.addWidget(color_group_box)
        layout.addWidget(zoom_group_box)

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
        # Abrir el diálogo de selección de color
        color = QColorDialog.getColor(QColor(*self.get_palette_color(index)), self)

        if color.isValid():
            # Convertir el color de QColor a RGB tuple
            new_color = (color.red(), color.green(), color.blue())

            # Cambiar el color en la paleta
            self.change_palette_color_at_index(index, new_color)

            # Actualizar el color del label
            self.update_color_label(index)

            # Actualizar la etiqueta de la imagen
            self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(self.image)))

    def change_palette_color_at_index(self, index, new_color):
        # Obtener la paleta actual
        palette = self.image.getpalette()

        # Actualizar el color en la paleta
        palette[index * 3 : (index + 1) * 3] = new_color

        # Aplicar la paleta actualizada a la imagen
        self.image.putpalette(palette)

    def set_zoom_level(self, level):
        new_size = (int(self.image.width * level), int(self.image.height * level))
        resized_image = self.image.resize(new_size)
        self.image_label.setPixmap(QPixmap.fromImage(self.convert_pil_to_qimage(resized_image)))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Abre un cuadro de diálogo para seleccionar una imagen
    file_dialog = QFileDialog()
    image_path, _ = file_dialog.getOpenFileName(None, "Seleccionar Imagen", "", "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)")

    if not image_path:
        sys.exit()

    # Crea y muestra la ventana principal de la aplicación
    window = QMainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle("Editor de Imágenes")
    
    image_editor = ImageEditorWidget(image_path)
    window.setCentralWidget(image_editor)

    window.show()
    sys.exit(app.exec_())
