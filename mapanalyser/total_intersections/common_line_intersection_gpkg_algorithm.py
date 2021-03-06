# -*- coding: utf-8 -*-

"""
/***************************************************************************
 CommonIntersection
                                 A QGIS plugin
 This plugin computes Total number of intersections of linear and polygon layers
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-08-30
        copyright            : (C) 2020 by Potemkin D.A., Yakimova O.P.
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

__author__ = 'Potemkin D.A., Yakimova O.P.'
__date__ = '2020-08-30'
__copyright__ = '(C) 2020 by Potemkin D.A., Yakimova O.P., Samsono T.E.'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import processing

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsVectorLayer,
                       QgsVectorDataProvider,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFileDestination,
                       QgsWkbTypes,
                       QgsProcessingException,
                       QgsGeometry,
                       QgsFeature,
                       QgsPointXY,
                       QgsFields)

from ..utils import tr, raise_exception, write_to_file, define_help_info, filter_layers, get_total_intersection, merge_layers


class CommonIntersectionAlgorithmGpkg(QgsProcessingAlgorithm):
    """
    This is a class that calculates the total number of
    intersections of linear and polygon layers
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    HELP_FILE = 'total_intersections_help.txt'


    def __init__(self):
        super().__init__()
        directory = os.path.dirname(__file__)
        file_name = os.path.join(directory, self.HELP_FILE)
        self._shortHelp = define_help_info(file_name)


    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                tr('Input workspace')
            )
        )

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

        geopackage = self.parameterAsFile(parameters, self.INPUT, context)
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        dummy = QgsVectorLayer(geopackage, "dummy", "ogr")
        sublyrs = dummy.dataProvider().subLayers()

        all_layers = []
        for sublyr in sublyrs:
            name = sublyr.split('!!::!!')[1]
            uri = "%s|layername=%s" % (geopackage, name)
            layer = QgsVectorLayer(uri, name, "ogr")
            all_layers.append(layer)


        layers = filter_layers(all_layers)
        result = {
            'Layers': 'missing layers with the right geometry',
            'The number of intersections': 0
            }

        if not layers:
            return result

        feedback.setProgress(10)
        feedback.pushInfo(tr('Merging layers'))
        merged_layer = merge_layers(layers)
        feedback.setProgress(20)

        intersections = get_total_intersection(merged_layer, feedback)
        feedback.setProgress(90)

        # (sink, dest_id) = self.parameterAsSink(
        #     parameters, self.OUTPUT,
        #     context, QgsFields(),
        #     QgsWkbTypes.Point,
        #     merged_layer.sourceCrs()
        # )
        #
        # feedback.pushInfo('Creating a layer')
        #
        # for point in intersections:
        #     if feedback.isCanceled():
        #         break
        #
        #     feature = QgsFeature()
        #     feature.setGeometry(QgsGeometry().fromPointXY(QgsPointXY(point[0], point[1])))
        #     sink.addFeature(feature, QgsFeatureSink.FastInsert)

        header = [
            'workspace',
            'total_intersections',
        ]
        row = [{
            header[0]: os.path.basename(os.path.normpath(geopackage)),
            header[1]: len(intersections),
        }]

        if output:
            feedback.pushInfo(tr('Writing to file'))
            write_to_file(output, header, row, ';')

        result['Layers'] = ' '.join([layer.name() for layer in layers])
        result['The number of intersections'] = len(intersections)
        feedback.setProgress(100)

        return result


    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Compute workspace total number of intersections of linear and polygon layers'


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
        return CommonIntersectionAlgorithmGpkg()
