from PyQt5.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from new_copper_widget import NewCopperWidget  # Importar el nuevo widget

class Copper:
    def __init__(self, position, palette):
        self.position = position
        self.palette = palette

class CopperEffectEditor:
    def __init__(self, image_lines, coppers, side_layout, edit_history, status_label, sender_button=None):
        self.image_lines = image_lines
        self.coppers = coppers
        self.side_layout = side_layout
        self.edit_history = edit_history
        self.status_label = status_label
        self.sender_button = sender_button
        self.new_copper_widget = None  # Cambiar de NewCopperDialog a NewCopperWidget

        # Llama al método para inicializar la interfaz gráfica
        self.init_ui_elements()

    def init_ui_elements(self):
        self.copper_palette_info_label = QLabel()
        self.copper_list_widget = QListWidget()

        # Conectar el nuevo botón al método launch_new_copper_widget
        if self.sender_button:
            self.sender_button.clicked.connect(lambda: self.launch_new_copper_widget(self.image_lines.index(self.sender_button)))

        # Agregar funcionalidad a los botones de la lista de Coppers
        self.copper_list_widget.itemClicked.connect(self.show_copper_palette_info)
        self.copper_list_widget.itemDoubleClicked.connect(self.edit_copper_palette)

        self.copper_palette_info_label.setAlignment(Qt.AlignCenter)

        self.update_copper_list_widget()

        self.side_layout.addWidget(self.copper_palette_info_label)
        self.side_layout.addWidget(self.copper_list_widget)

    def update_copper_list_widget(self):
        self.copper_list_widget.clear()
        for i, copper in enumerate(self.coppers):
            item_text = f"Copper {i + 1} - Posición: {copper.position}"
            self.copper_list_widget.addItem(item_text)

    def show_copper_palette_info(self, item):
        # Obtener el índice del Copper seleccionado
        index = self.copper_list_widget.row(item)
        if index >= 0:
            copper = self.coppers[index]
            palette_text = self.get_palette_text(copper.palette)
            self.copper_palette_info_label.setText(f"Paleta de Copper {index + 1}:\n{palette_text}")

    def get_palette_text(self, palette):
        return ", ".join([str(color) for color in palette])

    def edit_copper_palette(self, item):
        # Obtener el índice del Copper seleccionado
        index = self.copper_list_widget.row(item)
        if index >= 0:
            copper = self.coppers[index]
            if not self.new_copper_widget:
                self.new_copper_widget = NewCopperWidget(copper.palette, parent=self)

            # Mostrar el widget como un diálogo
            self.new_copper_widget.show()

    def launch_new_copper_widget(self, position):
        if not self.new_copper_widget:
            previous_palette = self.get_previous_palette()  # Obtener la paleta del copper anterior
            self.new_copper_widget = NewCopperWidget(previous_palette, parent=None)

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

    def apply_copper_effect(self, current_palette, button_index=None):
        position = self.get_copper_position(button_index)

        for i, image_line in enumerate(self.image_lines):
            copper_instance = self.get_copper_instance_at_position(i)

            if copper_instance and i >= copper_instance.position:
                image_line.palette_index = copper_instance.palette[i % 16]
            else:
                image_line.palette_index = current_palette[i % 16]

        # Asegúrate de tener un atributo slider_label definido
        if hasattr(self, 'slider_label'):
            self.slider_label.setText(f"Posición Y del Slider: {position}")

        self.status_label.setText("Efecto Copper: Activado")
        self.show_copper_palettes()

    def get_copper_instance_at_position(self, position):
        for copper in self.coppers:
            if copper.position == position:
                return copper

        return None

    def show_warning_dialog(self, message):
        warning_dialog = QMessageBox(self)
        warning_dialog.setIcon(QMessageBox.Warning)
        warning_dialog.setText(message)
        warning_dialog.setWindowTitle("Advertencia")
        warning_dialog.exec_()

    def get_previous_palette(self):
        if self.edit_history:
            return self.edit_history[-1]['palettes']
        else:
            return [0] * 16

    def get_palette_text_from_widget(self):
        return self.new_copper_widget.get_palette_text()

    def show_copper_palettes(self):
        for copper in self.coppers:
            print(f"Copper en posición {copper.position}: {copper.palette}")
