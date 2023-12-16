from PyQt5.QtWidgets import QLabel, QRadioButton, QVBoxLayout, QWidget, QPushButton, QFileDialog, QDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
from random import randint
from color_picker_label import ColorPickerLabel

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

        load_palette_button = QRadioButton("Cargar paleta desde archivo PAL", self)
        modify_palette_button = QRadioButton("Modificar paleta previa", self)
        random_palette_button = QRadioButton("Generar nueva paleta aleatoria", self)

        load_palette_button.toggled.connect(lambda: self.set_palette_option("load"))
        modify_palette_button.toggled.connect(lambda: self.set_palette_option("modify"))
        random_palette_button.toggled.connect(lambda: self.set_palette_option("random"))

        layout.addWidget(load_palette_button)
        layout.addWidget(modify_palette_button)
        layout.addWidget(random_palette_button)

        confirm_button = QPushButton("Confirmar", self)
        confirm_button.clicked.connect(self.confirm_palette)
        layout.addWidget(confirm_button)

        self.palette_display_layout = QHBoxLayout()
        layout.addLayout(self.palette_display_layout)

        self.setLayout(layout)

    def set_palette_option(self, option):
        self.palette_option = option

    def confirm_palette(self):
        if self.palette_option == "load":
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Select PAL file", "", "PAL Files (*.pal);;All Files (*)")

            if file_path:
                self.palette_text = file_path
        elif self.palette_option == "modify":
            # Obtener la paleta previa del Copper de índice cero
            previous_palette = self.get_previous_palette()
            self.display_palette(previous_palette)
        elif self.palette_option == "random":
            # Lógica para generar una nueva paleta aleatoria
            new_palette = self.generate_random_palette()
            self.display_palette(new_palette)


    def generate_random_palette(self):
        return [(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(16)]

    def display_palette(self, palette):
        self.clear_palette_display()

        # Mostrar los colores de la paleta horizontalmente
        for color in palette:
            color_label = ColorPickerLabel(color, self)
            self.palette_display_layout.addWidget(color_label)

        # Añadir el botón de regenerar
        regenerate_button = QPushButton("Regenerar", self)
        regenerate_button.clicked.connect(self.regenerate_palette)
        self.palette_display_layout.addWidget(regenerate_button)

    def clear_palette_display(self):
        # Limpiar cualquier widget anterior en el diseño de la paleta
        for i in reversed(range(self.palette_display_layout.count())):
            item = self.palette_display_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

    def regenerate_palette(self):
        new_palette = self.generate_random_palette()
        self.display_palette(new_palette)
    
    def get_previous_palette(self):
        return self.coppers[-1].palette