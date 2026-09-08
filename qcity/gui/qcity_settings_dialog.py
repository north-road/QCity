"""
Settings dialog for the QCity plugin
"""

from typing import Optional

from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qgis.gui import QgsProjectionSelectionWidget

from qcity.core.settings import SETTINGS_MANAGER


class QCitySettingsDialog(QDialog):
    """
    Dialog for configuring QCity plugin settings.

    Currently exposes a single option: the projection used for layers in
    newly created QCity databases.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("QCity Settings"))

        layout = QVBoxLayout(self)

        description = QLabel(
            self.tr(
                "Choose the projection used for layers in newly created "
                "QCity databases. Existing databases are not affected."
            )
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        form_layout = QFormLayout()
        self.crs_widget = QgsProjectionSelectionWidget()
        self.crs_widget.setCrs(SETTINGS_MANAGER.default_database_crs())
        form_layout.addRow(self.tr("Projection"), self.crs_widget)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_accept(self) -> None:
        crs = self.crs_widget.crs()
        if crs.isValid():
            SETTINGS_MANAGER.set_default_database_crs(crs.authid())
        self.accept()
