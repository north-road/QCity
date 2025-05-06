import json

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsFields,
    QgsField,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsCoordinateTransformContext
)

from .settings import SETTINGS_MANAGER


class DatabaseUtils:
    """
    Utilities for working with QCity databases
    """

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
            create_file=True
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
    def create_base_table(gpkg_path: str,
                          table_name: str,
                          json_config_path: str,
                          create_file: bool = False) -> None:
        """Creates a GeoPackage layer with attributes based on JSON data."""
        with open(json_config_path, "r") as file:
            data = json.load(file)

        fields = QgsFields()
        fields.append(QgsField("name", QVariant.String))
        for field_name, config in data.items():
            fields.append(QgsField(field_name, DatabaseUtils.qvariant_type_from_string(config['type'])))

        layer = QgsVectorLayer("Polygon?crs=EPSG:7844", table_name, "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = table_name
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer if not create_file else QgsVectorFileWriter.CreateOrOverwriteFile

        error, error_message, new_filename, new_layer = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer, gpkg_path, QgsCoordinateTransformContext(), options
        )

        if not error == QgsVectorFileWriter.NoError:
            raise Exception(f"Error adding layer to GeoPackage {gpkg_path}: {error_message}")
