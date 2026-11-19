import os

from dataclasses import dataclass

from qgis.PyQt.QtCore import Qt, QDir
from qgis.PyQt.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from qgis.core import Qgis, QgsCoordinateReferenceSystem
from qgis.gui import QgsFileWidget

from qcity.core import SETTINGS_MANAGER

from .crs_selector import CrsSelector


@dataclass
class NewDatabaseConfig:
    destination_path: str
    crs: QgsCoordinateReferenceSystem


class DestinationPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Destination File"))
        self.setSubTitle(self.tr("Choose where to save the QCity database."))

        self.path_input = QgsFileWidget()
        self.path_input.setDialogTitle(self.tr("QCity Database"))
        self.path_input.setFilter(self.tr("GeoPackage databases") + " (*.gpkg *.GPKG)")
        self.path_input.setStorageMode(QgsFileWidget.StorageMode.SaveFile)
        self.path_input.lineEdit().setPlaceholderText(
            self.tr("Select or type a destination path…")
        )

        self.path_input.setDefaultRoot(SETTINGS_MANAGER.last_used_database_folder())

        self.registerField(
            "dest.path*", self.path_input, "filePath", self.path_input.fileChanged
        )

        row = QHBoxLayout()
        row.addWidget(self.path_input)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(self.tr("Destination file:")))
        layout.addLayout(row)
        self.setLayout(layout)

    def filePath(self) -> str:
        return self.path_input.filePath().strip()

    def isComplete(self) -> bool:
        return bool(self.filePath())

    def validatePage(self):
        path = self.filePath()
        parent_dir = os.path.dirname(path) or "."

        if not os.path.isdir(parent_dir):
            QMessageBox.warning(
                self,
                self.tr("Invalid Folder"),
                self.tr("The folder '{}' does not exist.").format(parent_dir),
            )
            return False

        if os.path.exists(path):
            reply = QMessageBox.question(
                self,
                self.tr("Overwrite File?"),
                self.tr("'{}' already exists. Do you want to overwrite it?").format(
                    QDir.toNativeSeparators(path)
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False

        return True


class CrsPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Coordinate Reference System"))
        self.setSubTitle(self.tr("Select the CRS for the QCity database."))

        self.crs_widget = CrsSelector()

        self.registerField(
            "dest.crs*", self.crs_widget, "crs", self.crs_widget.crs_changed
        )

        layout = QVBoxLayout()
        layout.addWidget(self.crs_widget)
        self.setLayout(layout)

    def crs(self):
        return self.crs_widget.crs()

    def isComplete(self) -> bool:
        return self.crs_widget.crs().isValid()


class SummaryPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Summary"))
        self.setSubTitle(
            self.tr("Confirm your new QCity database properties and click Finish.")
        )

        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.summary_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.summary_label)

    def initializePage(self):
        wizard = self.wizard()
        dest_path = wizard.dest_page.filePath()
        crs = wizard.crs_page.crs()

        self.summary_label.setText(
            self.tr(
                "<b>Destination:</b> {}<br><b>Coordinate Reference System:</b> {}"
            ).format(
                QDir.toNativeSeparators(dest_path),
                crs.userFriendlyIdentifier(Qgis.CrsIdentifierType.FullString),
            )
        )


class NewDatabaseWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("New QCity Database"))
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.dest_page = DestinationPage()
        self.crs_page = CrsPage()

        self.addPage(self.dest_page)
        self.addPage(self.crs_page)
        self.addPage(SummaryPage())

    def config(self) -> NewDatabaseConfig:
        """Return the final validated choices entered in the wizard."""
        return NewDatabaseConfig(
            destination_path=self.dest_page.filePath(),
            crs=self.crs_page.crs(),
        )
