"""
QCity Processing widget wrappers
"""

from qgis.PyQt.QtWidgets import QComboBox

from qgis.core import Qgis, QgsProcessingParameterDefinition
from qgis.gui import (
    QgsAbstractProcessingParameterWidgetWrapper,
    QgsProcessingParameterWidgetFactoryInterface,
)


from qcity.core import (
    get_project_controller,
)


class QCityProjectAreaWidgetWrapper(QgsAbstractProcessingParameterWidgetWrapper):
    def __init__(
        self,
        parameter: QgsProcessingParameterDefinition,
        dialogType: Qgis.ProcessingMode,
    ):
        super().__init__(parameter, dialogType)
        self._combo: QComboBox | None = None

    def createWidget(self) -> QComboBox:

        controller = get_project_controller()
        project_area_layer = controller.get_project_area_layer()

        self._combo = QComboBox()
        self._combo.setToolTip(self.parameterDefinition().toolTip())

        if self.parameterDefinition().flags() & Qgis.ProcessingParameterFlag.Optional:
            self._combo.addItem(self.tr("Not set"), None)

        if project_area_layer and project_area_layer.isValid():
            name_to_id = {
                feature["name"]: feature.id()
                for feature in project_area_layer.getFeatures()
            }
            names_sorted = sorted(list(name_to_id.keys()), key=str.casefold)
            for name in names_sorted:
                self._combo.addItem(name, name_to_id[name])

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
