"""
Settings manager
"""

import os
from typing import Optional, List, Union

from qgis.PyQt.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor
import sqlite3

from qgis._core import QgsProject
from qgis.core import (
    QgsSettings,
    QgsVectorLayer,
)


class SettingsManager(QObject):
    """
    Manages plugin settings, and advises on changes
    """

    SETTINGS_KEY = "qcity"

    database_path_changed = pyqtSignal(str)
    add_project_area_clicked = pyqtSignal(bool)
    spinbox_changed = pyqtSignal(tuple)
    current_project_area_parameter_name_changed = pyqtSignal(str)
    database_path_with_project_name_saved = pyqtSignal(dict)
    current_development_site_parameter_name_changed = pyqtSignal(str)

    plugin_path = os.path.dirname(os.path.realpath(__file__))
    area_parameter_prefix = "project_area_parameters_"
    area_prefix = "project_areas"
    development_site_parameter_prefix = "development_site_parameters_"
    development_site_prefix = "development_sites"

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
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

    def get_project_items(self):
        """Returns a list of all project areas in database."""
        layer = QgsVectorLayer(self._database_path, "database", "ogr")
        layers = layer.dataProvider().subLayers()
        areas = list()
        for area in layers:
            name = area.split("!!::!!")[1]
            areas.append(name)
        return areas

    def save_widget_value_to_settings(
        self, widget: QWidget, value: Union[float, int, str], tab: str
    ):
        """
        Sets a spinbox value from the corresponding widget-value.
        """
        try:
            if tab == "project_areas":
                table_name = self._current_project_area_parameter_table_name
                prefix = self.area_parameter_prefix
            elif tab == "development_sites":
                table_name = self._current_development_site_parameter_table_name
                prefix = self.development_site_parameter_prefix

            if isinstance(value, Union[float, int]):
                col = "value_float"
            elif isinstance(value, str):
                col = "value_string"
            elif isinstance(value, bool):
                col = "value_bool"

            if table_name:
                with sqlite3.connect(self._database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"DELETE FROM {prefix}{table_name} where widget_name = '{widget.objectName()}';"
                    )
                    sql = f"INSERT INTO {prefix}{table_name} (widget_name, {col}) VALUES (?, ?)"
                    params = (widget.objectName(), value)
                    cursor.execute(sql, params)
                    conn.commit()

        except Exception as e:
            raise e

        self.spinbox_changed.emit((widget.objectName(), value))

    def get_spinbox_value_from_database(
        self, widget: QWidget
    ) -> Optional[Union[int, float]]:
        """
        Returns the value corresponding to the given widget name from the database.
        """
        try:
            with sqlite3.connect(self._database_path) as conn:
                cursor = conn.cursor()

                query = f"SELECT value FROM {self.area_parameter_prefix}{self._current_project_area_parameter_table_name} WHERE widget_name = '{widget.objectName()}';"
                cursor.execute(query)
                result = cursor.fetchone()

                if result:
                    if isinstance(widget, QSpinBox):
                        return int(result[0])
                    elif isinstance(widget, QDoubleSpinBox):
                        return result[0]
                else:
                    print("No matching row found.")
        except Exception as e:
            raise e

    def set_current_project_area_parameter_table_name(self, name: str) -> None:
        """
        Sets the current project area parameter table name.
        """
        self._current_project_area_parameter_table_name = name
        self.current_project_area_parameter_name_changed.emit(name)

    def set_current_development_site_parameter_table_name(self, name: str) -> None:
        """
        Sets the current project area parameter table name.
        """
        self._current_development_site_parameter_table_name = name
        self.current_development_site_parameter_name_changed.emit(name)

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


# Settings manager singleton instance
SETTINGS_MANAGER = SettingsManager()
