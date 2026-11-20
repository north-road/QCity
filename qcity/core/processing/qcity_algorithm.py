"""
Base class for QCity Processing algorithms
"""

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsProcessingAlgorithm,
)

from qcity.gui.gui_utils import GuiUtils


class QCityAlgorithm(QgsProcessingAlgorithm):
    def __init__(self):
        super().__init__()

    def tr(self, string, context=""):
        if context == "":
            context = self.__class__.__name__
        return QCoreApplication.translate(context, string)

    def createInstance(self):
        return type(self)()

    def icon(self):
        return GuiUtils.get_icon("plugin.svg")

    def svgIconPath(self):
        return GuiUtils.get_icon_svg("plugin.svg")
