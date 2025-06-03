import json
from typing import Optional, Dict

from qgis.PyQt.QtCore import QVariant, QDate
from qgis.core import (
    QgsFields,
    QgsField,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
    QgsProject,
)

from .settings import SETTINGS_MANAGER
from .enums import LayerType


class DatabaseUtils:
    """
    Utilities for working with QCity databases
    """

    @staticmethod
    def primary_key_for_layer(layer: LayerType) -> str:
        """
        Returns the primary key field name for the given layer
        """
        return {
            LayerType.ProjectAreas: "fid",
            LayerType.DevelopmentSites: "fid",
            LayerType.BuildingLevels: "fid",
        }[layer]

    @staticmethod
    def foreign_key_for_layer(layer: LayerType) -> Optional[str]:
        """
        Returns the foreign key field name for the given layer
        """
        return {
            LayerType.ProjectAreas: None,
            LayerType.DevelopmentSites: "project_area_pk",
            LayerType.BuildingLevels: "development_site_pk",
        }[layer]

    @staticmethod
    def name_field_for_layer(layer: LayerType) -> Optional[str]:
        """
        Returns the "name" field for the given layer
        """
        return {
            LayerType.ProjectAreas: "name",
            LayerType.DevelopmentSites: "name",
            LayerType.BuildingLevels: "name",
        }[layer]

    @staticmethod
    def qvariant_type_from_string(key: str) -> QVariant.Type:
        """
        Returns the QVariant.Type corresponding to a config string value
        """
        return {
            "int": QVariant.Int,
            "double": QVariant.Double,
            "string": QVariant.String,
            "date": QVariant.Date,
            "value_map": QVariant.String,
            "bool": QVariant.Bool,
        }[key]

    @staticmethod
    def create_base_tables(gpkg_path: str):
        """
        Creates all base database tables
        """
        DatabaseUtils.create_base_table(
            gpkg_path,
            SETTINGS_MANAGER.project_area_prefix,
            SETTINGS_MANAGER._default_project_area_parameters_path,
            create_file=True,
        )
        DatabaseUtils.create_base_table(
            gpkg_path,
            SETTINGS_MANAGER.development_site_prefix,
            SETTINGS_MANAGER._default_project_development_site_path,
        )
        DatabaseUtils.create_base_table(
            gpkg_path,
            SETTINGS_MANAGER.building_level_prefix,
            SETTINGS_MANAGER._default_project_building_level_path,
        )

    @staticmethod
    def get_field_config(layer: LayerType, field_name: str) -> Optional[Dict]:
        """
        Returns the field config for the given field
        """
        if layer == LayerType.ProjectAreas:
            config_path = SETTINGS_MANAGER._default_project_area_parameters_path
        elif layer == LayerType.DevelopmentSites:
            config_path = SETTINGS_MANAGER._default_project_development_site_path
        elif layer == LayerType.BuildingLevels:
            config_path = SETTINGS_MANAGER._default_project_building_level_path
        else:
            assert False

        with open(config_path, "r") as file:
            data = json.load(file)

        return data.get(field_name)

    @staticmethod
    def get_field_default(layer: LayerType, field_name: str):
        """
        Returns the default value for the given field
        """
        # special handling!
        if field_name == "date":
            return QDate.currentDate().year()

        config = DatabaseUtils.get_field_config(layer, field_name)
        if config is None:
            return None

        return config.get("default")

    @staticmethod
    def create_base_table(
        gpkg_path: str,
        table_name: str,
        json_config_path: str,
        create_file: bool = False,
    ) -> None:
        """Creates a GeoPackage layer with attributes based on JSON data."""
        with open(json_config_path, "r") as file:
            data = json.load(file)

        fields = QgsFields()
        fields.append(QgsField("name", QVariant.String))
        for field_name, config in data.items():
            fields.append(
                QgsField(
                    field_name, DatabaseUtils.qvariant_type_from_string(config["type"])
                )
            )

        layer = QgsVectorLayer("Polygon?crs=EPSG:7844", table_name, "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = table_name
        options.actionOnExistingFile = (
            QgsVectorFileWriter.CreateOrOverwriteLayer
            if not create_file
            else QgsVectorFileWriter.CreateOrOverwriteFile
        )

        error, error_message, new_filename, new_layer = (
            QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, gpkg_path, QgsCoordinateTransformContext(), options
            )
        )

        if not error == QgsVectorFileWriter.NoError:
            raise Exception(
                f"Error adding layer to GeoPackage {gpkg_path}: {error_message}"
            )
