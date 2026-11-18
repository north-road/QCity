from qgis.PyQt import uic
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
        self.widget.setMainPanel(self._main_panel)

    def main_panel(self) -> MainPanel:
        return self._main_panel
