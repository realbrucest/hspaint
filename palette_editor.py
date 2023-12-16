from image_line import ImageLine
class PaletteEditor:
    def __init__(self, image_lines):
        self.image_lines = image_lines
        self.edit_history = []

    def get_palettes_array(self):
        palettes_array = []
        
        for i in range(self.image_lines[0].image.height):
            line_image = self.image_lines[0].image.crop((0, i, self.image_lines[0].image.width, i + 1))
            palette_index = i % 16
            self.image_lines.append(ImageLine(line_image, palette_index))

        for image_line in self.image_lines:
            palette_index = image_line.palette_index
            color = self.get_palette_color(palette_index)
            palettes_array.append(color)

        return palettes_array

    def change_palette_color_at_index(self, index, new_color):
        for image_line in self.image_lines:
            palette = list(image_line.image.getpalette())  # Convertir a lista para modificar
            palette[index * 3: (index + 1) * 3] = new_color
            image_line.image.putpalette(palette)

    def get_palette_color(self, index):
        palette_size = len(self.image_lines[0].image.getpalette())
        # Asegurarse de que el índice no sea mayor que la longitud de la paleta
        if palette_size > 0:
            index %= palette_size // 3

        color_start = index * 3
        color_end = (index + 1) * 3
        palette = list(self.image_lines[0].image.getpalette())
        color = tuple(palette[color_start:color_end])
        return color

    @staticmethod
    def load_palette_from_file(file_path):
        with open(file_path, 'r') as file:
            # Lee las líneas del archivo
            lines = file.readlines()

            # Verifica si el formato es válido
            if len(lines) < 3 or lines[0].strip() != 'JASC-PAL' or lines[1].strip() != '0100':
                raise ValueError('Formato de archivo de paleta no válido.')

            # Extrae el número de colores de la paleta
            num_colors = int(lines[2].strip())

            # Verifica si el número de colores es válido
            if num_colors != 16:
                raise ValueError('El número de colores en la paleta debe ser 16.')

            # Extrae los colores de la paleta y crea una lista de tuplas
            palette_colors = [tuple(map(int, line.split())) for line in lines[3:]]

            return palette_colors
