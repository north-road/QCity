# -----------------------------------------------------------
# Copyright (C) 2024 XX XX
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------
import math
import os
import statistics
from typing import List, Union, Tuple, Optional

from qgis.PyQt import sip
from qgis.PyQt.QtWidgets import QDockWidget, QDialog
from qgis.PyQt.QtCore import Qt, QEvent, QSize
from qgis.PyQt.QtGui import QColor, QCursor, QPixmap, QPainter, QFont, QIcon

from qgis.core import (
    QgsProject,
    QgsDistanceArea,
    QgsWkbTypes,
    QgsGeometry,
    QgsVectorLayer,
    QgsPoint,
    QgsPointXY,
    QgsRasterLayer,
    QgsUnitTypes,
    Qgis,
    QgsFeatureRequest,
)

from qgis.gui import (
    QgsMapToolDigitizeFeature,
    QgsMapCanvas,
    QgsAdvancedDigitizingDockWidget,
    QgsMessageBar,
    QgsMapToolCapture,
    QgsRubberBand,
    QgsMapTool,
    QgisInterface,
    QgsAbstractMapToolHandler,
    QgsSnapIndicator,
    QgsMapToolCaptureLayerGeometry,
    QgsMapMouseEvent,
)

from ..gui.widget import SlopeDigitizingConfigWidget
from ..core import SETTINGS_MANAGER, Utils


class DrawLineTool(QgsMapToolDigitizeFeature):
    """
    A map tool for drawing lines
    """

    def __init__(
        self,
        map_canvas: QgsMapCanvas,
        cad_dock_widget: QgsAdvancedDigitizingDockWidget,
        message_bar: QgsMessageBar,
        dlg_live_display: QDockWidget,
        dlg_config: SlopeDigitizingConfigWidget,
        iface: QgisInterface,
    ) -> None:
        super().__init__(map_canvas, cad_dock_widget, QgsMapToolCapture.CaptureLine)
        self.iface = iface
        self.unit = None
        self.cursor_band: Optional[QgsRubberBand] = None
        self.round_value: int = 2
        self.message_bar: QgsMessageBar = message_bar
        self.rubber_bands: List[QgsRubberBand] = list()
        self.last_click_raster_value: Optional[float] = None
        self.last_map_point: Optional[QgsPointXY] = None
        self.move_map_point: Optional[QgsPointXY] = None
        self.points: List[QgsPointXY] = []
        self.project_instance: QgsProject = QgsProject.instance()
        self.map_canvas: QgsMapCanvas = map_canvas
        self.last_maptool: QgsMapTool = self.canvas().mapTool()
        self.layer: QgsVectorLayer = self.iface.activeLayer()
        self.dlg_live_display: QDialog = dlg_live_display
        self.dlg_config: SlopeDigitizingConfigWidget = dlg_config
        self.settings_section = "slopeDigitizer"
        self.project = QgsProject.instance()
        # slopes, always in percent
        self.slopes_in_percent: List[float] = list()
        self.snap_indicator = QgsSnapIndicator(map_canvas)

        self._distance_units: Qgis.DistanceUnit = SETTINGS_MANAGER.get_distance_unit()

        SETTINGS_MANAGER.distance_unit_changed.connect(self.updateDistanceUnits)
        SETTINGS_MANAGER.slope_type_changed.connect(self.updateSlopeUnits)
        if hasattr(self.iface, "layerTreeView"):
            self.iface.layerTreeView().currentLayerChanged.connect(self.update_layer)

    def activate(self):
        # skip QgsMapToolDigitizeFeature method -- it has odd logic
        # about storing/restoring active layer for canvas which messes
        # things up
        QgsMapToolCaptureLayerGeometry.activate(self)

    def deactivate(self):
        # skip QgsMapToolDigitizeFeature method -- it has odd logic
        # about storing/restoring active layer for canvas which messes
        # things up
        QgsMapToolCaptureLayerGeometry.deactivate(self)


class MapToolHandler(QgsAbstractMapToolHandler):
    def __init__(self, tool, action):
        super().__init__(tool, action)

    def isCompatibleWithLayer(
        self, layer: Union[QgsVectorLayer, QgsRasterLayer], context
    ) -> None:
        # this tool can only be activated when an editable vector layer is selected
        return (
            isinstance(layer, QgsVectorLayer)
            and layer.isEditable()
            and layer.geometryType() == Qgis.GeometryType.Line
        )
