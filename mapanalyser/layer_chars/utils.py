"""
    Helper methods for the algorithm characteristics of the layer
"""
from math import sqrt, fabs
from numbers import Number
from ..utils import raise_exception


def distance(pointA, pointB):
    """
    Returns the distance between two points

    :param pointA: first point
    :param pointB: second point
    """

    return sqrt((pointA[0] - pointB[0]) ** 2 + (pointA[1] - pointB[1]) ** 2)


def area(pointA, pointB, pointC):
    """
    Returns the area of the triangle

    :param pointA: first point
    :param pointB: second point
    :param pointC: third point
    """

    a = distance(pointA, pointB)
    b = distance(pointB, pointC)
    c = distance(pointA, pointC)
    pr = (a + b + c) / 2
    epsilon = 0.001

    if (fabs(pr - a) < epsilon or
        fabs(pr - b) < epsilon or
        fabs(pr - c) < epsilon):
        return 0

    return sqrt(pr * (pr - a) * (pr - b) * (pr - c))


def orientation(pointA, pointB, pointC):
    """
    Computes the orientation of three-point bend

    :param pointA: first point
    :param pointB: second point
    :param pointC: third point
    """

    direction = ((pointB[0] - pointA[0]) * (pointC[1] - pointA[1]) -
                (pointC[0] - pointA[0]) * (pointB[1] - pointA[1]))

    return direction >= 0


def bend_area(bend):
    """
    Returns the area of the bend

    :param bend: point representation of a bend
    """

    count = len(bend)

    if count < 3:
        return 0.0

    count = count-1
    result = 0
    i = 0

    while i < count:
        result += (bend[i][0] + bend[i + 1][0]) * (bend[i][1] - bend[i + 1][1])
        i = i + 1

    result += (bend[count ][0] + bend[0][0]) * (bend[count ][1] - bend[0][1])

    return fabs(result / 2)


def bend_length(bend):
    """
    Returns the length of the bend

    :param bend: point representation of a bend
    """

    count = len(bend)

    if count < 3:
        return 0.0

    result = 0.0
    i = 0

    while i < count - 1:
        result += distance(bend[i], bend[i + 1])
        i = i+1

    return result


def base_line_length(bend):
    """
    Returns the length of the baseline

    :param bend: point representation of a bend
    """

    count = len(bend)

    if count < 3:
        return 0

    return sqrt((bend[count - 1][0] - bend[0][0]) ** 2 +
            (bend[count - 1][1] - bend[0][1]) ** 2)


def peak_index(bend):
    """
    Finds the peak of a bend

    :param bend: point representation of a bend
    """

    count = len(bend)

    if count < 3:
        return 0

    begin = bend[0]
    end = bend[count - 1]
    index = 0
    max_sum = 0
    i = 0

    while i < count - 1:
        temp_sum = (sqrt(pow((bend[i][0] - begin[0]), 2) +
                        pow((bend[i][1] - begin[1]), 2)) +
                    sqrt(pow((bend[i][0] - end[0]), 2) +
                        pow((bend[i][1] - end[1]), 2)))
        i = i + 1

        if not temp_sum > max_sum:
            continue

        max_sum = temp_sum
        index = i - 1

    return index


def cos_angle(u, v, w):
    """
    Returns the cosine of the angle between the vectors [u, v] and [v, w]

    :param u: first point
    :param v: second point
    :param w: third point
    """

    cos = ((v[0] - u[0]) * (w[0] - v[0]) + (v[1] - u[1]) * (w[1] - v[1]))
    cos = cos / sqrt((pow(v[0] - u[0], 2) + pow(v[1] - u[1], 2)) *
                    (pow(w[0] - v[0], 2) + pow(w[1] - v[1], 2)))

    return cos


def height(bend):
    """
    Returns the height of the bend

    :param bend: point representation of a bend
    """

    count = len(bend)

    if count < 3:
        return 0

    a = bend[count - 1][1] - bend[0][1]
    b = bend[0][0] - bend[count - 1][0]
    epsilon = 0.001

    if fabs(a) < epsilon and fabs(b) < epsilon:
        if count ==3:
            return 0

        a = bend[count - 2][1] - bend[0][1]
        b = bend[0][0] - bend[count - 2][0]

    c = bend[0][1] * (-1) * b - bend[0][0] * a
    peakIndex = peak_index(bend)

    return fabs(a * bend[peakIndex][0] +
                b * bend[peakIndex][1] + c) / sqrt(a * a + b * b)


