"""
    Utils
"""
import os
import csv
import importlib.util
import processing

from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsMessageLog, Qgis, QgsProcessingException, QgsWkbTypes


def tr(string):
    return QCoreApplication.translate('Processing', string)


def raise_exception(message):
    raise QgsProcessingException(tr(message))


def write_to_file(path, header, rows, delimiter):
    """
    This method writes the result to a file

    :param path: Path to file
    :param header: Header of the csv file
    :param row: Csv rows
    :param delimiter: Csv delimiter
    """

    if not path:
        raise_exception('output path is empty')
    if not header:
        raise_exception('header is empty')
    if not rows:
        raise_exception('rows is empty')
    if not delimiter:
        raise_exception('delimiter is empty')

    file_exists = os.path.isfile(path)

    try:
        output_file = open(path, 'a', newline='')
        cout = csv.DictWriter(output_file, header, delimiter = delimiter)

        if not file_exists:
            cout.writeheader()

        cout.writerows(rows)
        output_file.close()
    except Exception:
        raise_exception('error while writing to file')


def define_help_info(file_name):
    """
    Sets the help text.

    :help_file: File name
    """

    try:
        with open(file_name, 'r') as f:
            return f.read()
    except Exception:
        return ''


def check(req_path, readme_path):
    '''
    this function checks whether packages are installed in Python

    :param req_path: Path to the requirements file
    '''

    packages = []

    try:
        with open(req_path, 'r') as f:
            packages = [line.strip() for line in f]
    except Exception:
        QgsMessageLog.logMessage(
            "Problem while reading requirements.txt",
            level=Qgis.Warning)

    not_installed_packages = [
        package_name for package_name in packages
        if not importlib.util.find_spec(package_name)
        ]
    message = f"Some packages are not installed ({','.join(not_installed_packages)}). "

    if not_installed_packages:
        message += f'Read the package installation instructions file - "{readme_path}"'
        raise ImportError(message)


def get_total_intersection(layer, feedback):
    """
    This method calculates the number of line intersections

    :param layer: Vector layer
    :param feedback: Feedback from a processing algorithm
    """

    if not layer:
        raise_exception('layer is empty')
    if not feedback:
        raise_exception('feedback is empty')
    if layer.geometryType() != QgsWkbTypes.LineGeometry:
        raise_exception('layer geometry is not line geometry')

    feedback.pushInfo(tr('Receiving endpoints of the lines'))

    end_points = {}

    for feature in layer.getFeatures():
        geom = feature.geometry()

        for part in geom.parts():
            verts = list(part.vertices())
            start_v = verts[0]
            start_v_cortege = (start_v.x(), start_v.y())

            if start_v_cortege in end_points:
                end_points[start_v_cortege] += 1
            else:
                end_points[start_v_cortege] = 1

            end_v = verts[-1]
            end_v_cortege = (end_v.x(), end_v.y())

            if end_v_cortege in end_points:
                end_points[end_v_cortege] += 1
            else:
                end_points[end_v_cortege] = 1

    feedback.pushInfo(tr('Getting intersection points (this can take a long time (the more lines, the more time))'))

    intersections_proc_params = {
        'INPUT': layer,
        'INTERSECT': layer,
        'OUTPUT': 'memory:'
        }
    result = processing.run(
        'qgis:lineintersections',
        intersections_proc_params
        )
    intersections_layer = result['OUTPUT']

    set_of_intersections = set((f.geometry().asPoint().x(), f.geometry().asPoint().y()) for f in intersections_layer.getFeatures())

    feedback.pushInfo(tr('Getting true intersection points'))

    intersections = get_true_intersections(set_of_intersections, end_points) if set_of_intersections else []

    return intersections


def get_true_intersections(intersections, end_points):
    """
    This method calculates true line intersections

    :param intersections: Total set of intersections
    :param end_points: End points of lines
    """

    if not intersections:
        raise_exception('intersections is empty')
    if not end_points:
        raise_exception('end_points is empty')

    true_intersections = set()

    for point_cortege in intersections:
        if point_cortege in end_points:
            if end_points[point_cortege] != 2:
                true_intersections.add(point_cortege)
        else:
            true_intersections.add(point_cortege)

    return true_intersections

def merge_layers(layers):
    """
    This method merges layers

    :param layers: Vector layers
    """

    if not layers:
        raise_exception('layers is empty')

    merge_proc_params = {
        'LAYERS': layers,
        'OUTPUT': 'memory:'
        }

    result = processing.run('qgis:mergevectorlayers', merge_proc_params, None)
    merged_layers_map = result['OUTPUT']

    return merged_layers_map


def filter_layers(layers):
    """
    Converts a polygon geometry layers in the line geometry layers

    :param layers: Vector layers
    """
    filtered_layers = []

    for layer in layers:
        if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            name = layer.name()
            line_layer = processing.run("native:polygonstolines", {'INPUT': layer, 'OUTPUT':'TEMPORARY_OUTPUT'})["OUTPUT"]
            line_layer.setName(name)
            filtered_layers.append(line_layer)
        elif layer.geometryType() == QgsWkbTypes.LineGeometry:
            filtered_layers.append(layer)

    return filtered_layers
