# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Dms2deg
                                 A QGIS plugin
 This plugin converts DMS to degree
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-10-07
        copyright            : (C) 2021 by Ivan Lebedev
        email                : lebedev77@gmail.com
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

__author__ = 'Ivan Lebedev'
__date__ = '2021-11-09'
__copyright__ = '(C) 2021 by Ivan Lebedev'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import (QCoreApplication, QVariant)
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsField,
                       QgsMessageLog,
                       QgsFeature)
from .dms_fun import dms2deg

# Icons
import os
import inspect
from qgis.PyQt.QtGui import QIcon

class Dms2degAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    FIELD1 = 'FIELD1'
    FIELD2 = 'FIELD2'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeMapLayer]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer to deg')
            )
        )

        self.addParameter(QgsProcessingParameterField(self.FIELD1,
                                                      self.tr('DMS attribute to convert to degree'),
                                                      parentLayerParameterName='INPUT',
                                                      type=QgsProcessingParameterField.String
                                                      ))
        self.addParameter(QgsProcessingParameterField(self.FIELD2,
                                                      self.tr('DMS attribute to convert to degree'),
                                                      parentLayerParameterName='INPUT',
                                                      type=QgsProcessingParameterField.String
                                                      ))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Names of source fields
        select_field1 = self.parameterAsString(
            parameters,
            self.FIELD1,
            context)
        select_field2 = self.parameterAsString(
            parameters,
            self.FIELD2,
            context)
        feedback.pushInfo('!!!!!!!!!!!!!!!!hi!!!!!!!!!!!!!!!!!!!')
        # Append a new fields
        new_fields = source.fields()
        if select_field1 != select_field2:
            new_fields.append(QgsField(select_field1 + '_deg', QVariant.Double))
            new_fields.append(QgsField(select_field2 + '_deg', QVariant.Double))
            deg1_id = new_fields.indexOf(select_field1 + '_deg')
            deg2_id = new_fields.indexOf(select_field2 + '_deg')
        elif select_field1 == select_field2:
            new_fields.append(QgsField(select_field1 + '_deg', QVariant.Double))
            deg1_id = new_fields.indexOf(select_field1 + '_deg')
        else:
            return {self.OUTPUT: dest_id}

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            new_fields,
            source.wkbType(),
            source.sourceCrs()
        )
        # Progress bar
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        # PROCESSING
        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            # From module dms_fun
            deg1 = dms2deg(feature[select_field1])
            deg2 = dms2deg(feature[select_field2])
            new_feature = QgsFeature()
            # Set geometry
            new_feature.setGeometry(feature.geometry())
            # Set attributes from sum_unique_values dictionary that we had computed
            new_feature.setFields(new_fields)
            attrib = feature.attributes()
            # Fill new feature attribues from old
            for i, attr in enumerate(attrib):
                new_feature.setAttribute(i, attr)
            # Add compute attributes
            if select_field1 != select_field2:
                new_feature.setAttribute(deg1_id, deg1)
                new_feature.setAttribute(deg2_id, deg2)
            elif select_field1 == select_field2:
                new_feature.setAttribute(deg1_id, deg1)

            # Add a feature in the sink
            sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # Take input layer name    
        source_layer = self.parameterAsLayer(
            parameters,
            self.INPUT,
            context)
        global renamer
        newname = '{}_to_Deg'.format(source_layer.name())
        renamer = Renamer(newname)
        context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(renamer)

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Convert DMS to degree'
    
    def icon(self):
        # Icons
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'deg2dms.png')))
        return icon

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Dms2degAlgorithm()
    
class Renamer (QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()
        
    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)
