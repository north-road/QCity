"""
QCity processing provider
"""

from qgis.core import QgsApplication, QgsProcessingProvider

from qcity.processing.reassign_building_levels_algorithm import (
    ReassignBuildingLevelsAlgorithm,
)


class QCityProcessingProvider(QgsProcessingProvider):
    """
    Processing provider for QCity algorithms
    """

    def __init__(self):
        super().__init__()
        self._algorithms = [ReassignBuildingLevelsAlgorithm()]

    def id(self) -> str:
        return "qcity"

    def name(self) -> str:
        return "QCity"

    def longName(self) -> str:
        return self.name()

    def loadAlgorithms(self) -> None:
        for algorithm in self._algorithms:
            self.addAlgorithm(algorithm)

    def unload(self) -> None:
        """
        Removes the provider from the processing registry
        """
        QgsApplication.processingRegistry().removeProvider(self)
