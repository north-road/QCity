"""
QCity processing provider
"""

from qgis.core import QgsApplication, QgsProcessingProvider
from qcity.gui.gui_utils import GuiUtils

from .reassign_building_levels import ReassignBuildingLevelsAlgorithm
from .import_development_sites import ImportDevelopmentSitesAlgorithm


class QCityProcessingProvider(QgsProcessingProvider):
    """
    Processing provider for QCity algorithms
    """

    def __init__(self):
        super().__init__()
        self._algorithms = [
            ImportDevelopmentSitesAlgorithm,
            ReassignBuildingLevelsAlgorithm,
        ]

    def id(self) -> str:
        return "qcity"

    def name(self) -> str:
        return "QCity"

    def longName(self) -> str:
        return self.name()

    def icon(self):
        return GuiUtils.get_icon("plugin.svg")

    def svgIconPath(self):
        return GuiUtils.get_icon_svg("plugin.svg")

    def supportsNonFileBasedOutput(self):
        return True

    def loadAlgorithms(self) -> None:
        for algorithm in self._algorithms:
            self.addAlgorithm(algorithm())

    def unload(self) -> None:
        """
        Removes the provider from the processing registry
        """
        QgsApplication.processingRegistry().removeProvider(self)
