"""
    Utils
"""
import os
import csv
import importlib.util
from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsMessageLog, Qgis, QgsProcessingException


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