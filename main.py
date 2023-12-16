from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QIcon
import sys
from image_editor_widget import ImageEditorWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Open a file dialog to select an image
    file_dialog = QFileDialog()
    image_path, _ = file_dialog.getOpenFileName(None, "Select Image", "", "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)")

    if not image_path:
        sys.exit()

    # Create and show the main application window
    window = QMainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle("Sega Genesis Copper Colorized Editor")

    # Set a custom icon for the window
    #icon_path = "icono.png"  # Cambia la ruta según sea necesario
    #window.setWindowIcon(QIcon(icon_path))

    window.showMaximized()  # Show maximized

    # Create and set the central widget as the ImageEditorWidget
    image_editor = ImageEditorWidget(image_path)
    window.setCentralWidget(image_editor)

    sys.exit(app.exec_())
