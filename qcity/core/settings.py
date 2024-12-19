"""
Settings manager
"""

import os
from typing import Optional, List

from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt import sip
from qgis._core import QgsVectorFileWriter

from qgis.core import (
    Qgis,
    QgsSettings,
    QgsSymbolLayerUtils,
    QgsUnitTypes,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProject,
    QgsMapLayer,
)


class SettingsManager(QObject):
    """
    Manages plugin settings, and advises on changes
    """

    SETTINGS_KEY = "qcity"

    database_path_changed = pyqtSignal(str)
    add_project_area_clicked = pyqtSignal(bool)

    plugin_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
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
            name = area.split('!!::!!')[1]
            areas.append(name)
        return areas


# Settings manager singleton instance
SETTINGS_MANAGER = SettingsManager()
