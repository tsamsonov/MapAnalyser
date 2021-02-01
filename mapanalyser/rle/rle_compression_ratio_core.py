from numba import jit

@jit
def compress_ratio(pixels_matrix, matrix_length, channels_number, compare):
    '''
    this function calculates the compression ratio using the RLE algorithm

    :param pixels_matrix: Matrix of pixels
    :param matrix_length: Length of the matrix
    :param channels_number: Number of the pixel channels
    :param compare: Сomparison method
    '''

    compressed_size = 1

    for i in range(1, matrix_length):
        if compare(pixels_matrix[i - 1, 0],
                   pixels_matrix[i - 1, 1],
                   pixels_matrix[i - 1, 2],
                   pixels_matrix[i, 0],
                   pixels_matrix[i, 1],
                   pixels_matrix[i, 2]):
            continue

        compressed_size += 1

    return round((compressed_size * (channels_number + 1)) /
                (matrix_length * channels_number), 3)



@jit
def simple_pixel_compare(pr, pg, pb, r, g, b):
    '''
    this function compares the r, g, b of pixels

    :param pr: Red color value of the previous pixel
    :param pg: Green color value of the previous pixel
    :param pb: Blue color value of the previous pixel
    :param r: Red color value of the current pixel
    :param g: Green color value of the current pixel
    :param b: Blue color value of the current pixel
    '''

    return pr == r and pg == g and pb == b


@jit
def abs_pixel_compare(pr, pg, pb, r, g, b):
    '''
    this function compares r, g, b pixels in the range of two scale values

    :param pr: Red color value of the previous pixel
    :param pg: Green color value of the previous pixel
    :param pb: Blue color value of the previous pixel
    :param r: Red color value of the current pixel
    :param g: Green color value of the current pixel
    :param b: Blue color value of the current pixel
    '''
    
    return abs(pr - r) < 2 and abs(pg - g) < 2 and abs(pb - b) < 2
