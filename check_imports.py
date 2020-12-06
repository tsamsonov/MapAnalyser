'''
check imports script
'''

import importlib.util
from qgis.core import (QgsMessageLog, Qgis)


def check(req_path):
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
        message += 'Read the package installation instructions file - \'readme_imports.txt\''
        raise ImportError(message)
