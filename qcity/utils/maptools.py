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

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QInputDialog
from qgis.PyQt.QtCore import Qt
from qgis._core import (
    QgsFeature,
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
    QgsField,
    QgsFields,
    QgsWkbTypes,
)
from qgis._gui import QgsSnapIndicator

from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsVectorLayer,
    QgsPointXY,
    QgsRasterLayer,
    Qgis,
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
            self.clearRubberBands()

            gpkg_path = SETTINGS_MANAGER.get_database_path()

            layer_provider = self.layer.dataProvider()

            polygon_geometry = QgsGeometry.fromPolygonXY([self.points])

            feature = QgsFeature()
            feature.setGeometry(polygon_geometry)

            layer_provider.addFeature(feature)

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"

            table_name, ok = QInputDialog.getText(
                self.dlg, "Name", "Input Name for Project Area:"
            )
            options.layerName = table_name

            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

            schema = QgsFields()
            schema.append(QgsField("project_areas", QVariant.Double))

            error = QgsVectorFileWriter.writeAsVectorFormatV2(
                self.layer, gpkg_path, QgsCoordinateTransformContext(), options
            )
            if error[0] == QgsVectorFileWriter.NoError:
                gpkg_uri = f"{gpkg_path}|layername={table_name}"
                new_layer = QgsVectorLayer(gpkg_uri, table_name, "ogr")
                QgsProject.instance().addMapLayer(new_layer)
                self.dlg.listWidget_project_areas.addItem(table_name)

                SETTINGS_MANAGER.set_current_project_area_parameter_table_name(
                    f"{SETTINGS_MANAGER.area_parameter_prefix}{table_name}"
                )

                conn = sqlite3.connect(gpkg_path)
                cursor = conn.cursor()

                try:
                    create_table_query = f"CREATE TABLE {SETTINGS_MANAGER.area_parameter_prefix}{table_name} (widget_name TEXT NOT NULL, value FLOAT NOT NULL);"
                    cursor.execute(create_table_query)

                    with open(self._default_project_area_parameters_path, "r") as file:
                        data = json.load(file)
                    insert_queries = [
                        f"INSERT INTO {SETTINGS_MANAGER.area_parameter_prefix}{table_name} (widget_name, value) VALUES ('{widget_name}', {value});"
                        for widget_name, value in data.items()
                    ]
                    for insert_query in insert_queries:
                        cursor.execute(insert_query)

                    insert_gpkg_contents_query = """INSERT INTO gpkg_contents (table_name, data_type, identifier, description) VALUES ('widget_values', 'attributes', 'widget_values', 'A table to store widget settings');"""
                    cursor.execute(insert_gpkg_contents_query)
                    conn.commit()

                except Exception as e:
                    print(e)

                finally:
                    cursor.close()
                    conn.close()
            else:
                # TODO: message bar here instead
                print(f"Error adding layer to GeoPackage: {error[1]}")

            self.cleanup()

    def cleanup(self):
        """Run after digitization is finished, cleans up the maptool"""
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
