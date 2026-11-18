from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import QWidget

from qgis.gui import QgsPanelWidget

from .gui_utils import GuiUtils
from qcity.core import SETTINGS_MANAGER

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path("database_settings.ui"))


class DatabaseSettingsPanel(WIDGET, QgsPanelWidget):
    """
    Database settings panel
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setPanelTitle(self.tr("Database Properties"))

        self.panelAccepted.connect(self._save_settings)

    def _save_settings(self):
        pass
