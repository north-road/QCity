"""
Processing algorithm to reassign building levels to the development site
which they overlap the most.
"""

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsCoordinateTransform,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterVectorLayer,
    QgsSpatialIndex,
)

from qcity.core import (
    DatabaseUtils,
    LayerType,
)
from qcity.core.utils import wrapped_edits
from .qcity_algorithm import QCityAlgorithm
from .parameters import QCityProjectAreaParameterDefinition


class ReassignBuildingLevelsAlgorithm(QCityAlgorithm):
    """
    Reassigns building levels to the development site they overlap most
    """

    INPUT = "INPUT"
    ONLY_SELECTED = "ONLY_SELECTED"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "reassignbuildinglevels"

    def displayName(self) -> str:
        return self.tr("Reassign building levels")

    def shortDescription(self) -> str:
        return self.tr(
            "Reassigns building levels to the development sites that are positioned below them."
        )

    def shortHelpString(self) -> str:
        return self.tr("")

    def initAlgorithm(self, config=None) -> None:
        project_area_param = QCityProjectAreaParameterDefinition(
            self.INPUT, self.tr("Only reassign to development sites in"), optional=True
        )
        project_area_param.setHelp(
            self.tr(
                "If set, building levels will only be assigned to development sites that are within the selected project area."
            )
        )

        self.addParameter(project_area_param)

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ONLY_SELECTED,
                self.tr("Only reassign selected building levels"),
                defaultValue=False,
            )
        )
        self.addOutput(
            QgsProcessingOutputVectorLayer(self.OUTPUT, self.tr("Updated layer"))
        )

    def processAlgorithm(
        self,
        parameters,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):

        return {}
