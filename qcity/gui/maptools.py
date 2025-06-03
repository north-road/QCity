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
from typing import List, Union, Optional

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.core import (
    NULL,
    QgsGeometry,
    QgsVectorLayer,
    QgsPointXY,
    QgsRasterLayer,
    Qgis,
    QgsWkbTypes,
)
from qgis.gui import (
    QgsMapToolDigitizeFeature,
    QgsMapCanvas,
    QgsAdvancedDigitizingDockWidget,
    QgsMapToolCapture,
    QgsRubberBand,
    QgsAbstractMapToolHandler,
    QgsMapToolCaptureLayerGeometry,
    QgsMapMouseEvent,
    QgsSnapIndicator,
)

from qcity.core import LayerType, PROJECT_CONTROLLER, DatabaseUtils


class DrawPolygonToolOld(QgsMapToolDigitizeFeature):
    """
    A map tool for drawing polygons, for use with QGIS < 3.44.

    Does NOT support CAD digitizing dock, as we need https://github.com/qgis/QGIS/pull/62097 for that

    Remove when we can run on 3.44+ only.
    """

    def __init__(
            self,
            map_canvas: QgsMapCanvas,
            cad_dock_widget: QgsAdvancedDigitizingDockWidget
    ) -> None:
        super().__init__(map_canvas, cad_dock_widget, QgsMapToolCapture.CaptureLine)
        self.default_color: QColor = QColor(255, 0, 0, 100)
        self.cursor_band: Optional[QgsRubberBand] = None
        self.points: List[QgsPointXY] = []
        self.layer: QgsVectorLayer = QgsVectorLayer(
            "Polygon?crs=EPSG:4326", "memory_polygon_layer", "memory"
        )
        self.rubber_band = QgsRubberBand(
            mapCanvas=self.canvas(),
            geometryType=QgsWkbTypes.GeometryType.PolygonGeometry,
        )
        self.snap_indicator = QgsSnapIndicator(map_canvas)
        self._layer_type = LayerType.ProjectAreas
        self._parent_pk = NULL

    def add_feature(self, layer_type: LayerType, parent_pk):
        self._layer_type = layer_type
        self._parent_pk = parent_pk
        self.canvas().setMapTool(self)

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
        self.cursor_band = QgsRubberBand(self.canvas(), QgsWkbTypes.PolygonGeometry)
        self.cursor_band.setColor(self.default_color)
        self.cursor_band.setLineStyle(Qt.DotLine)

        if self.points:
            for p in [self.points[0], self.points[-1], cursor_point]:
                p_map = self.toMapCoordinates(self.layer, p)
                self.cursor_band.addPoint(p_map)

    def createRubberBand(self):
        """Builds rubber band from all points and adds it to the map canvas."""
        self.rubber_band = QgsRubberBand(self.canvas(), QgsWkbTypes.PolygonGeometry)
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


class DrawPolygonTool(QgsMapToolCaptureLayerGeometry):
    """
    A map tool for drawing polygons, for use with QGIS 3.44+

    Does support CAD digitizing dock.
    """

    def __init__(
            self,
            map_canvas: QgsMapCanvas,
            cad_dock_widget: QgsAdvancedDigitizingDockWidget
    ) -> None:
        super().__init__(map_canvas, cad_dock_widget, QgsMapToolCapture.CapturePolygon)
        self.points: List[QgsPointXY] = []
        self._temp_layer: QgsVectorLayer = QgsVectorLayer(
            "Polygon?crs=EPSG:4326", "memory_polygon_layer", "memory"
        )
        self._layer_type = LayerType.ProjectAreas
        self._parent_pk = NULL

    def layer(self):
        return self._temp_layer

    def add_feature(self, layer_type: LayerType, parent_pk):
        self._layer_type = layer_type
        self._parent_pk = parent_pk
        self.canvas().setMapTool(self)

    def layerGeometryCaptured(self, polygon: QgsGeometry) -> None:
        if polygon.constGet().exteriorRing().numPoints() < 3:
            return

        feature_name, ok = QInputDialog.getText(
            self.canvas(), self.tr("Create {}").format(self._layer_type.as_title_case(plural=False)),
            self.tr("Input {} name").format(self._layer_type.as_sentence_case(plural=False)))

        if not ok:
            return

        self.create_feature(
            feature_name, polygon
        )

    def create_feature(self, feature_name: str, polygon: QgsGeometry) -> None:
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
            return

        if not layer.isValid():
            raise Exception("Layer is not valid!")

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
