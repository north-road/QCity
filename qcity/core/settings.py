"""
Settings manager
"""

import json
import os
from typing import Optional, List, Union

from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import QObject, pyqtSignal, QDir
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
    database_path_with_project_name_saved = pyqtSignal(dict)

    plugin_path = os.path.dirname(os.path.realpath(__file__))
    project_area_prefix = "project_areas"
    development_site_prefix = "development_sites"
    building_level_prefix = "building_levels"

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
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
        project_folder = os.path.join(self.plugin_path, "..", "data", "projects")

        for path in os.listdir(project_folder):
            if path.lower().endswith(".qgz") or path.lower().endswith(".qgs"):
                project_paths.append(project_folder + '/' + path)

        return project_paths

    def set_last_used_database_folder(self, folder: str):
        """
        Sets the last used database folder
        """
        QgsSettings().setValue(
            f"{self.SETTINGS_KEY}/last_used_database_folder",
            folder,
            section=QgsSettings.Plugins,
        )

    def last_used_database_folder(self) -> str:
        """
        Returns the last used database folder
        """
        return QgsSettings().value(
            f"{self.SETTINGS_KEY}/last_used_database_folder",
            QDir.homePath(), section=QgsSettings.Plugins
        )

    def set_last_used_export_path(self, path: str):
        """
        Sets the last used export path
        """
        QgsSettings().setValue(
            f"{self.SETTINGS_KEY}/last_used_export_path",
            path,
            section=QgsSettings.Plugins,
        )

    def last_used_export_path(self) -> str:
        """
        Returns the last used export path
        """
        return QgsSettings().value(
            f"{self.SETTINGS_KEY}/last_used_export_path",
            QDir.homePath(), section=QgsSettings.Plugins
        )

    def set_database_path(self, database_path: str) -> None:
        """
        Sets the current database path.
        """
        if database_path != self._database_path:
            self._database_path = database_path
            self.database_path_changed.emit(database_path)

    def get_database_path(self) -> QColor:
        """
        Get the current database path.
        """
        return self._database_path

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


# Settings manager singleton instance
SETTINGS_MANAGER = SettingsManager()
