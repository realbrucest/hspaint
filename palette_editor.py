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
        palette = list(self.image_lines[0].image.getpalette())  # Convertir a lista para acceder por índice

        # Asegurarse de que el índice no sea mayor que la longitud de la paleta
        index %= len(palette) // 3

        color_start = index * 3
        color_end = (index + 1) * 3
        color = tuple(palette[color_start:color_end])
        return color
