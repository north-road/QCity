from qgis.core import QgsApplication

from .provider import QCityProcessingProvider
from .parameters import QCityProjectAreaParameterType


class QCityProcessingImpl:
    def __init__(self):
        self._project_area_param_type = QCityProjectAreaParameterType()
        QgsApplication.processingRegistry().addParameterType(
            self._project_area_param_type
        )

        self._provider = QCityProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self._provider)

    def __del__(self):
        QgsApplication.processingRegistry().removeProvider(self._provider)

        QgsApplication.processingRegistry().removeParameterType(
            self._project_area_param_type
        )
        self._project_area_param_type = None
