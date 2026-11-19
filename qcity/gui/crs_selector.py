from qgis.PyQt.QtCore import pyqtSignal

from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QDialog,
    QDialogButtonBox,
)

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsCsException,
)
from qgis.gui import QgsProjectionSelectionTreeWidget, QgsGui
from qgis.utils import iface

from qcity.core import SETTINGS_MANAGER


class CrsSelector(QWidget):
    crs_double_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout()

        group = QGroupBox(self.tr("Select CRS for QCity database"))
        layout.addWidget(group)
        layout.setContentsMargins(0, 0, 0, 0)

        group_layout = QVBoxLayout()

        self._crs_widget = QgsProjectionSelectionTreeWidget()
        self._crs_widget.setCrs(SETTINGS_MANAGER.default_database_crs())
        group_layout.addWidget(self._crs_widget, 1)

        self._crs_widget.projectionDoubleClicked.connect(self.crs_double_clicked)

        group.setLayout(group_layout)

        self.setLayout(layout)

        if iface is not None:
            canvas = iface.mapCanvas()
            extent = canvas.extent()
            ct = QgsCoordinateTransform(
                canvas.mapSettings().destinationCrs(),
                QgsCoordinateReferenceSystem("EPSG:4326"),
                QgsProject.instance(),
            )
            ct.setBallparkTransformsAreAppropriate(True)
            try:
                extent_wgs = ct.transformBoundingBox(extent)
                self._crs_widget.setPreviewRect(extent_wgs)
            except QgsCsException:
                pass

    def set_crs(self, crs: QgsCoordinateReferenceSystem):
        self._crs_widget.setCrs(crs)

    def crs(self) -> QgsCoordinateReferenceSystem:
        return self._crs_widget.crs()


class CrsSelectorDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setObjectName("CrsSelectorDialog")
        QgsGui.enableAutoGeometryRestore(self)
        self.setWindowTitle(self.tr("QCity Database CRS"))

        layout = QVBoxLayout()
        self._crs_widget = CrsSelector()
        layout.addWidget(self._crs_widget, 1)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

        self.setLayout(layout)

        self._crs_widget.crs_double_clicked.connect(self.accept)

    def set_crs(self, crs: QgsCoordinateReferenceSystem):
        self._crs_widget.set_crs(crs)

    def crs(self) -> QgsCoordinateReferenceSystem:
        return self._crs_widget.crs()
