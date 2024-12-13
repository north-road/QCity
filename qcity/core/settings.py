"""
Settings manager
"""
import os
from typing import Optional, List

from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt import sip

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

    plugin_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    def get_base_layers_items(self) -> List[str]:
        """ Returns a list of all project files in plugin project directory."""
        project_paths = list()

        for path in os.listdir(os.path.join(self.plugin_path, "..", "data", "projects")):
            if path.endswith(".qgz"):
                project_paths.append(path.removesuffix(".qgz"))

        return project_paths




# Settings manager singleton instance
SETTINGS_MANAGER = SettingsManager()
