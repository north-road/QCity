from typing import List, Optional

from qgis.PyQt.QtCore import QObject, pyqtSignal

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRelation,
    QgsRelationContext,
    QgsFeature,
    QgsFeatureRequest,
    QgsExpression
)

from .settings import SETTINGS_MANAGER
from .enums import LayerType
from .database import DatabaseUtils

class ProjectController(QObject):
    """
    Controller for working with QCity projects
    """

    project_area_changed = pyqtSignal(int)
    development_site_changed = pyqtSignal(int)
    project_area_added = pyqtSignal(QgsFeature)
    development_site_added = pyqtSignal(QgsFeature)
    building_level_added = pyqtSignal(QgsFeature)

    def __init__(self, project: QgsProject):
        super().__init__()
        self.project = project
        self.current_project_area_fid: Optional[int] = None
        self.current_development_site_fid: Optional[int] = None

        self.connect_layers()

        self.project.layersAdded.connect(self._update_project_layers)
        self.project.layersRemoved.connect(self._update_project_layers)

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
        if project_area_layer:
            if disconnect:
                project_area_layer.featureAdded.disconnect(self._project_area_added)
            else:
                project_area_layer.featureAdded.connect(self._project_area_added)

        development_site_layers = self.get_development_sites_layer()
        if development_site_layers:
            if disconnect:
                development_site_layers.featureAdded.disconnect(self._development_site_added)
            else:
                development_site_layers.featureAdded.connect(self._development_site_added)

        building_levels_layer = self.get_building_levels_layer()
        if building_levels_layer:
            if disconnect:
                building_levels_layer.featureAdded.disconnect(self._building_level_added)
            else:
                building_levels_layer.featureAdded.connect(self._building_level_added)

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

    @staticmethod
    def add_database_layers_to_project(project: QgsProject, database_path: str) -> None:
        """Adds the layers from the gpkg to the canvas"""
        area_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.project_area_prefix}",
            SETTINGS_MANAGER.project_area_prefix,
            "ogr",
        )
        assert area_layer.isValid()
        area_layer.setCustomProperty('_qcity_role', 'project_areas')

        development_site_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.development_site_prefix}",
            SETTINGS_MANAGER.development_site_prefix,
            "ogr",
        )
        assert development_site_layer.isValid()
        development_site_layer.setCustomProperty('_qcity_role', 'development_sites')

        building_level_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.building_level_prefix}",
            SETTINGS_MANAGER.building_level_prefix,
            "ogr",
        )
        assert building_level_layer.isValid()
        building_level_layer.setCustomProperty('_qcity_role', 'building_levels')

        project.addMapLayers([area_layer, development_site_layer, building_level_layer])

    def get_project_area_layer(self) -> Optional[QgsVectorLayer]:
        """
        Retrieves the project area layer from a project
        """
        for _, layer in self.project.mapLayers().items():
            if layer.customProperty('_qcity_role') == 'project_areas':
                return layer

        return None

    def get_development_sites_layer(self) -> Optional[QgsVectorLayer]:
        """
        Retrieves the development sites layer from a project
        """
        for _, layer in self.project.mapLayers().items():
            if layer.customProperty('_qcity_role') == 'development_sites':
                return layer

        return None

    def get_building_levels_layer(self) -> Optional[QgsVectorLayer]:
        """
        Retrieves the building levels layer from a project
        """
        for _, layer in self.project.mapLayers().items():
            if layer.customProperty('_qcity_role') == 'building_levels':
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

    def get_unique_names(self, layer: LayerType) -> List[str]:
        """
        Gets a list of all existing unique names for the specified layer type,
        sorted alphabetically.
        """
        map_layer = self.get_layer(layer)
        return sorted(map_layer.uniqueValues(map_layer.fields().lookupField(
            DatabaseUtils.name_field_for_layer(layer)
        )), key=str.casefold)

    def create_layer_relations(self):
        """Adds relations between layers to the QGIS project."""
        relation_manager = self.project.relationManager()
        existing_relations = {rel.name() for rel in relation_manager.relations().values()}

        if "project_area_to_development_sites" in existing_relations and "development_sites_to_building_levels" in existing_relations:
            return

        project_area_layer = self.get_project_area_layer()
        development_site_layer = self.get_development_sites_layer()
        building_level_layer = self.get_building_levels_layer()
        if not project_area_layer or not development_site_layer or not building_level_layer:
            return

        relations = [
            ("project_area_to_development_sites", project_area_layer, development_site_layer, "project_area_pk"),
            ("development_sites_to_building_levels", development_site_layer, building_level_layer, "development_site_pk"),
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
        self.project.writeEntry('qcity', 'database_path', path)

    def associated_database_path(self) -> str:
        """
        Returns the database path associated with a project
        """
        return self.project.readEntry('qcity', 'database_path')[0]

    def set_current_project_area(self, project_area_fid: int):
        """
        Sets the feature ID for the current project area
        """
        self.current_project_area_fid = project_area_fid
        self.project_area_changed.emit(self.current_project_area_fid)

    def set_current_development_site(self, development_site_fid: int):
        """
        Sets the feature ID for the current development site
        """
        self.current_development_site_fid = development_site_fid
        self.development_site_changed.emit(self.current_development_site_fid)

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

        project_area_primary_key = project_area_feature[DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas)]

        # find matching development sites
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites),
                                                        project_area_primary_key)
        )
        development_site_layer = self.get_development_sites_layer()
        development_site_features = [f for f in development_site_layer.getFeatures(request)]

        # find matching building levels
        development_site_primary_keys = [
            f[DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)] for f in development_site_features
        ]
        building_levels_filter = '{} IN ({})'.format(
            DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels),
            ','.join([str(k) for k in development_site_primary_keys])
        )
        request = QgsFeatureRequest().setFilterExpression(
            building_levels_filter
        )
        building_level_layer = self.get_building_levels_layer()
        building_level_features = [f for f in building_level_layer.getFeatures(request)]

        if not building_level_layer.startEditing():
            return False
        if not building_level_layer.deleteFeatures([f.id() for f in building_level_features]):
            return False

        if not development_site_layer.startEditing():
            return False
        if not development_site_layer.deleteFeatures([f.id() for f in development_site_features]):
            return False

        if not project_area_layer.startEditing():
            return False
        if not project_area_layer.deleteFeature(project_area_fid):
            return False

        # only commit if ALL layer edits were successful
        building_level_layer.commitChanges()
        development_site_layer.commitChanges()
        project_area_layer.commitChanges()
        return True

    def delete_development_site(self, development_site_fid: int) -> bool:
        """
        Deletes the specified development site, and all child objects
        """
        development_site_layer = self.get_development_sites_layer()
        if not development_site_layer:
            return False

        development_site_feature = development_site_layer.getFeature(development_site_fid)
        if not development_site_feature.isValid():
            return False

        development_site_primary_key = development_site_feature[DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)]

        # find matching building levels
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels),
                                                        development_site_primary_key)
        )
        building_level_layer = self.get_building_levels_layer()
        building_level_features = [f for f in building_level_layer.getFeatures(request)]

        if not building_level_layer.startEditing():
            return False
        if not building_level_layer.deleteFeatures([f.id() for f in building_level_features]):
            return False

        if not development_site_layer.startEditing():
            return False
        if not development_site_layer.deleteFeature(development_site_fid):
            return False

        # only commit if ALL layer edits were successful
        building_level_layer.commitChanges()
        development_site_layer.commitChanges()
        return True


PROJECT_CONTROLLER = ProjectController(QgsProject.instance())