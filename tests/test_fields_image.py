# coding=utf-8
import solution as f

"""Test calculate_dimensions for n cases:

1) the height and width of the current image is smaller than the desired
dimensions.

2) the height of the current image is smaller than the desired height but the
width larger.

3) The width of the current image is smaller than the desired width but the
height is larger.

4) The width and height of the current image is larger than the desired
 dimensions.  """


def test_calculate_dimensions_case_1():
    current_size = (300, 480)
    desired_size = (600, 800)
    assert None is f.Image.calculate_dimensions(current_size, desired_size)


def test_calculate_dimensions_case_2():
    current_size = (600, 480)
    desired_size = (300, 800)
    assert (150, 0, 300, 480) == f.Image.calculate_dimensions(current_size, desired_size)


def test_calculate_dimensions_case_3():
    current_size = (300, 800)
    desired_size = (600, 480)
    assert (0, 160, 300, 480) == f.Image.calculate_dimensions(current_size, desired_size)


def test_calculate_dimensions_case_4():
    current_size = (600, 800)
    desired_size = (300, 480)
    assert (150, 160, 300, 480) == f.Image.calculate_dimensions(current_size, desired_size)
