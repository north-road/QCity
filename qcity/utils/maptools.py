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
import os
from typing import List, Union, Optional

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.core import (
    NULL,
    QgsProject,
    QgsGeometry,
    QgsVectorLayer,
    QgsPointXY,
    QgsRasterLayer,
    Qgis,
    QgsWkbTypes,
    QgsVectorLayerUtils
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
    QgsMapToolCaptureLayerGeometry,
    QgsMapMouseEvent,
    QgsSnapIndicator,
)

from ..core import LayerType, PROJECT_CONTROLLER, DatabaseUtils
from ..gui.qcity_dock import QCityDockWidget


class DrawPolygonTool(QgsMapToolDigitizeFeature):
    """
    A map tool for drawing polygons
    """

    def __init__(
            self,
            map_canvas: QgsMapCanvas,
            cad_dock_widget: QgsAdvancedDigitizingDockWidget,
            message_bar: QgsMessageBar,
            dlg: QCityDockWidget,
            iface: QgisInterface,
    ) -> None:
        super().__init__(map_canvas, cad_dock_widget, QgsMapToolCapture.CaptureLine)
        self.default_color: QColor = QColor(255, 0, 0, 100)
        self.cursor_band: Optional[QgsRubberBand] = None
        self.iface = iface
        self.dlg = dlg
        self.unit = None
        self.cursor_band: Optional[QgsRubberBand] = None
        self.message_bar: QgsMessageBar = message_bar
        self.rubber_bands: List[QgsRubberBand] = list()
        self.last_click_raster_value: Optional[float] = None
        self.last_map_point: Optional[QgsPointXY] = None
        self.move_map_point: Optional[QgsPointXY] = None
        self.points: List[QgsPointXY] = []
        self.project_instance: QgsProject = QgsProject.instance()
        self.map_canvas: QgsMapCanvas = map_canvas
        self.last_maptool: QgsMapTool = self.map_canvas.mapTool()
        self.layer: QgsVectorLayer = QgsVectorLayer(
            "Polygon?crs=EPSG:4326", "memory_polygon_layer", "memory"
        )
        self.project = QgsProject.instance()
        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self._default_project_area_parameters_path = os.path.join(
            self.plugin_path, "..", "data", "default_project_area_parameters.json"
        )
        self._default_development_site_parameters_path = os.path.join(
            self.plugin_path, "..", "data", "default_development_site_parameters.json"
        )
        self.rubber_band = QgsRubberBand(
            mapCanvas=self.map_canvas,
            geometryType=QgsWkbTypes.GeometryType.PolygonGeometry,
        )
        self.snap_indicator = QgsSnapIndicator(map_canvas)
        self._layer_type = LayerType.ProjectAreas
        self._parent_pk = NULL

    def add_feature(self, layer_type: LayerType, parent_pk):
        self._layer_type = layer_type
        self._parent_pk = parent_pk
        self.map_canvas.setMapTool(self)

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

    def createCursorBand(self, cursor_point: QgsPointXY) -> None:
        """Creates the moving dotted line rubber band."""
        if self.cursor_band:
            self.canvas().scene().removeItem(self.cursor_band)
        self.cursor_band = QgsRubberBand(self.map_canvas, QgsWkbTypes.PolygonGeometry)
        self.cursor_band.setColor(self.default_color)
        self.cursor_band.setLineStyle(Qt.DotLine)

        if self.points:
            for p in [self.points[0], self.points[-1], cursor_point]:
                p_map = self.toMapCoordinates(self.layer, p)
                self.cursor_band.addPoint(p_map)

    def createRubberBand(self):
        """Builds rubber band from all points and adds it to the map canvas."""
        self.rubber_band = QgsRubberBand(self.map_canvas, QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setColor(self.default_color)

        for point in self.points:
            point_m = self.toMapCoordinates(self.layer, point)
            if point == self.points[-1]:
                self.rubber_band.addPoint(point_m, True)
            self.rubber_band.addPoint(point_m, False)
        self.rubber_band.show()

    def canvasMoveEvent(self, event: QgsMapMouseEvent) -> None:
        move_map_point = event.snapPoint()
        self.snap_indicator.setMatch(event.mapPointMatch())
        self.createCursorBand(move_map_point)

    def canvasReleaseEvent(self, event: QgsMapMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            map_point = event.snapPoint()
            v_point = self.toLayerCoordinates(self.layer, map_point)
            self.points.append(v_point)
            if self.rubber_band:
                self.canvas().scene().removeItem(self.rubber_band)
            self.createRubberBand()

        if event.button() == Qt.RightButton:
            if len(self.points) < 3:
                self.cleanup()
                return

            feature_name, ok = QInputDialog.getText(
                self.canvas(), self.tr("Create {}").format(self._layer_type.as_title_case(plural=False)),
                self.tr("Input {} name").format(self._layer_type.as_sentence_case(plural=False)))

            if not ok:
                self.cleanup()
                return

            if self.rubber_band:
                self.clearRubberBands()

            self.create_feature(
                feature_name
            )

            self.cleanup()

    def create_feature(self, feature_name: str) -> None:
        """
        Called when the new feature should be created
        """
        layer = PROJECT_CONTROLLER.get_layer(self._layer_type)

        existing_names = PROJECT_CONTROLLER.get_unique_names(self._layer_type)
        feature_name_exists = feature_name in existing_names

        if not feature_name or feature_name_exists:
            if feature_name_exists:
                # TODO: Message bar here instead.
                print("Table name already exists.")
            self.cleanup()
            return

        if not layer.isValid():
            raise Exception("Layer is not valid!")

        polygon = QgsGeometry.fromPolygonXY(
            [[QgsPointXY(x, y) for x, y in self.points]]
        )
        initial_attributes = {}
        foreign_key = DatabaseUtils.foreign_key_for_layer(self._layer_type)
        if foreign_key:
            initial_attributes[foreign_key] = self._parent_pk
        if self._layer_type == LayerType.BuildingLevels:
            initial_attributes["level_index"] = PROJECT_CONTROLLER.get_next_building_level(
                self._parent_pk)
            initial_attributes["base_height"] = PROJECT_CONTROLLER.get_floor_base_height(
                self._parent_pk, initial_attributes["level_index"])

        feature = PROJECT_CONTROLLER.create_feature(self._layer_type,
                                                    feature_name,
                                                    polygon,
                                                    initial_attributes)

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()

    def cleanup(self):
        """Run after digitization is finished, cleans up the maptool"""
        self.clearRubberBands()
        self.layer = QgsVectorLayer(
            "Polygon?crs=EPSG:4326", "memory_polygon_layer", "memory"
        )
        self.points = list()

    def clearRubberBands(self) -> None:
        """Clears map canvas of all rubber bands and sets them to None."""
        if self.rubber_band:
            self.canvas().scene().removeItem(self.rubber_band)
        self.rubber_band = None
        if self.cursor_band:
            self.canvas().scene().removeItem(self.cursor_band)
        self.cursor_band = None


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
                and layer.geometryType() == Qgis.GeometryType.Polygon
        )
