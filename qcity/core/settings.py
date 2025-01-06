"""
Settings manager
"""

import os
from typing import Optional, List, Union

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor
import sqlite3

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

    plugin_path = os.path.dirname(os.path.realpath(__file__))
    area_parameter_prefix = "project_area_parameters_"

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._current_project_area_parameter_table_name: Optional[str] = None
        self._database_path = None

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
            QgsSettings().setValue(
                f"{self.SETTINGS_KEY}/database_path",
                database_path,
                section=QgsSettings.Plugins,
            )
            self.database_path_changed.emit(database_path)

    def get_database_path(self) -> QColor:
        """
        Get the current database path.
        """
        return self._database_path

    def get_project_areas_items(self):
        """Returns a list of all project areas in database."""
        layer = QgsVectorLayer(self._database_path, "database", "ogr")
        layers = layer.dataProvider().subLayers()
        areas = list()
        for area in layers:
            name = area.split("!!::!!")[1]
            areas.append(name)
        return areas

    def set_spinbox_value(self, widget, value):
        """
        Sets a spinbox value from the corresponding widget-value.
        """
        conn = sqlite3.connect(self._database_path)
        cursor = conn.cursor()

        try:
            if self._current_project_area_parameter_table_name:
                cursor.execute(
                    f"DELETE FROM {self._current_project_area_parameter_table_name} where widget_name = '{widget.objectName()}';"
                )
                cursor.execute(
                    f"INSERT INTO {self._current_project_area_parameter_table_name} (widget_name, value) VALUES ('{widget.objectName()}', {value});"
                )
                conn.commit()

        except Exception as e:
            print(e)
            pass

        finally:
            cursor.close()
            conn.close()
        self.spinbox_changed.emit((widget.objectName(), value))

    def get_spinbox_value_from_database(
        self, widget: QWidget
    ) -> Optional[Union[int, float]]:
        """
        Returns the value corresponding to the given widget name from the database.
        """
        query = f"SELECT value FROM {self._current_project_area_parameter_table_name} WHERE widget_name = '{widget.objectName()}';"

        conn = sqlite3.connect(self._database_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                if isinstance(widget, QSpinBox):
                    return int(result[0])
                elif isinstance(widget, QDoubleSpinBox):
                    return result[0]
            else:
                print("No matching row found.")
        finally:
            # Clean up
            cursor.close()
            conn.close()

    def set_current_project_area_parameter_table_name(self, name: str) -> None:
        """
        Sets the current project area parameter table name.
        """
        self._current_project_area_parameter_table_name = name
        self.current_project_area_parameter_name_changed.emit(name)

    def get_current_project_area_parameter_table_name(self) -> str:
        """
        Returns the current project area parameter table name.
        """
        return self._current_project_area_parameter_table_name


# Settings manager singleton instance
SETTINGS_MANAGER = SettingsManager()
