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
from typing import List, Union

from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
from qgis.core import (
    NULL,
    QgsGeometry,
    QgsVectorLayer,
    QgsPointXY,
    QgsRasterLayer,
    Qgis,
)
from qgis.gui import (
    QgsMapCanvas,
    QgsAdvancedDigitizingDockWidget,
    QgsMapToolCapture,
    QgsAbstractMapToolHandler,
    QgsMapToolCaptureLayerGeometry,
)

from qcity.core import LayerType, PROJECT_CONTROLLER, DatabaseUtils, LayerUtils
from qcity.core.utils import wrapped_edits


class DrawPolygonTool(QgsMapToolCaptureLayerGeometry):
    """
    A map tool for drawing polygons, for use with QGIS 3.44+

    Does support CAD digitizing dock.
    """

    def __init__(
        self, map_canvas: QgsMapCanvas, cad_dock_widget: QgsAdvancedDigitizingDockWidget
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

        parent_layer_type = None
        if self._layer_type == LayerType.DevelopmentSites:
            parent_layer_type = LayerType.ProjectAreas
        elif self._layer_type == LayerType.BuildingLevels:
            parent_layer_type = LayerType.DevelopmentSites

        if parent_layer_type is not None:
            parent_feature = PROJECT_CONTROLLER.get_feature_by_pk(
                parent_layer_type, self._parent_pk
            )
            if parent_feature is not None:
                if not LayerUtils.test_geometry_within(
                    PROJECT_CONTROLLER.get_layer(parent_layer_type),
                    parent_feature.id(),
                    polygon,
                    self.layer().crs(),
                ):
                    if (
                        QMessageBox.warning(
                            self.canvas().window(),
                            self.tr("Create {}").format(
                                self._layer_type.as_title_case(plural=False)
                            ),
                            self.tr(
                                "The digitized feature is not contained within the {}. Are you sure you want to continue?"
                            ).format(parent_layer_type.as_sentence_case(plural=False)),
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.NoButton,
                        )
                        == QMessageBox.No
                    ):
                        return

        feature_name, ok = QInputDialog.getText(
            self.canvas(),
            self.tr("Create {}").format(self._layer_type.as_title_case(plural=False)),
            self.tr("Input {} name").format(
                self._layer_type.as_sentence_case(plural=False)
            ),
        )

        if not ok:
            return

        self.create_feature(feature_name, polygon)

    def create_feature(self, feature_name: str, polygon: QgsGeometry) -> None:
        """
        Called when the new feature should be created
        """
        layer = PROJECT_CONTROLLER.get_layer(self._layer_type)

        existing_names = PROJECT_CONTROLLER.get_unique_names(
            self._layer_type, self._parent_pk
        )
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
            initial_attributes["level_index"] = (
                PROJECT_CONTROLLER.get_next_building_level(self._parent_pk)
            )
            initial_attributes["base_height"] = (
                PROJECT_CONTROLLER.get_floor_base_height(
                    self._parent_pk, initial_attributes["level_index"]
                )
            )

        feature = PROJECT_CONTROLLER.create_feature(
            self._layer_type, feature_name, polygon, initial_attributes
        )

        with wrapped_edits(layer) as edits:
            edits.addFeature(feature)


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
