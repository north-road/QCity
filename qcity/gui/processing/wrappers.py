"""
QCity Processing widget wrappers
"""

from qgis.PyQt.QtWidgets import QComboBox

from qgis.core import Qgis, QgsProcessingParameterDefinition
from qgis.gui import (
    QgsAbstractProcessingParameterWidgetWrapper,
    QgsProcessingParameterWidgetFactoryInterface,
)


class QCityProjectAreaWidgetWrapper(QgsAbstractProcessingParameterWidgetWrapper):
    ITEMS = ["a", "b", "c"]

    def __init__(
        self,
        parameter: QgsProcessingParameterDefinition,
        dialogType: Qgis.ProcessingMode,
    ):
        super().__init__(parameter, dialogType)
        self._combo: QComboBox | None = None

    def createWidget(self) -> QComboBox:
        self._combo = QComboBox()
        self._combo.addItems(self.ITEMS)
        self._combo.currentIndexChanged.connect(
            lambda: self.widgetValueHasChanged.emit(self)
        )
        return self._combo

    def setWidgetValue(self, value, context):
        if not self._combo:
            return
        idx = self._combo.findText(str(value))
        if idx >= 0:
            self._combo.setCurrentIndex(idx)

    def widgetValue(self):
        return self._combo.currentText() if self._combo else None


class QCityProjectAreaWidgetFactory(QgsProcessingParameterWidgetFactoryInterface):
    def parameterType(self) -> str:
        return "projectarea"

    def createWidgetWrapper(
        self,
        parameter: QgsProcessingParameterDefinition,
        dialogType: Qgis.ProcessingMode,
    ) -> QgsAbstractProcessingParameterWidgetWrapper:
        return QCityProjectAreaWidgetWrapper(parameter, dialogType)
