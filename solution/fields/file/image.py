# coding=utf-8
from math import floor, ceil
from os.path import join

from .file import File
from .helpers import IMAGES


class Image(File):
    """ Similar to a File Field but takes an tuple as size parameter and makes
    sure the image is of that size.
    """

    def __init__(self, base_path='.', size=None, **kwargs):
        self.size = size
        if size:
            self.width = size[0]
            self.height = size[1]
        kwargs.setdefault('allowed', IMAGES)
        super(Image, self).__init__(base_path, **kwargs)

    def clean(self, value):
        """Passes the value to FileField and resizes the image at the path the parent
        returns if needed.

        """
        path = super(Image, self).clean(value)
        if path and self.size:
            self.resize_image(join(self.base_path, path))
        return path

    def resize_image(self, image_path):
        import wand.image

        with wand.image.Image(filename=image_path) as img:
            result = Image.calculate_dimensions(
                img.size, self.size
            )
            if result:
                x, y, width, height = result
                img.crop(x, y, width=width, height=height)
                img.save(filename=image_path)

    @staticmethod
    def calculate_dimensions(image_size, desired_size):
        """Return the Tuple with the arguments to pass to Image.crop.

        If the image is smaller than than the desired_size Don't do
        anything. Otherwise, first calculate the (truncated) center and then
        take half the width and height (truncated again) for x and y.

        x0, y0: the center coordinates
        """

        current_x, current_y = image_size
        target_x, target_y = desired_size

        if current_x < target_x and current_y < target_y:
            return None

        if current_x > target_x:
            new_x0 = floor(current_x / 2)
            new_x = new_x0 - ceil(target_x / 2)
            new_width = target_x
        else:
            new_x = 0
            new_width = current_x

        if current_y > target_y:
            new_y0 = floor(current_y / 2)
            new_y = new_y0 - ceil(target_y / 2)
            new_height = target_y
        else:
            new_y = 0
            new_height = current_y

        return (int(new_x), int(new_y), new_width, new_height)
