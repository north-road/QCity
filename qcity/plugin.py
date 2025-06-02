from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject

from .core import PROJECT_CONTROLLER
from qcity.gui.maptools import DrawPolygonTool, MapToolHandler

from .gui.gui_utils import GuiUtils
from .gui.qcity_dock import (
    QCityDockWidget,
)


class QCityPlugin:

    def __init__(self, iface):
        self.dlg_config = None
        self.iface = iface
        self.actions = list()
        self.project = QgsProject.instance()
        self.widget = None
        self.action = None
        self.action_maptool = None
        self.map_tool = None
        self.handler = None

    def initGui(self) -> None:
        self.widget = QCityDockWidget(self.project, self.iface)

        self.action = QAction("QCity")
        self.action.setCheckable(True)
        self.action.setIcon(GuiUtils.get_icon("plugin.svg"))
        self.actions.append(self.action)
        self.widget.setToggleVisibilityAction(self.action)

        self.iface.pluginToolBar().addAction(self.action)

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.widget)

        self.action_maptool = QAction("QCity", self.iface.mainWindow())

        self.map_tool = DrawPolygonTool(
            map_canvas=self.iface.mapCanvas(),
            cad_dock_widget=self.iface.cadDockWidget()
        )

        self.handler = MapToolHandler(self.map_tool, self.action_maptool)
        self.iface.registerMapToolHandler(self.handler)

        self.widget.add_feature_clicked.connect(self.map_tool.add_feature)

        self.widget.show()

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI."""
        if self.widget:
            self.widget.deleteLater()
            self.widget = None

        if self.handler:
            self.iface.unregisterMapToolHandler(self.handler)
            self.handler = None

        if self.action:
            self.action.deleteLater()
            self.action = None

        for a in self.actions:
            a.deleteLater()
        self.actions = []

        PROJECT_CONTROLLER.cleanup()
        PROJECT_CONTROLLER.deleteLater()

    @staticmethod
    def tr(message) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("QCityPlugin", message)
