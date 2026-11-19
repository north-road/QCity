import json
import os
from typing import Optional, Dict

from qgis.PyQt.QtCore import QVariant, QDate
from qgis.core import (
    Qgis,
    QgsFields,
    QgsField,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
    QgsMemoryProviderUtils,
    QgsCoordinateReferenceSystem,
    QgsProviderRegistry,
    QgsProject,
    QgsProviderSublayerDetails,
    QgsCoordinateTransform,
)

from .enums import LayerType
from .settings import SETTINGS_MANAGER


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
    def qvariant_type_from_string(key: str) -> "QVariant.Type":
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

        default_crs = SETTINGS_MANAGER.default_database_crs()

        layer = QgsMemoryProviderUtils.createMemoryLayer(
            table_name, fields, Qgis.WkbType.MultiPolygon, default_crs
        )

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = table_name
        options.actionOnExistingFile = (
            QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer
            if not create_file
            else QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
        )

        error, error_message, new_filename, new_layer = (
            QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, gpkg_path, QgsCoordinateTransformContext(), options
            )
        )

        if not error == QgsVectorFileWriter.WriterError.NoError:
            raise Exception(
                f"Error adding layer to GeoPackage {gpkg_path}: {error_message}"
            )

    @staticmethod
    def upgrade_table(layer: QgsVectorLayer, layer_type: LayerType):
        """
        Upgrades the definition of a table to match current plugin version
        requirements
        """
        from .layer import wrapped_edits

        if layer_type == LayerType.DevelopmentSites:
            has_base_height_field = layer.fields().lookupField("base_height") >= 0
            if not has_base_height_field:
                with wrapped_edits(layer) as edits:
                    edits.addAttribute(QgsField("base_height", QVariant.Double))

    @staticmethod
    def copy_reprojected_geopackage(
        source_gpkg: str | os.PathLike,
        target_gpkg: str | os.PathLike,
        target_crs: QgsCoordinateReferenceSystem,
    ) -> None:
        """
        Copies all vector tables from an existing GeoPackage into a new GeoPackage,

        reprojecting every layer to a new CRS
        """
        source_path = os.fspath(source_gpkg)
        target_path = os.fspath(target_gpkg)

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source GeoPackage not found: {source_path}")

        if os.path.abspath(source_path) == os.path.abspath(target_path):
            raise ValueError("Target GeoPackage path must differ from source path.")

        sublayer_details = QgsProviderRegistry.instance().querySublayers(source_path)
        if not sublayer_details:
            raise RuntimeError(f"No sublayers found in GeoPackage: {source_path}")

        target_dir = os.path.dirname(os.path.abspath(target_path))
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        if os.path.exists(target_path):
            os.remove(target_path)

        transform_context = QgsProject.instance().transformContext()
        layer_options = QgsProviderSublayerDetails.LayerOptions(transform_context)
        file_exists = False

        for details in sublayer_details:
            if details.type() != Qgis.LayerType.Vector:
                continue

            layer_name = details.name()
            map_layer = details.toLayer(layer_options)
            if not isinstance(map_layer, QgsVectorLayer) or not map_layer.isValid():
                raise RuntimeError(
                    f"Failed to load vector sublayer '{layer_name}' from {source_path}"
                )

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"
            options.fileEncoding = map_layer.dataProvider().encoding() or "UTF-8"
            options.ct = QgsCoordinateTransform(
                map_layer.crs(), target_crs, QgsProject.instance()
            )
            options.layerName = layer_name

            if not file_exists:
                options.actionOnExistingFile = (
                    QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
                )
            else:
                options.actionOnExistingFile = (
                    QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer
                )

            error, error_msg, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer=map_layer,
                fileName=target_path,
                transformContext=transform_context,
                options=options,
            )

            if error != QgsVectorFileWriter.WriterError.NoError:
                raise RuntimeError(
                    f"Failed to write reprojected layer '{layer_name}' to {target_path}: {error_msg}"
                )

            file_exists = True

        if not file_exists:
            raise RuntimeError(f"No vector layers found in GeoPackage: {source_path}")
