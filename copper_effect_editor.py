from PyQt5.QtWidgets import QLabel, QMessageBox, QListWidget, QListWidgetItem, QPushButton
from new_copper_dialog import NewCopperDialog

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
        # Agregar un QListWidget para mostrar los coppers en el panel lateral
        self.copper_list_widget = QListWidget()
        self.side_layout.addWidget(self.copper_list_widget)

        # Botones para agregar y eliminar coppers
        add_copper_button = QPushButton("Agregar Copper")
        add_copper_button.clicked.connect(self.add_copper_instance)
        remove_copper_button = QPushButton("Eliminar Copper")
        remove_copper_button.clicked.connect(self.remove_selected_copper)

        self.side_layout.addWidget(add_copper_button)
        self.side_layout.addWidget(remove_copper_button)

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
        self.copper_list_widget.clear()

        for i, copper_instance in enumerate(self.coppers):
            self.copper_palette_info_label.setText(
                f"{self.copper_palette_info_label.text()}\nPosición: {copper_instance.position}, "
                f"Colores: {copper_instance.palette}"
            )

            # Agregar la instancia de Copper al QListWidget
            item = QListWidgetItem(f"Posición: {copper_instance.position}")
            self.copper_list_widget.addItem(item)

    def get_copper_instance_at_position(self, position):
        for copper_instance in self.coppers:
            if copper_instance.position == position:
                return copper_instance
        return None

    def add_copper_instance(self):
        position = self.copper_position_slider.value()

        # Validar la posición
        validation_result = self.is_valid_copper_position(position)
        if not validation_result["is_valid"]:
            error_message = f"Error: La posición del nuevo Copper no es válida.\n{validation_result['reason']}"
            self.show_warning_dialog(error_message)
            return

        new_copper_dialog = NewCopperDialog(self.get_previous_palette(), parent=None)  # Asegúrate de pasar self como el objeto QWidget padre
        result = new_copper_dialog.exec_()

        if result == NewCopperDialog.Accepted:
            # Aquí accedemos a la paleta_text seleccionada en el diálogo
            palette_text = new_copper_dialog.palette_text

            # Puedes procesar la palette_text según tus necesidades
            print(f"Nueva paleta seleccionada: {palette_text}")

    def get_previous_palette(self):
        return self.coppers[-1].palette

    def is_valid_copper_position(self, new_position):
        min_line_distance = 8  # Separación mínima de 8 líneas

        # Verificar que no sea la línea cero o inferior a ocho
        if new_position <= 8:
            return {"is_valid": False, "reason": "La posición debe ser mayor que 8."}

        # Verificar la separación mínima
        for copper_instance in self.coppers:
            if abs(new_position - copper_instance.position) < min_line_distance:
                return {"is_valid": False, "reason": "La separación entre coppers debe ser de al menos 8 líneas."}

        return {"is_valid": True, "reason": ""}

    def show_warning_dialog(self, message):
        warning_dialog = QMessageBox()
        warning_dialog.setIcon(QMessageBox.Warning)
        warning_dialog.setText(message)
        warning_dialog.setWindowTitle("Aviso")
        warning_dialog.exec_()

    def show_info_dialog(self, message):
        info_dialog = QMessageBox()
        info_dialog.setIcon(QMessageBox.Information)
        info_dialog.setText(message)
        info_dialog.setWindowTitle("Información")
        info_dialog.exec_()

    def get_palette_at_position(self, position):
        palette = []
        for i in range(16):
            palette.append(self.image_lines[position].palette_index)
        return palette
    
    def remove_selected_copper(self):
        selected_items = self.copper_list_widget.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        position_str = item.text().split(":")[1].strip()
        position = int(position_str)
        
        # Remover el copper correspondiente
        for i, copper_instance in enumerate(self.coppers):
            if copper_instance.position == position:
                del self.coppers[i]
                break

        self.show_copper_palettes()
        self.edit_history.append(f"Eliminar instancia de Copper en posición {position}")
        print(f"Instancia de Copper eliminada en posición: {position}")