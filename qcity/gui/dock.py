from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLabel, QToolButton

from qgis.gui import QgsDockWidget

from .gui_utils import GuiUtils
from .main_panel import MainPanel

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path("dockwidget_main.ui"))


class QCityDock(WIDGET, QgsDockWidget):
    """
    Main dock widget.
    """

    def __init__(self, project, iface) -> None:
        super(QCityDock, self).__init__()
        self.setupUi(self)
        self.setObjectName("QCityDock")

        self._main_panel = MainPanel(project, iface)
        self._main_panel.setDockMode(True)
        self._title_label = self.widget.findChildren(QLabel)[0]
        self._menu_button = self.widget.findChildren(QToolButton, "mMenuButton")[0]
        self.widget.setMainPanel(self._main_panel)
        self._main_panel.panel_dismissed.connect(
            self._update_title, Qt.ConnectionType.QueuedConnection
        )
        self._update_title()

    def main_panel(self) -> MainPanel:
        return self._main_panel

    def _update_title(self):
        self._title_label.show()
        self._title_label.setText(self.tr("Project Parameters"))
        self._menu_button.show()
