"""
QCity Processing parameter types
"""

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    Qgis,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterType,
    QgsProcessingParameterString,
    QgsProcessingOutputString,
)


class QCityProjectAreaParameterDefinition(QgsProcessingParameterDefinition):
    def __init__(
        self,
        name: str,
        description: str = "",
        defaultValue=None,
        optional: bool = False,
        help: str = "",
    ):
        super().__init__(name, description, defaultValue, optional, help)

    def clone(self):
        copy = QCityProjectAreaParameterDefinition(
            self.name(),
            self.description(),
            self.defaultValue(),
            bool(self.flags() & Qgis.ProcessingParameterFlag.Optional),
            self.help(),
        )
        copy.setFlags(self.flags())
        copy.setMetadata(self.metadata())
        return copy

    @staticmethod
    def typeName() -> str:
        return "projectarea"

    def type(self) -> str:
        return self.typeName()

    def checkValueIsAcceptable(self, input_val, context=None) -> bool:
        if input_val is None or input_val == "":
            return bool(self.flags() & Qgis.ProcessingParameterFlag.Optional)
        return True

    def valueAsPythonString(self, value, context) -> str:
        return repr(str(value)) if value is not None else "None"


class QCityProjectAreaParameterType(QgsProcessingParameterType):
    def tr(self, string, context=""):
        if context == "":
            context = self.__class__.__name__
        return QCoreApplication.translate(context, string)

    def create(self, name: str) -> QgsProcessingParameterDefinition:
        return QCityProjectAreaParameterDefinition(name)

    def description(self) -> str:
        return self.tr("A parameter which allows selection of a QCity project area")

    def name(self) -> str:
        return self.tr("QCity Project Area")

    def id(self) -> str:
        return "projectarea"

    def className(self) -> str:
        return "QCityProjectAreaParameterDefinition"

    def acceptedPythonTypes(self) -> list[str]:
        return ["str"]

    def acceptedParameterTypes(self) -> list[str]:
        return ["projectarea", QgsProcessingParameterString.typeName()]

    def acceptedOutputTypes(self) -> list[str]:
        return [QgsProcessingOutputString.typeName()]
