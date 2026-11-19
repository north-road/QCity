from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import QWidget

from qgis.core import Qgis
from qgis.gui import QgsPanelWidget, QgsProjectionSelectionTreeWidget

from .gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path("database_settings.ui"))

from ..core import DatabaseUtils, get_project_controller, LayerType

from .crs_selector import CrsSelectorDialog


class DatabaseSettingsPanel(WIDGET, QgsPanelWidget):
    """
    Database settings panel
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setPanelTitle(self.tr("Database Properties"))

        self.panelAccepted.connect(self._save_settings)

        project_controller = get_project_controller()

        layer = project_controller.get_building_levels_layer()

        self._db_crs = layer.crs()
        self.label_current_crs.setText(
            self._db_crs.userFriendlyIdentifier(Qgis.CrsIdentifierType.MediumString)
        )

        self.button_change_crs.clicked.connect(self._change_crs)

    def _save_settings(self):
        pass

    def _change_crs(self):
        dlg = CrsSelectorDialog()
        dlg.set_crs(self._db_crs)
        if dlg.exec():
            self._db_crs = dlg.crs()
            self.label_current_crs.setText(
                self._db_crs.userFriendlyIdentifier(Qgis.CrsIdentifierType.MediumString)
            )
