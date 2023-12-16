#palette_editor.py

from image_line import ImageLine


class PaletteEditor:
    def __init__(self, image_lines):
        self.image_lines = image_lines
        self.edit_history = []

    def get_palettes_array(self):
        for i in range(self.image_lines[0].image.height):
            line_image = self.image_lines[0].image.crop((0, i, self.image_lines[0].image.width, i + 1))
            palette_index = i % 16
            self.image_lines.append(ImageLine(line_image, palette_index))

        return [self.get_palette_color(image_line.palette_index) for image_line in self.image_lines]

    def change_palette_color_at_index(self, index, new_color):
        for image_line in self.image_lines:
            palette = image_line.image.getpalette()
            palette[index * 3: (index + 1) * 3] = new_color
            image_line.image.putpalette(palette)

    def get_palette_color(self, index):
        palette = self.image_lines[0].image.getpalette()
        color = palette[index * 3: (index + 1) * 3]
        return tuple(color)
