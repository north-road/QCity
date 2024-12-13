from libdnf.smartcols import Table
from qgis.PyQt import sip
from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from qgis._core import QgsProject
from qgis.core import QgsApplication

from .gui.gui_utils import GuiUtils
from .gui.widget import (
    TabDockWidget,
)

class GradientDigitizerPlugin:
    def __init__(self, iface):
        self.dlg_config = None
        self.iface = iface
        self.actions = list()
        self.project = QgsProject.instance()

    def initGui(self) -> None:
        self.action = QAction("QCity", self.iface.mainWindow())
        self.action.setIcon(GuiUtils.get_icon("plugin.svg"))

        self.action_widget = QAction("Live Display", self.iface.mainWindow())

        self.actions.append(self.action)
        self.actions.append(self.action_widget)

        self.iface.digitizeToolBar().addAction(self.action)

        self.action.triggered.connect(self.widget_display)

        message_bar = self.iface.messageBar()

        self.widget = TabDockWidget(self.project)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.widget)

        self.widget.show()

    def widget_display(self) -> None:
        """
        shows the widget.
        """
        self.widget.show()

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removeToolBarIcon(self.action)
        del self.action

        for a in self.actions:
            a.deleteLater()
        self.actions = []

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
        return QCoreApplication.translate("X", message)
