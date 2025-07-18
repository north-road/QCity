import math
import os
from pathlib import Path
from typing import List, Optional, Dict

from qgis.PyQt import sip
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor

from qgis.core import (
    NULL,
    Qgis,
    QgsProject,
    QgsVectorLayer,
    QgsRelation,
    QgsRelationContext,
    QgsFeature,
    QgsFeatureRequest,
    QgsExpression,
    QgsVectorLayerUtils,
    QgsGeometry,
    QgsDistanceArea,
    QgsMapLayerElevationProperties,
    QgsProperty,
    QgsMapLayer,
)
from qgis._3d import (
    QgsVectorLayer3DRenderer,
    QgsPolygon3DSymbol,
    QgsPhongMaterialSettings,
)

from .database import DatabaseUtils
from .enums import LayerType
from .settings import SETTINGS_MANAGER
from .utils import wrapped_edits


class ProjectController(QObject):
    """
    Controller for working with QCity projects
    """

    project_area_layer_changed = pyqtSignal()
    development_site_layer_changed = pyqtSignal()
    building_level_layer_changed = pyqtSignal()
    has_all_layers_changed = pyqtSignal(bool)

    project_area_changed = pyqtSignal(int)
    development_site_changed = pyqtSignal(int)

    project_area_added = pyqtSignal(QgsFeature)
    project_area_deleted = pyqtSignal(int)
    project_area_attribute_changed = pyqtSignal(int, str, object)

    development_site_added = pyqtSignal(QgsFeature)
    development_site_deleted = pyqtSignal(int)
    # final argument is project area feature id
    development_site_attribute_changed = pyqtSignal(int, str, object, int)

    building_level_added = pyqtSignal(QgsFeature)
    building_level_deleted = pyqtSignal(int)
    # final two arguments are project area and development site feature ids
    building_level_attribute_changed = pyqtSignal(int, str, object, int, int)
    # final argument is development site feature id
    building_level_geometry_changed = pyqtSignal(int, int)

    plugin_data_path = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "data"

    def __init__(self, project: QgsProject):
        super().__init__()
        self.project = project

        self._current_project_area_layer: Optional[QgsVectorLayer] = None
        self._current_development_sites_layer: Optional[QgsVectorLayer] = None
        self._current_building_levels_layer: Optional[QgsVectorLayer] = None

        self.current_project_area_fid: Optional[int] = None
        self.current_development_site_fid: Optional[int] = None

        self.connect_layers()

        self.project.layersAdded.connect(self._update_project_layers)
        self.project.layersRemoved.connect(self._update_project_layers)

        self._block_ds_auto_updates = 0
        self._block_floor_height_updates = 0

    def cleanup(self):
        """
        Cleanups the controller, ready for deletion
        """
        self.connect_layers(False)

    def _update_project_layers(self):
        """
        Called when project layers are changed
        """
        self.connect_layers()

    def connect_layers(self, disconnect: bool = False):
        """
        Connects/disconnects from current project layers
        """
        project_area_layer = self.get_project_area_layer()

        if self._current_project_area_layer is not None and sip.isdeleted(
            self._current_project_area_layer
        ):
            self._current_project_area_layer = None
        if self._current_development_sites_layer is not None and sip.isdeleted(
            self._current_development_sites_layer
        ):
            self._current_development_sites_layer = None
        if self._current_building_levels_layer is not None and sip.isdeleted(
            self._current_building_levels_layer
        ):
            self._current_building_levels_layer = None

        if self._current_project_area_layer and (
            disconnect or self._current_project_area_layer != project_area_layer
        ):
            self._current_project_area_layer.featureAdded.disconnect(
                self._project_area_added
            )
            self._current_project_area_layer.featureDeleted.disconnect(
                self._project_area_deleted
            )
            self._current_project_area_layer.attributeValueChanged.disconnect(
                self._project_area_attribute_changed
            )

        if (
            not disconnect
            and project_area_layer
            and project_area_layer != self._current_project_area_layer
        ):
            project_area_layer.featureAdded.connect(self._project_area_added)
            project_area_layer.featureDeleted.connect(self._project_area_deleted)
            project_area_layer.attributeValueChanged.connect(
                self._project_area_attribute_changed
            )
        project_area_layer_changed = (
            self._current_project_area_layer != project_area_layer
        )
        self._current_project_area_layer = project_area_layer

        development_site_layer = self.get_development_sites_layer()
        if self._current_development_sites_layer and (
            disconnect
            or self._current_development_sites_layer != development_site_layer
        ):
            self._current_development_sites_layer.featureAdded.disconnect(
                self._development_site_added
            )
            self._current_development_sites_layer.featureDeleted.disconnect(
                self._development_site_deleted
            )
            self._current_development_sites_layer.attributeValueChanged.disconnect(
                self._development_site_attribute_changed
            )

        if (
            not disconnect
            and development_site_layer
            and development_site_layer != self._current_development_sites_layer
        ):
            development_site_layer.featureAdded.connect(self._development_site_added)
            development_site_layer.featureDeleted.connect(
                self._development_site_deleted
            )
            development_site_layer.attributeValueChanged.connect(
                self._development_site_attribute_changed
            )
        development_site_layer_changed = (
            self._current_development_sites_layer != development_site_layer
        )
        self._current_development_sites_layer = development_site_layer

        building_levels_layer = self.get_building_levels_layer()
        if self._current_building_levels_layer and (
            disconnect or self._current_building_levels_layer != building_levels_layer
        ):
            self._current_building_levels_layer.featureAdded.disconnect(
                self._building_level_added
            )
            self._current_building_levels_layer.featureDeleted.disconnect(
                self._building_level_deleted
            )
            self._current_building_levels_layer.attributeValueChanged.disconnect(
                self._building_level_attribute_changed
            )
            self._current_building_levels_layer.geometryChanged.disconnect(
                self._building_level_geometry_changed
            )

        if (
            not disconnect
            and building_levels_layer
            and building_levels_layer != self._current_building_levels_layer
        ):
            building_levels_layer.featureAdded.connect(self._building_level_added)
            building_levels_layer.featureDeleted.connect(self._building_level_deleted)
            building_levels_layer.attributeValueChanged.connect(
                self._building_level_attribute_changed
            )
            building_levels_layer.geometryChanged.connect(
                self._building_level_geometry_changed
            )

            elevation_props = building_levels_layer.elevationProperties()
            elevation_props.setExtrusionEnabled(True)
            elevation_props.dataDefinedProperties().setProperty(
                QgsMapLayerElevationProperties.ZOffset,
                QgsProperty.fromField("base_height"),
            )
            elevation_props.dataDefinedProperties().setProperty(
                QgsMapLayerElevationProperties.ExtrusionHeight,
                QgsProperty.fromField("level_height"),
            )

            if not building_levels_layer.renderer3D():
                symbol = QgsPolygon3DSymbol()
                symbol.setDefaultPropertiesFromLayer(building_levels_layer)
                symbol.setEdgesEnabled(True)
                symbol.setEdgeWidth(2)

                material = QgsPhongMaterialSettings()
                material.setDiffuse(QColor(160, 160, 160))
                material.setAmbient(QColor(90, 90, 90))
                symbol.setMaterialSettings(material)

                renderer = QgsVectorLayer3DRenderer(symbol)
                building_levels_layer.setRenderer3D(renderer)

        building_level_layer_changed = (
            self._current_building_levels_layer != building_levels_layer
        )
        self._current_building_levels_layer = building_levels_layer

        if project_area_layer_changed:
            self.project_area_layer_changed.emit()
        if development_site_layer_changed:
            self.development_site_layer_changed.emit()
        if building_level_layer_changed:
            self.building_level_layer_changed.emit()

        self.has_all_layers_changed.emit(
            bool(
                self._current_project_area_layer
                and self._current_development_sites_layer
                and self._current_building_levels_layer
            )
        )

    def _project_area_added(self, project_area_fid: int):
        """
        Called when a new project area is added to the layer
        """
        if project_area_fid < 0:
            # ignore uncommitted features
            return

        self.project_area_added.emit(
            self.get_project_area_layer().getFeature(project_area_fid)
        )

    def _project_area_deleted(self, project_area_fid: int):
        """
        Called when a project area is deleted
        """
        if project_area_fid < 0:
            # ignore uncommitted features
            return

        self.project_area_deleted.emit(project_area_fid)

    def _project_area_attribute_changed(self, feature_id: int, field_index: int, value):
        """
        Called when a project area attribute is changed
        """
        if feature_id < 0:
            # ignore uncommitted features
            return

        layer = self.get_project_area_layer()
        field_name = layer.fields()[field_index].name()

        self.project_area_attribute_changed.emit(feature_id, field_name, value)

        if field_name in (
            "dwelling_size_1_bedroom",
            "dwelling_size_2_bedroom",
            "dwelling_size_3_bedroom",
            "dwelling_size_4_bedroom",
            "car_parking_1_bedroom",
            "car_parking_2_bedroom",
            "car_parking_3_bedroom",
            "car_parking_4_bedroom",
            "car_parking_commercial_bays_count",
            "car_parking_commercial_bays_area",
            "car_parking_office_bays_count",
            "car_parking_office_bays_area",
            "bicycle_parking_1_bedroom",
            "bicycle_parking_2_bedroom",
            "bicycle_parking_3_bedroom",
            "bicycle_parking_4_bedroom",
            "bicycle_parking_commercial_bays_count",
            "bicycle_parking_commercial_bays_area",
            "bicycle_parking_office_bays_count",
            "bicycle_parking_office_bays_area",
        ):
            project_area_feature = layer.getFeature(feature_id)
            if not project_area_feature.isValid():
                return

            project_area_primary_key = project_area_feature[
                DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas)
            ]

            # find matching development sites
            request = QgsFeatureRequest().setFilterExpression(
                QgsExpression.createFieldEqualityExpression(
                    DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites),
                    project_area_primary_key,
                )
            )
            development_site_layer = self.get_development_sites_layer()
            for f in development_site_layer.getFeatures(request):
                self.auto_calculate_development_site_floorspace(f.id())
                self.auto_calculate_development_site_car_parking(f.id())
                self.auto_calculate_development_site_bicycle_parking(f.id())

    def _development_site_added(self, development_site_fid: int):
        """
        Called when a new development site is added to the layer
        """
        if development_site_fid < 0:
            # ignore uncommitted features
            return

        self.development_site_added.emit(
            self.get_development_sites_layer().getFeature(development_site_fid)
        )

    def _development_site_deleted(self, development_site_fid: int):
        """
        Called when a development site is deleted
        """
        if development_site_fid < 0:
            # ignore uncommitted features
            return

        self.development_site_deleted.emit(development_site_fid)

    def _development_site_attribute_changed(
        self, feature_id: int, field_index: int, value
    ):
        """
        Called when a development site attribute is changed
        """
        if feature_id < 0:
            # ignore uncommitted features
            return

        layer = self.get_development_sites_layer()
        field_name = layer.fields()[field_index].name()

        original_feature = layer.getFeature(feature_id)
        project_area_key = original_feature[
            DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites)
        ]

        self.development_site_attribute_changed.emit(
            feature_id, field_name, value, project_area_key
        )

        if (
            not self._block_ds_auto_updates
            and original_feature["auto_calculate_floorspace"]
            and field_name
            in (
                "commercial_floorspace",
                "office_floorspace",
                "residential_floorspace",
                "count_1_bedroom_dwellings",
                "count_2_bedroom_dwellings",
                "count_3_bedroom_dwellings",
                "count_4_bedroom_dwellings",
            )
        ):
            with wrapped_edits(layer) as edits:
                edits.changeAttributeValues(
                    feature_id,
                    {layer.fields().lookupField("auto_calculate_floorspace"): False},
                )

        if (
            not self._block_ds_auto_updates
            and original_feature["auto_calculate_car_parking"]
            and field_name
            in ("commercial_car_bays", "residential_car_bays", "office_car_bays")
        ):
            with wrapped_edits(layer) as edits:
                edits.changeAttributeValues(
                    feature_id,
                    {layer.fields().lookupField("auto_calculate_car_parking"): False},
                )

        if (
            not self._block_ds_auto_updates
            and original_feature["auto_calculate_bicycle_parking"]
            and field_name
            in (
                "commercial_bicycle_bays",
                "office_bicycle_bays",
                "residential_bicycle_bays",
            )
        ):
            with wrapped_edits(layer) as edits:
                edits.changeAttributeValues(
                    feature_id,
                    {
                        layer.fields().lookupField(
                            "auto_calculate_bicycle_parking"
                        ): False
                    },
                )

        if field_name in (
            "commercial_floorspace",
            "office_floorspace",
            "residential_floorspace",
            "count_1_bedroom_dwellings",
            "count_2_bedroom_dwellings",
            "count_3_bedroom_dwellings",
            "count_4_bedroom_dwellings",
        ):
            self.auto_calculate_development_site_car_parking(feature_id)
            self.auto_calculate_development_site_bicycle_parking(feature_id)

    def _building_level_attribute_changed(
        self, feature_id: int, field_index: int, value
    ):
        """
        Called when a building level attribute is changed
        """
        if feature_id < 0:
            # ignore uncommitted features
            return

        layer = self.get_building_levels_layer()
        field_name = layer.fields()[field_index].name()

        original_feature = layer.getFeature(feature_id)
        development_site_key = original_feature[
            DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels)
        ]
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites),
                development_site_key,
            )
        )
        development_site_layer = self.get_development_sites_layer()
        development_site_features = [
            f for f in development_site_layer.getFeatures(request)
        ]
        development_site_feature = development_site_features[0]

        project_area_key = development_site_feature[
            DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites)
        ]

        self.building_level_attribute_changed.emit(
            feature_id, field_name, value, project_area_key, development_site_key
        )

        if field_name in (
            "percent_commercial_floorspace",
            "percent_office_floorspace",
            "percent_residential_floorspace",
            "percent_1_bedroom_floorspace",
            "percent_2_bedroom_floorspace",
            "percent_3_bedroom_floorspace",
            "percent_4_bedroom_floorspace",
        ):
            self.auto_calculate_development_site_floorspace(
                development_site_feature.id()
            )
        if field_name in ("level_index", "level_height"):
            if not self._block_floor_height_updates:
                self.update_floor_heights(development_site_feature.id())

    def _building_level_geometry_changed(self, feature_id: int, geometry: QgsGeometry):
        """
        Called when a building level geometry is changed
        """
        if feature_id < 0:
            # ignore uncommitted features
            return

        layer = self.get_building_levels_layer()

        original_feature = layer.getFeature(feature_id)
        development_site_key = original_feature[
            DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels)
        ]
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites),
                development_site_key,
            )
        )
        development_site_layer = self.get_development_sites_layer()
        development_site_features = [
            f for f in development_site_layer.getFeatures(request)
        ]
        development_site_feature = development_site_features[0]

        self.auto_calculate_development_site_floorspace(development_site_feature.id())

        self.building_level_geometry_changed.emit(feature_id, development_site_key)

    def _building_level_added(self, building_level_fid: int):
        """
        Called when a new building level is added to the layer
        """
        if building_level_fid < 0:
            # ignore uncommitted features
            return

        self.building_level_added.emit(
            self.get_building_levels_layer().getFeature(building_level_fid)
        )

    def _building_level_deleted(self, building_level_fid: int):
        """
        Called when a building level is deleted
        """
        if building_level_fid < 0:
            # ignore uncommitted features
            return

        self.building_level_deleted.emit(building_level_fid)

    @staticmethod
    def load_qml_if_exists(layer: QgsMapLayer, qml_path: str):
        """
        Loads and applies a QML file from the data folder
        """
        full_path = ProjectController.plugin_data_path / qml_path
        if full_path.exists():
            layer.loadNamedStyle(full_path.as_posix())

    @staticmethod
    def add_database_layers_to_project(project: QgsProject, database_path: str) -> None:
        """Adds the layers from the gpkg to the canvas"""
        for _, layer in project.mapLayers().items():
            layer.setCustomProperty("_qcity_role", "")

        area_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.project_area_prefix}",
            SETTINGS_MANAGER.project_area_prefix,
            "ogr",
        )
        assert area_layer.isValid()

        ProjectController.load_qml_if_exists(
            area_layer, "default_project_areas_style.qml"
        )

        area_layer.setCustomProperty("_qcity_role", "project_areas")

        development_site_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.development_site_prefix}",
            SETTINGS_MANAGER.development_site_prefix,
            "ogr",
        )
        assert development_site_layer.isValid()

        ProjectController.load_qml_if_exists(
            development_site_layer, "default_development_sites_style.qml"
        )
        development_site_layer.setCustomProperty("_qcity_role", "development_sites")

        building_level_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.building_level_prefix}",
            SETTINGS_MANAGER.building_level_prefix,
            "ogr",
        )
        assert building_level_layer.isValid()
        ProjectController.load_qml_if_exists(
            building_level_layer, "default_building_levels_style.qml"
        )
        building_level_layer.setCustomProperty("_qcity_role", "building_levels")

        prev_insertion_method = None
        if Qgis.QGIS_VERSION_INT >= 33000:
            prev_insertion_method = (
                project.layerTreeRegistryBridge().layerInsertionMethod()
            )
            project.layerTreeRegistryBridge().setLayerInsertionMethod(
                Qgis.LayerTreeInsertionMethod.TopOfTree
            )

        project.addMapLayers([building_level_layer, development_site_layer, area_layer])
        if Qgis.QGIS_VERSION_INT >= 33000:
            project.layerTreeRegistryBridge().setLayerInsertionMethod(
                prev_insertion_method
            )

    def get_project_area_layer(self) -> Optional[QgsVectorLayer]:
        """
        Retrieves the project area layer from a project
        """
        for _, layer in self.project.mapLayers().items():
            if layer.customProperty("_qcity_role") == "project_areas":
                return layer

        return None

    def get_development_sites_layer(self) -> Optional[QgsVectorLayer]:
        """
        Retrieves the development sites layer from a project
        """
        for _, layer in self.project.mapLayers().items():
            if layer.customProperty("_qcity_role") == "development_sites":
                return layer

        return None

    def get_building_levels_layer(self) -> Optional[QgsVectorLayer]:
        """
        Retrieves the building levels layer from a project
        """
        for _, layer in self.project.mapLayers().items():
            if layer.customProperty("_qcity_role") == "building_levels":
                return layer

        return None

    def get_layer(self, layer: LayerType) -> Optional[QgsVectorLayer]:
        """
        Retrieves the specified QCity layer from a project
        """
        if layer == LayerType.ProjectAreas:
            return self.get_project_area_layer()
        if layer == LayerType.DevelopmentSites:
            return self.get_development_sites_layer()
        if layer == LayerType.BuildingLevels:
            return self.get_building_levels_layer()
        return None

    def get_feature_by_pk(self, layer: LayerType, pk) -> Optional[QgsFeature]:
        """
        Retrieves a feature by primary key
        """
        vector_layer = self.get_layer(layer)
        if vector_layer is None:
            return None

        pk_field = DatabaseUtils.primary_key_for_layer(layer)
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(pk_field, pk)
        )
        for f in vector_layer.getFeatures(request):
            return f

        return None

    def get_unique_names(
        self, layer: LayerType, parent_key: Optional[int] = None
    ) -> List[str]:
        """
        Gets a list of all existing unique names for the specified layer type,
        sorted alphabetically.
        """
        map_layer = self.get_layer(layer)
        name_field = DatabaseUtils.name_field_for_layer(layer)

        if parent_key is None:
            return sorted(
                map_layer.uniqueValues(map_layer.fields().lookupField(name_field)),
                key=str.casefold,
            )

        foreign_key_name = DatabaseUtils.foreign_key_for_layer(layer)
        _filter = QgsExpression.createFieldEqualityExpression(
            foreign_key_name,
            parent_key,
        )
        request = (
            QgsFeatureRequest()
            .setFilterExpression(_filter)
            .setSubsetOfAttributes([name_field], map_layer.fields())
        )
        values = set()
        for f in map_layer.getFeatures(request):
            values.add(f[name_field])

        return sorted(
            list(values),
            key=str.casefold,
        )

    def get_next_building_level(self, development_site_fid: int) -> int:
        """
        Returns the next building level to use for a new level added to the
        matching development site.
        """
        development_site_layer = self.get_development_sites_layer()
        development_site_feature = development_site_layer.getFeature(
            development_site_fid
        )

        # find matching building levels
        development_site_primary_key = development_site_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)
        ]
        building_levels_filter = QgsExpression.createFieldEqualityExpression(
            DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels),
            development_site_primary_key,
        )
        request = QgsFeatureRequest().setFilterExpression(building_levels_filter)
        building_level_layer = self.get_building_levels_layer()

        max_building_level = None
        for f in building_level_layer.getFeatures(request):
            level = f["level_index"]
            if level != NULL and (
                max_building_level is None or level > max_building_level
            ):
                max_building_level = level

        return (max_building_level + 1) if max_building_level else 1

    def get_floor_base_height(
        self, development_site_fid: int, level_index: int
    ) -> float:
        """
        Calculates the base floor height for all floors below the specified index
        """
        development_site_layer = self.get_development_sites_layer()
        development_site_feature = development_site_layer.getFeature(
            development_site_fid
        )

        # find matching building levels
        development_site_primary_key = development_site_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)
        ]
        building_levels_filter = QgsExpression.createFieldEqualityExpression(
            DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels),
            development_site_primary_key,
        )
        request = QgsFeatureRequest().setFilterExpression(building_levels_filter)
        request.combineFilterExpression(f'"level_index" < {level_index}')
        building_level_layer = self.get_building_levels_layer()

        current_floor_height = 0
        for f in building_level_layer.getFeatures(request):
            height = f["level_height"]
            if height != NULL:
                current_floor_height += height

        return current_floor_height

    def move_building_level(self, building_level_fid: int, up: bool = True) -> bool:
        """
        Moves a building level up or down
        """
        building_level_layer = self.get_building_levels_layer()
        if not building_level_layer:
            return False

        feature_to_move = building_level_layer.getFeature(building_level_fid)
        if not feature_to_move.isValid():
            return False

        level_index_field_name = "level_index"
        level_height_field_name = "level_height"
        base_height_field_name = "base_height"
        development_site_fk_field = DatabaseUtils.foreign_key_for_layer(
            LayerType.BuildingLevels
        )

        development_site_pk = feature_to_move[development_site_fk_field]

        # fetch all building levels for this development site
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                development_site_fk_field, development_site_pk
            )
        )

        all_levels_in_site_data = []
        for f in building_level_layer.getFeatures(request):
            level_idx_val = f[level_index_field_name]
            all_levels_in_site_data.append(
                {
                    "fid": f.id(),
                    "current_index": level_idx_val,
                    "height": f[level_height_field_name]
                    if f[level_height_field_name] is not NULL
                    else 0.0,
                }
            )
        all_levels_in_site_data.sort(key=lambda x: x["current_index"])

        original_list_idx = -1
        for i, level_data in enumerate(all_levels_in_site_data):
            if level_data["fid"] == building_level_fid:
                original_list_idx = i
                break

        if up:
            new_list_idx = original_list_idx + 1
        else:  # down
            new_list_idx = original_list_idx - 1

        if new_list_idx < 0:
            new_list_idx = 0
        elif new_list_idx >= len(all_levels_in_site_data):
            new_list_idx = len(all_levels_in_site_data) - 1

        moved_item = all_levels_in_site_data.pop(original_list_idx)
        all_levels_in_site_data.insert(new_list_idx, moved_item)

        with wrapped_edits(building_level_layer) as edits:
            fields = building_level_layer.fields()
            level_index_fidx = fields.lookupField(level_index_field_name)
            base_height_fidx = fields.lookupField(base_height_field_name)

            current_cumulative_height = 0.0

            self._block_floor_height_updates += 1
            for i, level_data in enumerate(all_levels_in_site_data):
                new_level_index_val = i + 1
                new_base_height_val = current_cumulative_height

                attrs_to_update = {
                    level_index_fidx: new_level_index_val,
                    base_height_fidx: new_base_height_val,
                }

                if not edits.changeAttributeValues(level_data["fid"], attrs_to_update):
                    return False

                current_cumulative_height += level_data[
                    "height"
                ]  # Use pre-fetched height

            self._block_floor_height_updates -= 1

        return True

    def update_floor_heights(self, development_site_id: int) -> bool:
        """
        Recalculated building floor heights for a development site
        """
        if self._block_floor_height_updates:
            return False

        development_site_layer = self.get_development_sites_layer()
        development_site_feature = development_site_layer.getFeature(
            development_site_id
        )
        development_site_pk = development_site_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)
        ]

        building_level_layer = self.get_building_levels_layer()
        if not building_level_layer:
            return False

        level_index_field_name = "level_index"
        level_height_field_name = "level_height"
        base_height_field_name = "base_height"
        development_site_fk_field = DatabaseUtils.foreign_key_for_layer(
            LayerType.BuildingLevels
        )

        # fetch all building levels for this development site
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                development_site_fk_field, development_site_pk
            )
        )

        all_levels_in_site_data = []
        for f in building_level_layer.getFeatures(request):
            level_idx_val = f[level_index_field_name]
            all_levels_in_site_data.append(
                {
                    "fid": f.id(),
                    "current_index": level_idx_val,
                    "base_height": f[base_height_field_name],
                    "height": f[level_height_field_name]
                    if f[level_height_field_name] is not NULL
                    else 0.0,
                }
            )
        all_levels_in_site_data.sort(key=lambda x: x["current_index"])

        with wrapped_edits(building_level_layer) as edits:
            fields = building_level_layer.fields()
            level_index_fidx = fields.lookupField(level_index_field_name)
            base_height_fidx = fields.lookupField(base_height_field_name)

            current_cumulative_height = 0.0

            self._block_floor_height_updates += 1
            for i, level_data in enumerate(all_levels_in_site_data):
                new_level_index_val = i + 1
                new_base_height_val = current_cumulative_height

                if (
                    level_data["current_index"] != new_level_index_val
                    or level_data["base_height"] != new_base_height_val
                ):
                    attrs_to_update = {
                        level_index_fidx: new_level_index_val,
                        base_height_fidx: new_base_height_val,
                    }

                    if not edits.changeAttributeValues(
                        level_data["fid"], attrs_to_update
                    ):
                        return False

                current_cumulative_height += level_data["height"] or 0

            self._block_floor_height_updates -= 1

        return True

    def create_feature(
        self,
        layer: LayerType,
        name: str,
        geometry: QgsGeometry,
        initial_attributes: Optional[Dict[str, object]] = None,
    ) -> QgsFeature:
        """
        Creates a new feature, initialized with defaults, for the given layer
        """
        map_layer = self.get_layer(layer)
        if not map_layer:
            return QgsFeature()

        attributes = {}
        if initial_attributes:
            for key, value in initial_attributes.items():
                attributes[map_layer.fields().lookupField(key)] = value

        for field_index, field in enumerate(map_layer.fields()):
            if field.name() == DatabaseUtils.name_field_for_layer(layer):
                attributes[field_index] = name
            elif initial_attributes is None or field.name() not in initial_attributes:
                default_value = DatabaseUtils.get_field_default(layer, field.name())
                if default_value is not None:
                    attributes[field_index] = default_value

        feature = QgsVectorLayerUtils.createFeature(map_layer, geometry, attributes)
        return feature

    def create_layer_relations(self):
        """Adds relations between layers to the QGIS project."""
        relation_manager = self.project.relationManager()
        existing_relations = {
            rel.name() for rel in relation_manager.relations().values()
        }

        if (
            "project_area_to_development_sites" in existing_relations
            and "development_sites_to_building_levels" in existing_relations
        ):
            return

        project_area_layer = self.get_project_area_layer()
        development_site_layer = self.get_development_sites_layer()
        building_level_layer = self.get_building_levels_layer()
        if (
            not project_area_layer
            or not development_site_layer
            or not building_level_layer
        ):
            return

        relations = [
            (
                "project_area_to_development_sites",
                project_area_layer,
                development_site_layer,
                "project_area_pk",
            ),
            (
                "development_sites_to_building_levels",
                development_site_layer,
                building_level_layer,
                "development_site_pk",
            ),
        ]

        context = QgsRelationContext(self.project)
        for name, parent_layer, child_layer, foreign_key in relations:
            relation = QgsRelation(context)
            relation.setName(name)
            relation.setReferencedLayer(parent_layer.id())
            relation.setReferencingLayer(child_layer.id())
            relation.addFieldPair(foreign_key, "fid")
            relation.setId(name)
            relation.setStrength(QgsRelation.Association)
            assert relation.isValid(), relation.validationError()
            relation_manager.addRelation(relation)

    def set_associated_database_path(self, path: str):
        """
        Sets the database path which is associated with a project
        """
        self.project.writeEntry("qcity", "database_path", path)

    def associated_database_path(self) -> str:
        """
        Returns the database path associated with a project
        """
        return self.project.readEntry("qcity", "database_path")[0]

    def set_current_project_area(self, project_area_fid: int):
        """
        Sets the feature ID for the current project area
        """
        self.current_project_area_fid = project_area_fid
        self.project_area_changed.emit(self.current_project_area_fid)

        project_area_layer = self.get_project_area_layer()
        project_area_feature = project_area_layer.getFeature(project_area_fid)
        if not project_area_feature.isValid():
            return

        project_area_primary_key = project_area_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas)
        ]

        from .layer import LayerUtils

        if SETTINGS_MANAGER.use_rule_based_layer_filters():
            LayerUtils.set_renderer_filter(
                project_area_layer,
                QgsExpression.createFieldEqualityExpression(
                    DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas),
                    project_area_primary_key,
                ),
            )

        if SETTINGS_MANAGER.synchronize_layer_selection():
            project_area_layer.selectByIds([project_area_fid])

    def set_current_development_site(self, development_site_fid: int):
        """
        Sets the feature ID for the current development site
        """
        self.current_development_site_fid = development_site_fid
        self.development_site_changed.emit(self.current_development_site_fid)

        development_site_layer = self.get_development_sites_layer()
        development_site_feature = development_site_layer.getFeature(
            development_site_fid
        )
        if not development_site_feature.isValid():
            return

        development_site_primary_key = development_site_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)
        ]

        from .layer import LayerUtils

        if SETTINGS_MANAGER.use_rule_based_layer_filters():
            LayerUtils.set_renderer_filter(
                development_site_layer,
                QgsExpression.createFieldEqualityExpression(
                    DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites),
                    development_site_primary_key,
                ),
            )

        if SETTINGS_MANAGER.synchronize_layer_selection():
            development_site_layer.selectByIds([development_site_fid])

    def set_current_building_level(self, building_level_fid: int):
        """
        Sets the feature ID for the current building level feature
        """
        building_level_layer = self.get_building_levels_layer()
        if SETTINGS_MANAGER.synchronize_layer_selection():
            building_level_layer.selectByIds([building_level_fid])

    def delete_project_area(self, project_area_fid: int) -> bool:
        """
        Deletes the specified project area, and all child objects
        """
        project_area_layer = self.get_project_area_layer()
        if not project_area_layer:
            return False

        project_area_feature = project_area_layer.getFeature(project_area_fid)
        if not project_area_feature.isValid():
            return False

        project_area_primary_key = project_area_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas)
        ]

        # find matching development sites
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites),
                project_area_primary_key,
            )
        )
        development_site_layer = self.get_development_sites_layer()
        development_site_features = [
            f for f in development_site_layer.getFeatures(request)
        ]

        # find matching building levels
        development_site_primary_keys = [
            f[DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)]
            for f in development_site_features
        ]
        building_levels_filter = "{} IN ({})".format(
            DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels),
            ",".join([str(k) for k in development_site_primary_keys]),
        )
        request = QgsFeatureRequest().setFilterExpression(building_levels_filter)
        building_level_layer = self.get_building_levels_layer()
        building_level_features = [f for f in building_level_layer.getFeatures(request)]

        with (
            wrapped_edits(building_level_layer) as building_level_edits,
            wrapped_edits(development_site_layer) as development_site_edits,
            wrapped_edits(project_area_layer) as project_area_edits,
        ):
            if (
                not building_level_layer.isEditable()
                or not development_site_layer.isEditable()
                or not project_area_layer.isEditable()
            ):
                return False

            # only commit if ALL layer edits were successful
            if (
                not building_level_edits.deleteFeatures(
                    [f.id() for f in building_level_features]
                )
                or not development_site_edits.deleteFeatures(
                    [f.id() for f in development_site_features]
                )
                or not project_area_edits.deleteFeature(project_area_fid)
            ):
                building_level_edits.error_occurred = True
                development_site_edits.error_occurred = True
                project_area_edits.error_occurred = True
                return False

        return True

    def delete_development_site(self, development_site_fid: int) -> bool:
        """
        Deletes the specified development site, and all child objects
        """
        development_site_layer = self.get_development_sites_layer()
        if not development_site_layer:
            return False

        development_site_feature = development_site_layer.getFeature(
            development_site_fid
        )
        if not development_site_feature.isValid():
            return False

        development_site_primary_key = development_site_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)
        ]

        # find matching building levels
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels),
                development_site_primary_key,
            )
        )
        building_level_layer = self.get_building_levels_layer()
        building_level_features = [f for f in building_level_layer.getFeatures(request)]

        with (
            wrapped_edits(building_level_layer) as building_level_edits,
            wrapped_edits(development_site_layer) as development_site_edits,
        ):
            if (
                not building_level_layer.isEditable()
                or not development_site_layer.isEditable()
            ):
                return False

            # only commit if ALL layer edits were successful
            if not building_level_edits.deleteFeatures(
                [f.id() for f in building_level_features]
            ) or not development_site_edits.deleteFeature(development_site_fid):
                building_level_edits.error_occurred = True
                development_site_edits.error_occurred = True
                return False

        return True

    def delete_building_level(self, building_level_fid: int) -> bool:
        """
        Deletes the specified building level
        """
        building_level_layer = self.get_building_levels_layer()
        if not building_level_layer:
            return False

        building_level_feature = building_level_layer.getFeature(building_level_fid)
        if not building_level_feature.isValid():
            return False

        with wrapped_edits(building_level_layer) as edits:
            if not edits.deleteFeature(building_level_fid):
                return False
        return True

    def auto_calculate_development_site_floorspace(
        self, development_site_fid: int
    ) -> bool:
        """
        Auto calculates the development site floor space
        """
        development_site_layer = self.get_development_sites_layer()
        if not development_site_layer:
            return False

        development_site_feature = development_site_layer.getFeature(
            development_site_fid
        )
        if not development_site_feature.isValid():
            return False

        if not development_site_feature["auto_calculate_floorspace"]:
            return False

        development_site_primary_key = development_site_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)
        ]

        # find project area
        project_area_layer = self.get_project_area_layer()
        project_area_key = development_site_feature[
            DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites)
        ]
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas),
                project_area_key,
            )
        )
        project_area_feature = next(project_area_layer.getFeatures(request))
        dwelling_size_1_bedroom = project_area_feature["dwelling_size_1_bedroom"]
        dwelling_size_2_bedroom = project_area_feature["dwelling_size_2_bedroom"]
        dwelling_size_3_bedroom = project_area_feature["dwelling_size_3_bedroom"]
        dwelling_size_4_bedroom = project_area_feature["dwelling_size_4_bedroom"]

        # find matching building levels
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels),
                development_site_primary_key,
            )
        )
        building_level_layer = self.get_building_levels_layer()
        building_level_features = [f for f in building_level_layer.getFeatures(request)]

        total_commercial = 0
        total_office = 0
        total_residential = 0
        count_1_bedroom = 0
        count_2_bedroom = 0
        count_3_bedroom = 0
        count_4_bedroom = 0

        da = QgsDistanceArea()
        da.setEllipsoid(self.project.ellipsoid())
        da.setSourceCrs(building_level_layer.crs(), self.project.transformContext())

        for level in building_level_features:
            floor_area_m2 = da.convertAreaMeasurement(
                da.measureArea(level.geometry()), Qgis.AreaUnit.SquareMeters
            )
            total_commercial += (
                level["percent_commercial_floorspace"] / 100 * floor_area_m2
            )
            total_office += level["percent_office_floorspace"] / 100 * floor_area_m2
            residential_area_m2 = (
                level["percent_residential_floorspace"] / 100 * floor_area_m2
            )
            total_residential += residential_area_m2

            floor_1_bedroom = (
                level["percent_1_bedroom_floorspace"] / 100 * residential_area_m2
            )
            floor_2_bedroom = (
                level["percent_2_bedroom_floorspace"] / 100 * residential_area_m2
            )
            floor_3_bedroom = (
                level["percent_3_bedroom_floorspace"] / 100 * residential_area_m2
            )
            floor_4_bedroom = (
                level["percent_4_bedroom_floorspace"] / 100 * residential_area_m2
            )

            count_1_bedroom += math.floor(floor_1_bedroom / dwelling_size_1_bedroom)
            count_2_bedroom += math.floor(floor_2_bedroom / dwelling_size_2_bedroom)
            count_3_bedroom += math.floor(floor_3_bedroom / dwelling_size_3_bedroom)
            count_4_bedroom += math.floor(floor_4_bedroom / dwelling_size_4_bedroom)

        self._block_ds_auto_updates += 1
        with wrapped_edits(development_site_layer) as edits:
            edits.changeAttributeValues(
                development_site_fid,
                {
                    development_site_layer.fields().lookupField(
                        "commercial_floorspace"
                    ): total_commercial,
                    development_site_layer.fields().lookupField(
                        "office_floorspace"
                    ): total_office,
                    development_site_layer.fields().lookupField(
                        "residential_floorspace"
                    ): total_residential,
                    development_site_layer.fields().lookupField(
                        "count_1_bedroom_dwellings"
                    ): count_1_bedroom,
                    development_site_layer.fields().lookupField(
                        "count_2_bedroom_dwellings"
                    ): count_2_bedroom,
                    development_site_layer.fields().lookupField(
                        "count_3_bedroom_dwellings"
                    ): count_3_bedroom,
                    development_site_layer.fields().lookupField(
                        "count_4_bedroom_dwellings"
                    ): count_4_bedroom,
                },
            )

        self._block_ds_auto_updates -= 1
        return True

    def auto_calculate_development_site_car_parking(
        self, development_site_fid: int
    ) -> bool:
        """
        Auto calculates the development site car parking
        """
        development_site_layer = self.get_development_sites_layer()
        if not development_site_layer:
            return False

        development_site_feature = development_site_layer.getFeature(
            development_site_fid
        )
        if not development_site_feature.isValid():
            return False

        if not development_site_feature["auto_calculate_car_parking"]:
            return False

        # find project area
        project_area_layer = self.get_project_area_layer()
        project_area_key = development_site_feature[
            DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites)
        ]
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas),
                project_area_key,
            )
        )
        project_area_feature = next(project_area_layer.getFeatures(request))

        car_parks_1_bedroom = (
            project_area_feature["car_parking_1_bedroom"]
            * development_site_feature["count_1_bedroom_dwellings"]
        )
        car_parks_2_bedroom = (
            project_area_feature["car_parking_2_bedroom"]
            * development_site_feature["count_2_bedroom_dwellings"]
        )
        car_parks_3_bedroom = (
            project_area_feature["car_parking_3_bedroom"]
            * development_site_feature["count_3_bedroom_dwellings"]
        )
        car_parks_4_bedroom = (
            project_area_feature["car_parking_4_bedroom"]
            * development_site_feature["count_4_bedroom_dwellings"]
        )
        commercial_car_parks = math.ceil(
            project_area_feature["car_parking_commercial_bays_count"]
            * development_site_feature["commercial_floorspace"]
            / project_area_feature["car_parking_commercial_bays_area"]
        )
        office_car_parks = math.ceil(
            project_area_feature["car_parking_office_bays_count"]
            * development_site_feature["office_floorspace"]
            / project_area_feature["car_parking_office_bays_area"]
        )

        self._block_ds_auto_updates += 1
        with wrapped_edits(development_site_layer) as edits:
            edits.changeAttributeValues(
                development_site_fid,
                {
                    development_site_layer.fields().lookupField(
                        "residential_car_bays"
                    ): car_parks_1_bedroom
                    + car_parks_2_bedroom
                    + car_parks_3_bedroom
                    + car_parks_4_bedroom,
                    development_site_layer.fields().lookupField(
                        "commercial_car_bays"
                    ): commercial_car_parks,
                    development_site_layer.fields().lookupField(
                        "office_car_bays"
                    ): office_car_parks,
                },
            )
        self._block_ds_auto_updates -= 1
        return True

    def auto_calculate_development_site_bicycle_parking(
        self, development_site_fid: int
    ) -> bool:
        """
        Auto calculates the development site bicycle parking
        """
        development_site_layer = self.get_development_sites_layer()
        if not development_site_layer:
            return False

        development_site_feature = development_site_layer.getFeature(
            development_site_fid
        )
        if not development_site_feature.isValid():
            return False

        if not development_site_feature["auto_calculate_bicycle_parking"]:
            return False

        # find project area
        project_area_layer = self.get_project_area_layer()
        project_area_key = development_site_feature[
            DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites)
        ]
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas),
                project_area_key,
            )
        )
        project_area_feature = next(project_area_layer.getFeatures(request))

        bicycle_parks_1_bedroom = (
            project_area_feature["bicycle_parking_1_bedroom"]
            * development_site_feature["count_1_bedroom_dwellings"]
        )
        bicycle_parks_2_bedroom = (
            project_area_feature["bicycle_parking_2_bedroom"]
            * development_site_feature["count_2_bedroom_dwellings"]
        )
        bicycle_parks_3_bedroom = (
            project_area_feature["bicycle_parking_3_bedroom"]
            * development_site_feature["count_3_bedroom_dwellings"]
        )
        bicycle_parks_4_bedroom = (
            project_area_feature["bicycle_parking_4_bedroom"]
            * development_site_feature["count_4_bedroom_dwellings"]
        )
        commercial_bicycle_parks = math.ceil(
            project_area_feature["bicycle_parking_commercial_bays_count"]
            * development_site_feature["commercial_floorspace"]
            / project_area_feature["bicycle_parking_commercial_bays_area"]
        )
        office_bicycle_parks = math.ceil(
            project_area_feature["bicycle_parking_office_bays_count"]
            * development_site_feature["office_floorspace"]
            / project_area_feature["bicycle_parking_office_bays_area"]
        )

        self._block_ds_auto_updates += 1
        with wrapped_edits(development_site_layer) as edits:
            edits.changeAttributeValues(
                development_site_fid,
                {
                    development_site_layer.fields().lookupField(
                        "residential_bicycle_bays"
                    ): bicycle_parks_1_bedroom
                    + bicycle_parks_2_bedroom
                    + bicycle_parks_3_bedroom
                    + bicycle_parks_4_bedroom,
                    development_site_layer.fields().lookupField(
                        "commercial_bicycle_bays"
                    ): commercial_bicycle_parks,
                    development_site_layer.fields().lookupField(
                        "office_bicycle_bays"
                    ): office_bicycle_parks,
                },
            )
        self._block_ds_auto_updates -= 1
        return True

    def calculate_project_area_stats(self, project_area_fid: int) -> Dict[str, float]:
        """
        Calculates the statistics of all development sites in a project area
        """
        totals = {
            "commercial_floorspace": 0,
            "office_floorspace": 0,
            "residential_floorspace": 0,
            "count_1_bedroom_dwellings": 0,
            "count_2_bedroom_dwellings": 0,
            "count_3_bedroom_dwellings": 0,
            "count_4_bedroom_dwellings": 0,
            "total_dwellings": 0,
            "commercial_car_bays": 0,
            "office_car_bays": 0,
            "residential_car_bays": 0,
            "commercial_bicycle_bays": 0,
            "office_bicycle_bays": 0,
            "residential_bicycle_bays": 0,
        }

        project_area_layer = self.get_project_area_layer()
        project_area_feature = project_area_layer.getFeature(project_area_fid)
        if not project_area_feature.isValid():
            return {}

        project_area_key = project_area_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas)
        ]
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(
                DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites),
                project_area_key,
            )
        )
        development_site_layer = self.get_development_sites_layer()
        all_keys = list(totals.keys())
        for f in development_site_layer.getFeatures(request):
            for field in all_keys:
                try:
                    totals[field] += f[field]
                except KeyError:
                    pass

        totals["total_dwellings"] = (
            totals["count_1_bedroom_dwellings"]
            + totals["count_2_bedroom_dwellings"]
            + totals["count_3_bedroom_dwellings"]
            + totals["count_4_bedroom_dwellings"]
        )

        return totals


PROJECT_CONTROLLER = ProjectController(QgsProject.instance())
