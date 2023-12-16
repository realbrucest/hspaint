from PyQt5.QtWidgets import QLabel, QDialog, QLineEdit, QVBoxLayout, QWidget, QRadioButton, QPushButton, QFileDialog
from PyQt5.QtCore import Qt

class NewCopperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.palette_option = None
        self.palette_text = None
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
            # Lógica para modificar la paleta previa
            self.palette_text = "Modify Palette"  # Reemplaza esto con tu lógica
        elif self.palette_option == "random":
            # Lógica para generar una nueva paleta aleatoria
            self.palette_text = "Random Palette"  # Reemplaza esto con tu lógica

        self.accept()
