# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LayerCharacteristics
                                 A QGIS plugin
 This plugin computes layer characteristics
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-08-21
        copyright            : (C) 2020 by YSU
        email                : daniilpot@yandex.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'YSU'
__date__ = '2020-08-21'
__copyright__ = '(C) 2020 by YSU'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from random import randrange

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsFeatureRequest,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsWkbTypes)
from qgis.utils import iface

from .utils import get, get_formatted_ratios_result, update_unique_values, get_formatted_result, get_unique_values_ratio, get_ave_unique_values_ratio
from ..utils import tr, raise_exception, write_to_file, define_help_info


class LayerCharacteristicsAlgorithm(QgsProcessingAlgorithm):
    """
    This is a class that calculates the topological and
    semantic characteristics of a layer and
    for linear layers:
        the number of bends in the line and the average bend characteristics:
        height, length, area and baseline length
    for polygon layers:
        the total area, total perimeter, average polygon area in the layer and
        average polygon perimeter in the layer
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    EXTENT = 'EXTENT'
    HELP_FILE = 'layer_characteristics_help.txt'

    def __init__(self):
        super().__init__()
        directory = os.path.dirname(__file__)
        file_name = os.path.join(directory, self.HELP_FILE)
        self._shortHelp = define_help_info(file_name)
        self.progress = 0


    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        default_extent = iface.mapCanvas().extent()
        default_extent_value = '{0},{1},{2},{3}'.format(
            default_extent.xMinimum(),
            default_extent.xMaximum(),
            default_extent.yMinimum(),
            default_extent.yMaximum())

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                tr('Input layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                tr('Minimum extent to render'),
                defaultValue=str(default_extent_value)))

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                tr('Output File'),
                'csv(*.csv)',
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        self.progress = 0
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        if not extent:
            raise_exception('can\'t read extent')

        if not layer:
            raise_exception('can\'t get a layer')

        if not output:
            raise_exception('can\'t get an output')

        feedback.pushInfo(tr('The algorithm is running'))
        request = QgsFeatureRequest().setFilterRect(extent)
        features = list(layer.getFeatures(request))
        features_count = len(features)
        fields = layer.dataProvider().fields()
        indexes = [fields.indexFromName(field.name()) for field in fields]

        unique_values_per_field = {key: set() for key in indexes}
        points_num = 0
        total_length = 0
        bend_num = 0
        ave_bend_area = 0.0
        ave_bend_base_line_len = 0.0
        ave_bend_height = 0.0
        ave_bend_length = 0.0
        total_polygon_area = 0.0
        count = 0.0

        total = 100.0 / features_count if features_count > 0 else 0

        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break

            update_unique_values(feature, indexes, unique_values_per_field)
            geom = feature.geometry()
            is_single_type = QgsWkbTypes.isSingleType(geom.wkbType())

            if geom.type() == QgsWkbTypes.LineGeometry:
                total_length += geom.length()

                if is_single_type:
                    data_list = [(v.x(), v.y()) for v in geom.vertices()]

                    if len(data_list) < 3:
                        continue

                    result = get(data_list)
                    count = count + 1
                    points_num += result[0]
                    bend_num += result[1]
                    ave_bend_area += result[2]
                    ave_bend_base_line_len += result[3]
                    ave_bend_height += result[4]
                    ave_bend_length += result[5]
                else:
                    for part in geom.parts():
                        data_list = [(v.x(), v.y()) for v in part.vertices()]

                        if len(data_list) < 3:
                            continue

                        result = get(data_list)
                        count = count + 1
                        points_num += result[0]
                        bend_num += result[1]
                        ave_bend_area += result[2]
                        ave_bend_base_line_len += result[3]
                        ave_bend_height += result[4]
                        ave_bend_length += result[5]
            elif geom.type() == QgsWkbTypes.PolygonGeometry:
                total_length += geom.length()

                if is_single_type:
                    data_list = [(v.x(), v.y()) for v in geom.vertices()]

                    if len(data_list) < 3:
                        continue

                    result = get(data_list)
                    count = count+1
                    points_num += result[0]
                    bend_num += result[1]
                    ave_bend_area += result[2]
                    ave_bend_base_line_len += result[3]
                    ave_bend_height += result[4]
                    ave_bend_length += result[5]
                    total_polygon_area += geom.area()
                else:
                    for part in geom.parts():
                        data_list = [(v.x(), v.y()) for v in part.vertices()]

                        if len(data_list) < 3:
                            continue

                        result = get(data_list)
                        count = count + 1
                        points_num += result[0]
                        bend_num += result[1]
                        ave_bend_area += result[2]
                        ave_bend_base_line_len += result[3]
                        ave_bend_height += result[4]
                        ave_bend_length += result[5]
                    total_polygon_area += geom.area()
            else:
                break

            self.progress = int(current * total)
            feedback.setProgress(self.progress)

        uniq_values_number = get_unique_values_ratio(unique_values_per_field, features_count)
        ave_uniq_values_number = get_ave_unique_values_ratio(uniq_values_number, len(fields))

        header = [
            'layer',
            'field count',
            'features count',
            'uniq values number',
            'ave uniq values',
            'total length',
            'number of points',
            'number of bends',
            'average area of bends',
            'average length of bends baseline',
            'average height of bends',
            'average length of the bends',
            'total polygons area',
            'average polygons area',
            'average length',
        ]
        row = [{
            header[0]: layer.name(),
            header[1]: len(fields),
            header[2]: features_count,
            header[3]: uniq_values_number,
            header[4]: ave_uniq_values_number,
            header[5]: get_formatted_result(total_length),
            header[6]: points_num,
            header[7]: bend_num,
            header[8]: get_formatted_result(ave_bend_area / bend_num) if bend_num > 0 else 0.0,
            header[9]: get_formatted_result(ave_bend_base_line_len / bend_num) if bend_num > 0 else 0.0,
            header[10]: get_formatted_result(ave_bend_height / bend_num) if bend_num > 0 else 0.0,
            header[11]: get_formatted_result(ave_bend_length / bend_num) if bend_num > 0 else 0.0,
            header[12]: get_formatted_result(total_polygon_area),
            header[13]: get_formatted_result(total_polygon_area / count) if count > 0 else 0.0,
            header[14]: get_formatted_result(total_length / count) if count > 0 else 0.0,
        }]

        if output:
            feedback.pushInfo(tr('Writing to file'))
            write_to_file(output, header, row, ';')

        return row[0]


    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Compute layer characteristics'


    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return tr(self.name())


    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return tr(self.groupId())


    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Map characteristics'


    def shortHelpString(self):
        return self._shortHelp


    def createInstance(self):
        return LayerCharacteristicsAlgorithm()