def get(line):
    """
    Main method
    Returns the number of points, the number of bends,
    the average area of bends, the average length of baselines,
    the average height of bends, the average length of the bends

    :param line: a feature with a type equal to QgsWkbTypes.LineGeometry
    """

    points_number = len(line)
    epsilon = 0.001

    if points_number == 3 and fabs(line[0][0] - line[2][0]) < epsilon:
        return (points_number, 0, 0.0, 0.0, 0.0, 0.0)

    bend_number = 0
    ave_bend_length = 0.0
    ave_bend_base_line_length = 0.0
    ave_bend_height = 0.0
    ave_bend_area = 0.0
    i = 0

    while i < points_number - 2:
        bend =[]
        bend_orient = orientation(line[i], line[i + 1], line[i + 2])
        bend.append(line[i])
        bend.append(line[i + 1])
        bend.append(line[i + 2])
        index = i + 3

        while index < points_number:
            count = len(bend)
            p1 = line[index]
            orient = orientation(bend[count - 2],bend[count - 1], p1)

            if orient != bend_orient:
                break

            bend.append(p1)
            index += 1

        index -= 1

        while index < points_number - 1 :
            if (cos_angle(line[index - 1], line[index], line[index + 1]) > 0.9 and
                    pow(base_line_length(bend), 2) < pow(line[i][0] - line[index + 1][0], 2) +
                        pow(line[i][1] - line[index + 1][1], 2)):
                index += 1
                bend.append(line[index])
            else:
                break

        index -= 1
        i = index
        bend_number += 1
        ave_bend_length += bend_length(bend)
        ave_bend_base_line_length += base_line_length(bend)
        ave_bend_height += height(bend)
        ave_bend_area += bend_area(bend)
        bend.clear()

    if bend_number > 0 :
        return (
            points_number,
            bend_number,
            round(ave_bend_area),
            round(ave_bend_base_line_length),
            round(ave_bend_height),
            round(ave_bend_length)
            )

    return (points_number, 0, 0.0, 0.0, 0.0, 0.0)


def get_formatted_ratios_result(pair):
    """
    This method builds a formatted string of a pair of ratios

    :param pair: Pair of ratios
    """

    if not pair:
        raise_exception("pair is empty")

    first_ratio = '0' if pair[0] == 0.000 else "%.3f" % pair[0]
    second_ratio = '0' if pair[1] == 0.000 else "%.3f" % pair[1]

    return f"{first_ratio}, {second_ratio}"


def get_formatted_result(number):
    """
    Rounds to three decimal places

    :param number: number
    """

    if not isinstance(number, Number):
        raise_exception('number is not Number')

    return round(number, 3)


def update_unique_values(feature, indexes, unique_values_per_field):
    """
    This method updates unique values for feature per fields

    :param feature: the feature of the layer
    :param indexes: field indexes
    :param unique_values_per_field: dictionary of sets with unique values
    """

    if not feature:
        raise_exception('feature is empty')

    if not indexes:
        raise_exception('indexes is empty')

    if not unique_values_per_field:
        raise_exception('unique_values_per_field is empty')

    attributes = feature.attributes()

    for index in indexes:
        unique_values_per_field[index].add(attributes[index])


def get_unique_values_ratio(unique_values_per_field, feature_count):
    """
    This method calculates the ratio of unique values

    :param unique_values_per_field: dictionary of sets with unique values
    :param feature_count: the number of features in the layer
    """

    unique_values_ratio = 0.0

    if feature_count:
        for value in unique_values_per_field.values():
            unique_values_ratio += len(value)

        unique_values_ratio = round(unique_values_ratio / feature_count, 3)

    return unique_values_ratio


def get_ave_unique_values_ratio(unique_values_ratio, fields_count):
    """
    This method calculates the ave ratio of unique values

    :param unique_values_ratio: the ratio of unique values
    :param fields_count: the number of fields in the layer data provider
    """

    unique_values_ratio_by_fields_count = 0.0

    if fields_count:
        unique_values_ratio_by_fields_count = round(unique_values_ratio / fields_count, 3)

    return unique_values_ratio_by_fields_count
