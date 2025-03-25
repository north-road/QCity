"""
Settings manager
"""

import json
import os
from typing import Optional, List, Union

from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsSettings,
    QgsVectorLayer,
    QgsProject,
    QgsFeatureRequest,
)


class SettingsManager(QObject):
    """
    Manages plugin settings, and advises on changes
    """

    SETTINGS_KEY = "qcity"

    database_path_changed = pyqtSignal(str)
    add_feature_clicked = pyqtSignal(bool)
    spinbox_changed = pyqtSignal(tuple)
    current_project_area_parameter_name_changed = pyqtSignal(str)
    database_path_with_project_name_saved = pyqtSignal(dict)
    current_development_site_parameter_name_changed = pyqtSignal(str)
    current_building_level_parameter_name_changed = pyqtSignal(str)
    project_layer_ids_changed = pyqtSignal(tuple)

    plugin_path = os.path.dirname(os.path.realpath(__file__))
    project_area_prefix = "project_areas"
    development_site_prefix = "development_sites"
    building_level_prefix = "building_levels"
    current_digitisation_type: Optional[str] = None

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._current_building_level_parameter_table_name: Optional[str] = None
        self._current_development_site_parameter_table_name: Optional[str] = None
        self._current_project_area_parameter_table_name: Optional[str] = None
        self._database_path = None

        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self._default_project_area_parameters_path = os.path.join(
            self.plugin_path, "..", "data", "default_project_area_parameters.json"
        )
        self._default_project_development_site_path = os.path.join(
            self.plugin_path, "..", "data", "default_development_site_parameters.json"
        )
        self._default_project_building_level_path = os.path.join(
            self.plugin_path, "..", "data", "default_building_level_parameters.json"
        )

        self.project = QgsProject().instance()

    def get_base_layers_items(self) -> List[str]:
        """Returns a list of all project files in plugin project directory."""
        project_paths = list()

        for path in os.listdir(
            os.path.join(self.plugin_path, "..", "data", "projects")
        ):
            if path.endswith(".qgz"):
                project_paths.append(path.removesuffix(".qgz"))

        return project_paths

    def set_database_path(self, database_path: str) -> None:
        """
        Sets the current database path.
        """
        if database_path != self.get_database_path():
            self._database_path = database_path
            self.database_path_changed.emit(database_path)

    def get_database_path(self) -> QColor:
        """
        Get the current database path.
        """
        return self._database_path

    def save_widget_value_to_layer(
        self, widget: QWidget, value: Union[float, int, str], kind: str
    ):
        """
        Sets a spinbox value from the corresponding widget-value.
        """
        if kind == SETTINGS_MANAGER.project_area_prefix:
            feature_name = self._current_project_area_parameter_table_name
        elif kind == SETTINGS_MANAGER.development_site_prefix:
            feature_name = self._current_development_site_parameter_table_name
        elif kind == SETTINGS_MANAGER.building_level_prefix:
            feature_name = self._current_building_level_parameter_table_name

        if feature_name:
            gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={kind}"
            layer = QgsVectorLayer(gpkg_path, feature_name, "ogr")
            request = QgsFeatureRequest().setFilterExpression(
                f"\"name\" = '{feature_name}'"
            )
            iterator = layer.getFeatures(request)
            feature = next(iterator)

            layer.startEditing()
            if feature:
                feature[widget.objectName()] = value
                layer.updateFeature(feature)
                layer.commitChanges()
            else:
                layer.rollBack()

        self.spinbox_changed.emit((widget.objectName(), value))

    def set_current_project_area_feature_name(self, name: str) -> None:
        """
        Sets the current project area parameter table name.
        """
        self._current_project_area_parameter_table_name = name
        self.current_project_area_parameter_name_changed.emit(name)

    def set_current_development_site_feature_name(self, name: str) -> None:
        """
        Sets the current project area parameter table name.
        """
        self._current_development_site_parameter_table_name = name
        self.current_development_site_parameter_name_changed.emit(name)

    def set_current_building_level_feature_name(self, name: str) -> None:
        """
        Sets the current project area parameter table name.
        """
        self._current_building_level_parameter_table_name = name
        self.current_building_level_parameter_name_changed.emit(name)

    def save_database_path_with_project_name(self) -> None:
        """
        Saves the database path with the QGIS project name to the settings.
        """
        project_name = os.path.basename(self.project.fileName())

        if project_name:
            QgsSettings().setValue(
                f"{self.SETTINGS_KEY}/database_path_{project_name}",
                self._database_path,
                section=QgsSettings.Plugins,
            )

            self.database_path_with_project_name_saved.emit(
                {project_name: self._database_path}
            )

    def get_database_path_with_project_name(self) -> Optional[dict]:
        """
        Gets the database path with the QGIS project name from the settings.
        """
        project_name = os.path.basename(self.project.fileName())
        if project_name:
            database_path = QgsSettings().value(
                f"{self.SETTINGS_KEY}/database_path_{project_name}",
                section=QgsSettings.Plugins,
            )
            self.set_database_path(database_path)
            return database_path

    def get_attributes_from_json(self, kind: str) -> dict:
        """Gets the attributes of the default values from the json files"""
        if kind == "project_areas":
            json_path = self._default_project_area_parameters_path
        elif kind == "development_sites":
            json_path = self._default_project_development_site_path
        elif kind == "building_levels":
            json_path = self._default_project_building_level_path
        else:
            raise Exception(f"Unknown kind {kind}")

        with open(json_path, "r") as file:
            attributes = json.load(file)

        return attributes

    def set_project_layer_ids(
        self,
        area_layer: QgsVectorLayer,
        dev_site_layer: QgsVectorLayer,
        building_level_layer: QgsVectorLayer,
    ) -> None:
        self.area_layer_id = area_layer.id()
        self.dev_site_layer_id = dev_site_layer.id()
        self.building_level_layer_id = building_level_layer.id()

        self.project_layer_ids_changed.emit((area_layer.id(), dev_site_layer.id()))

    def get_project_area_layer_id(self) -> int:
        return self.area_layer_id

    def get_development_site_layer_id(self) -> int:
        return self.dev_site_layer_id

    def get_building_level_layer_id(self) -> int:
        return self.building_level_layer_id

    def restore_checkbox_state(self, checkbox, item) -> None:
        state = QgsSettings().value(
            f"{self.SETTINGS_KEY}/checkBoxState_{checkbox.objectName()}_{item.text()}",
            section=QgsSettings.Plugins,
        )
        if isinstance(state, bool):
            checkbox.setChecked(state)
        else:
            checkbox.setChecked(False)

    def save_checkbox_state(self, checkbox, item) -> None:
        QgsSettings().setValue(
            f"{self.SETTINGS_KEY}/checkBoxState_{checkbox.objectName()}_{item.text()}",
            checkbox.isChecked(),
            section=QgsSettings.Plugins,
        )

    def get_pk(self, kind: str) -> int:
        """Gets the primary key of the current feature."""

        if kind == self.development_site_prefix:
            gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={self.project_area_prefix}"
            name = self._current_project_area_parameter_table_name
        elif kind == self.building_level_prefix:
            name = self._current_development_site_parameter_table_name
            gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={self.development_site_prefix}"

        layer = QgsVectorLayer(gpkg_path, "", "ogr")

        request = QgsFeatureRequest().setFilterExpression(f"\"name\" = '{name}'")
        feat = next(layer.getFeatures(request))

        print(feat.id())

        return feat.id()


# Settings manager singleton instance
SETTINGS_MANAGER = SettingsManager()
