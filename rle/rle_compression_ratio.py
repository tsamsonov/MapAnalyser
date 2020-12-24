'''
this module provides the ability to calculate
the compression ratio in different ways
'''

import numpy
import cv2
from .rle_compression_ratio_core import compress_ratio, abs_pixel_compare, simple_pixel_compare


def get_ratio_with_simple_comparator(path):
    '''
    this function compute the ratio using simple comparator

    :param path: Path to image
    '''

    matrix, length, channels = get_matrix_data(path)

    return compress_ratio(matrix, length, channels, simple_pixel_compare)


def get_ratio_with_abs_comparator(path):
    '''
    this function compute the ratio using abs comparator

    :param path: Path to image
    '''

    matrix, length, channels = get_matrix_data(path)

    return compress_ratio(matrix, length, channels, abs_pixel_compare)


def get_matrix_data(path):
    '''
    this function returns the modified pixel matrix

    :param path: Path to image
    '''

    stream = open(path, "rb")
    file_bytes = bytearray(stream.read())
    numpyarray = numpy.asarray(file_bytes, dtype=numpy.uint8)
    pixels_matrix = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    rows, cols, channels = pixels_matrix.shape
    new_size = rows * cols
    pixels_matrix.shape = (new_size, channels)

    return pixels_matrix, new_size, channels
