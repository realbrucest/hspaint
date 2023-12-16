from PyQt5.QtWidgets import QLabel, QRadioButton, QVBoxLayout, QWidget, QPushButton, QFileDialog, QDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from random import randint
from color_picker_label import ColorPickerLabel
from palette_editor import PaletteEditor

class NewCopperDialog(QDialog):
    def __init__(self, previous_palette=None, parent=None):
        super().__init__(parent)
        self.palette_option = None
        self.palette_text = None
        self.previous_palette = previous_palette
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Seleccione una opción:")
        layout.addWidget(label)

        self.load_palette_button = QRadioButton("Cargar paleta desde archivo PAL", self)
        self.modify_palette_button = QRadioButton("Modificar paleta previa", self)
        self.random_palette_button = QRadioButton("Generar nueva paleta aleatoria", self)

        self.load_palette_button.clicked.connect(lambda: self.set_palette_option("load"))
        self.modify_palette_button.clicked.connect(self.display_previous_palette)
        self.random_palette_button.clicked.connect(lambda: self.set_palette_option("random"))

        layout.addWidget(self.load_palette_button)
        layout.addWidget(self.modify_palette_button)
        layout.addWidget(self.random_palette_button)

        self.palette_display_layout = QHBoxLayout()
        layout.addLayout(self.palette_display_layout)

        # Inicializar el botón de regenerar como invisible
        self.regenerate_button = QPushButton("Regenerar", self)
        self.regenerate_button.clicked.connect(self.regenerate_palette)
        self.regenerate_button.hide()  # Ocultar inicialmente el botón de regenerar

        layout.addWidget(self.regenerate_button)

        confirm_button = QPushButton("Confirmar", self)
        confirm_button.clicked.connect(self.confirm_palette)
        layout.addWidget(confirm_button)

        self.setLayout(layout)

    def set_palette_option(self, option):
        self.palette_option = option
        # Limpiar la paleta y ocultar el botón "Regenerar" al cambiar la opción
        self.clear_palette_display()
        self.hide_regenerate_button()

    def confirm_palette(self):
        # Limpiar la paleta al confirmar
        self.clear_palette_display()

        if self.palette_option == "load":
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Select PAL file", "", "PAL Files (*.pal);;All Files (*)")

            if file_path:
                self.palette_text = file_path
                self.load_palette_from_file(file_path)
        elif self.palette_option == "modify":
            self.display_previous_palette()
        elif self.palette_option == "random":
            self.generate_and_display_random_palette()

    def load_palette_from_file(self, file_path):
        try:
            palette_colors = PaletteEditor.load_palette_from_file(file_path)
            # Limpiar la paleta antes de cargarla
            self.display_palette(palette_colors)
            self.hide_regenerate_button()  # Ocultar el botón de regenerar
        except ValueError as e:
            print(f"Error al cargar la paleta desde el archivo: {e}")

    def generate_random_palette(self):
        return [(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(16)]

    def generate_and_display_random_palette(self):
        # Limpiar la paleta aleatoria al regenerarla
        self.display_palette(self.generate_random_palette())
        self.show_regenerate_button()

    def display_palette(self, palette):
        # Mostrar los colores de la paleta horizontalmente
        for color in palette:
            color_label = ColorPickerLabel(color, self)
            self.palette_display_layout.addWidget(color_label)

    def display_previous_palette(self):
        # Limpiar la paleta aleatoria antes de mostrar la paleta previa
        if self.palette_option == "random":
            self.clear_palette_display()
        self.display_palette(self.get_previous_palette())

    def clear_palette_display(self):
        # Limpiar cualquier widget anterior en el diseño de la paleta
        for i in reversed(range(self.palette_display_layout.count())):
            item = self.palette_display_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

    def regenerate_palette(self):
        # Limpiar la paleta aleatoria al regenerarla
        if self.palette_option == "random":
            self.clear_palette_display()
            self.generate_and_display_random_palette()

    def show_regenerate_button(self):
        self.regenerate_button.show()

    def hide_regenerate_button(self):
        self.regenerate_button.hide()

    def get_previous_palette(self):
        return self.previous_palette
