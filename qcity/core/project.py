from typing import Optional
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRelation,
    QgsRelationContext
)
from .settings import SETTINGS_MANAGER


class ProjectUtils:
    """
    Contains utility functions for working with QCity projects
    """

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

    @staticmethod
    def get_project_area_layer(project: QgsProject) -> Optional[QgsVectorLayer]:
        """
        Retrieves the project area layer from a project
        """
        for _, layer in project.mapLayers().items():
            if layer.customProperty('_qcity_role') == 'project_areas':
                return layer

        return None

    @staticmethod
    def get_development_sites_layer(project: QgsProject) -> Optional[QgsVectorLayer]:
        """
        Retrieves the development sites layer from a project
        """
        for _, layer in project.mapLayers().items():
            if layer.customProperty('_qcity_role') == 'development_sites':
                return layer

        return None

    @staticmethod
    def get_building_levels_layer(project: QgsProject) -> Optional[QgsVectorLayer]:
        """
        Retrieves the building levels layer from a project
        """
        for _, layer in project.mapLayers().items():
            if layer.customProperty('_qcity_role') == 'building_levels':
                return layer

        return None

    @staticmethod
    def create_layer_relations(project: QgsProject):
        """Adds relations between layers to the QGIS project."""
        relation_manager = project.relationManager()
        existing_relations = {rel.name() for rel in relation_manager.relations().values()}

        if "project_area_to_development_sites" in existing_relations and "development_sites_to_building_levels" in existing_relations:
            return

        project_area_layer = ProjectUtils.get_project_area_layer(project)
        development_site_layer = ProjectUtils.get_development_sites_layer(project)
        building_level_layer = ProjectUtils.get_building_levels_layer(project)
        if not project_area_layer or not development_site_layer or not building_level_layer:
            return

        relations = [
            ("project_area_to_development_sites", project_area_layer, development_site_layer, "project_area_pk"),
            ("development_sites_to_building_levels", development_site_layer, building_level_layer, "development_site_pk"),
        ]

        context = QgsRelationContext(project)
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

    @staticmethod
    def set_associated_database_path(project: QgsProject, path: str):
        """
        Sets the database path which is associated with a project
        """
        project.writeEntry('qcity', 'database_path', path)

    @staticmethod
    def associated_database_path(project: QgsProject) -> str:
        """
        Returns the database path associated with a project
        """
        return project.readEntry('qcity', 'database_path')[0]

