from PyQt5.QtWidgets import QLabel, QMessageBox

class Copper:
    def __init__(self, position, palette):
        self.position = position
        self.palette = palette
class CopperEffectEditor:
    def __init__(self, image_lines, coppers, copper_position_slider, slider_position_label, side_layout, edit_history, status_label):
        self.image_lines = image_lines
        self.coppers = coppers
        self.copper_position_slider = copper_position_slider
        self.slider_position_label = slider_position_label
        self.side_layout = side_layout
        self.edit_history = edit_history
        self.status_label = status_label

        # Llama al método para inicializar la interfaz gráfica
        self.init_ui_elements()

    def init_ui_elements(self):
        self.copper_palette_info_label = QLabel()  # Inicializar aquí para evitar el AttributeError

    def apply_copper_effect(self, current_palette):
        position = self.copper_position_slider.value()

        for i, image_line in enumerate(self.image_lines):
            copper_instance = self.get_copper_instance_at_position(i)

            if copper_instance and i >= copper_instance.position:
                image_line.palette_index = copper_instance.palette[i % 16]
            else:
                image_line.palette_index = current_palette[i % 16]

        self.slider_position_label.setText(f"Posición Y del Slider: {position}")
        self.status_label.setText("Efecto Copper: Activado")
        self.show_copper_palettes()

    def show_copper_palettes(self):
        self.copper_palette_info_label.setText("Instancias de Copper:\n")
        for copper_instance in self.coppers:
            self.copper_palette_info_label.setText(
                f"{self.copper_palette_info_label.text()}\nPosición: {copper_instance.position}, "
                f"Colores: {copper_instance.palette}"
            )

    def get_copper_instance_at_position(self, position):
        for copper_instance in self.coppers:
            if copper_instance.position == position:
                return copper_instance
        return None

    def add_copper_instance(self):
        position = self.copper_position_slider.value()
        
        # Evitar añadir Copper en la línea cero
        if position == 0:
            self.show_warning_dialog("No se permite añadir una instancia de Copper en la línea cero.")
            return

        print(f"Añadiendo instancia de Copper en posición: {position}")

        palette = self.get_palette_at_position(position)
        new_copper = Copper(position, palette)
        self.coppers.append(new_copper)

        self.show_copper_palettes()
        self.edit_history.append(f"Añadir instancia de Copper en posición {position}")
        print(f"Instancia de Copper añadida: {new_copper}")

    def show_warning_dialog(self, message):
        warning_dialog = QMessageBox()
        warning_dialog.setIcon(QMessageBox.Warning)
        warning_dialog.setText(message)
        warning_dialog.setWindowTitle("Aviso")
        warning_dialog.exec_()

    def get_palette_at_position(self, position):
        palette = []
        for i in range(16):
            palette.append(self.image_lines[position].palette_index)
        return palette