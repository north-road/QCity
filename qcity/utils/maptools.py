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
import json
import os
import sqlite3
from typing import List, Union, Optional

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.PyQt.QtCore import Qt

from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsVectorLayer,
    QgsPointXY,
    QgsRasterLayer,
    Qgis,
    QgsFeature,
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
    QgsField,
    QgsFields,
    QgsWkbTypes,
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

from ..core import SETTINGS_MANAGER
from ..gui.widget import TabDockWidget


class DrawPolygonTool(QgsMapToolDigitizeFeature):
    """
    A map tool for drawing polygons
    """

    def __init__(
        self,
        map_canvas: QgsMapCanvas,
        cad_dock_widget: QgsAdvancedDigitizingDockWidget,
        message_bar: QgsMessageBar,
        dlg: TabDockWidget,
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

    def createRubberBand(self, cursor_point: QgsPointXY) -> None:
        """Creates the moving dotted line rubber band."""
        if self.cursor_band:
            self.canvas().scene().removeItem(self.cursor_band)
        self.cursor_band = QgsRubberBand(self.map_canvas, QgsWkbTypes.PolygonGeometry)
        self.cursor_band.setColor(self.default_color)
        self.cursor_band.setLineStyle(Qt.DotLine)

        if self.points:
            self.cursor_band.addPoint(self.points[0])
            self.cursor_band.addPoint(self.points[-1])
            self.cursor_band.addPoint(cursor_point)

    def showLine(self):
        """Builds rubber band from all points and adds it to the map canvas."""
        self.rubber_band = QgsRubberBand(self.map_canvas, QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setColor(self.default_color)

        for point in self.points:
            if point == self.points[-1]:
                self.rubber_band.addPoint(point, True)
            self.rubber_band.addPoint(point, False)
        self.rubber_band.show()

    def canvasMoveEvent(self, event: QgsMapMouseEvent) -> None:
        move_map_point = event.snapPoint()
        self.snap_indicator.setMatch(event.mapPointMatch())
        self.createRubberBand(move_map_point)

    def canvasReleaseEvent(self, event: QgsMapMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            map_point = event.snapPoint()
            v_point = self.toLayerCoordinates(self.layer, map_point)
            self.points.append(v_point)
            if self.rubber_band:
                self.canvas().scene().removeItem(self.rubber_band)
            self.showLine()

        if event.button() == Qt.RightButton:
            if len(self.points) < 3:
                self.cleanup()
                return

            table_name, ok = QInputDialog.getText(
                self.dlg, "Name", "Input Name for Project Area:"
            )

            if not ok:
                self.cleanup()
                return

            if self.rubber_band:
                self.clearRubberBands()

            tab_name = self.dlg.tabWidget.currentWidget().objectName()

            self.add_layers_to_gpkg(table_name, tab_name)

            self.cleanup()

    def add_layers_to_gpkg(self, feature_name: str, tab_name: str) -> None:
        """
        Creates a project area and parameter file, adds them to the gpkg and adds a list-widget entry.
        """
        if tab_name == "tab_development_sites":
            kind = SETTINGS_MANAGER.development_site_prefix
            list_widget = self.dlg.listWidget_development_sites
            json_path = SETTINGS_MANAGER._default_project_development_site_path
            SETTINGS_MANAGER.set_current_development_site_parameter_table_name(
                feature_name
            )
        elif tab_name == "tab_project_areas":
            kind = SETTINGS_MANAGER.area_prefix
            list_widget = self.dlg.listWidget_project_areas
            json_path = SETTINGS_MANAGER._default_project_area_parameters_path
            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(feature_name)

        else:
            raise Exception(f"Unknown tab name: {tab_name}")

        items = []
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            items.append(item.text())

        table_name_exists = True if feature_name in items else False

        if not feature_name or table_name_exists:
            if table_name_exists:
                # TODO: Message bar here instead.
                print("Table name already exists.")
            self.cleanup()
            return

        list_widget.addItem(feature_name)

        gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={kind}"

        layer = QgsVectorLayer(gpkg_path, feature_name, "ogr")

        if not layer.isValid():
            raise Exception(f"Layer {feature_name} is not valid!")

        feature = QgsFeature()
        feature.setFields(layer.fields())

        with open(json_path, "r") as file:
            attributes = json.load(file)

        feature.setAttribute("name", feature_name)
        for key, value in attributes.items():
            if key in layer.fields().names():
                feature.setAttribute(key, value)

        polygon = QgsGeometry.fromPolygonXY([[QgsPointXY(x, y) for x, y in self.points]])
        feature.setGeometry(polygon)

        layer.startEditing()
        layer.dataProvider().addFeature(feature)
        layer.commitChanges()

        item = list_widget.findItems(feature_name, Qt.MatchExactly)[0]
        row = list_widget.row(item)
        list_widget.setCurrentRow(row)

        # Add layer to canvas
        layer.setSubsetString(f"name='{feature_name}'")
        if not layer.isValid():
            print("Layer failed to load!")
        else:
            QgsProject.instance().addMapLayer(layer)

        if not list_widget.isEnabled():
            list_widget.setEnabled(True)

    def cleanup(self):
        """Run after digitization is finished, cleans up the maptool"""
        self.clearRubberBands()
        self.layer = QgsVectorLayer(
            "Polygon?crs=EPSG:4326", "memory_polygon_layer", "memory"
        )
        self.points = list()

    def clearRubberBands(self) -> None:
        """Clears map canvas of all rubber bands and sets them to None."""
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
