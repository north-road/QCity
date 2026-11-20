from qgis.gui import QgsGui

from .wrappers import QCityProjectAreaWidgetFactory


class QCityProcessingGuiImpl:
    def __init__(self):
        self._project_area_widget_factory = QCityProjectAreaWidgetFactory()
        QgsGui.processingGuiRegistry().addParameterWidgetFactory(
            self._project_area_widget_factory
        )

    def __del__(self):
        QgsGui.processingGuiRegistry().removeParameterWidgetFactory(
            self._project_area_widget_factory
        )
        self._project_area_widget_factory = None
