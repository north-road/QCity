from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import QWidget

from qgis.gui import QgsPanelWidget

from .gui_utils import GuiUtils
from qcity.core import SETTINGS_MANAGER

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path("settings_panel.ui"))


class SettingsPanel(WIDGET, QgsPanelWidget):
    """
    Settings panel
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setPanelTitle(self.tr("QCity Settings"))

        self.default_crs_widget.setCrs(SETTINGS_MANAGER.default_database_crs())

        self.panelAccepted.connect(self._save_settings)

    def _save_settings(self):
        SETTINGS_MANAGER.set_default_database_crs(self.default_crs_widget.crs())
