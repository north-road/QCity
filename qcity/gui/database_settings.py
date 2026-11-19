import os
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QDir
from qgis.PyQt.QtWidgets import QWidget, QFileDialog, QMessageBox

from qgis.core import Qgis, QgsFileUtils, QgsProjectUtils, QgsProject
from qgis.gui import QgsPanelWidget
from qgis.utils import iface
from .gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path("database_settings.ui"))

from ..core import get_project_controller, SETTINGS_MANAGER, DatabaseUtils

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
            QMessageBox.information(
                self,
                self.tr("Change Database CRS"),
                self.tr(
                    "To change the CRS of an existing QCity database a new copy of this database must be created. Please select the path to store the new database."
                ),
                QMessageBox.StandardButton.Ok,
            )

            current_path = SETTINGS_MANAGER.get_database_path()

            while True:
                file_name, selected_filter = QFileDialog.getSaveFileName(
                    self,
                    self.tr("New QCity Package"),
                    SETTINGS_MANAGER.last_used_database_folder(),
                    "GeoPackage (*.gpkg)",
                )
                if not file_name:
                    return

                gpkg_path = QgsFileUtils.addExtensionFromFilter(
                    file_name, selected_filter
                )

                if (
                    os.path.exists(current_path)
                    and os.path.exists(gpkg_path)
                    and os.path.samefile(current_path, gpkg_path)
                ):
                    QMessageBox.warning(
                        self,
                        self.tr("Invalid Database Path"),
                        self.tr(
                            "The new database path must be a different file to the existing database."
                        ),
                        QMessageBox.StandardButton.Ok,
                    )

                    continue
                break

            dest_crs = dlg.crs()
            DatabaseUtils.copy_reprojected_geopackage(current_path, gpkg_path, dest_crs)
            QgsProjectUtils.updateLayerPath(
                QgsProject.instance(), current_path, gpkg_path
            )
            SETTINGS_MANAGER.set_database_path(gpkg_path)
            QgsProject.instance().setDirty()

            self._db_crs = dest_crs
            self.label_current_crs.setText(
                self._db_crs.userFriendlyIdentifier(Qgis.CrsIdentifierType.MediumString)
            )

            if iface is not None:
                iface.messageBar().pushSuccess(
                    "",
                    self.tr(
                        "QCity database copied to {}, and existing QGIS project updated"
                    ).format(QDir.toNativeSeparators(gpkg_path)),
                )
