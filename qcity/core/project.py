from typing import Optional

from qgis.PyQt.QtCore import QObject, pyqtSignal

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRelation,
    QgsRelationContext
)

from .settings import SETTINGS_MANAGER
from .enums import LayerType

class ProjectController(QObject):
    """
    Controller for working with QCity projects
    """

    project_area_changed = pyqtSignal(int)

    def __init__(self, project: QgsProject):
        super().__init__()
        self.project = project
        self.current_project_area_fid: Optional[int] = None

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


PROJECT_CONTROLLER = ProjectController(QgsProject.instance())