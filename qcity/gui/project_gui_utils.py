"""
Project related GUI Utilities
"""

from typing import List, Union, Optional

from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox, QDialog, QWidget
from qgis.core import (
    NULL,
    QgsGeometry,
    QgsVectorLayer,
    QgsPointXY,
    QgsRasterLayer,
    Qgis,
)
from qgis.gui import (
    QgsMapCanvas,
    QgsAdvancedDigitizingDockWidget,
    QgsMapToolCapture,
    QgsAbstractMapToolHandler,
    QgsMapToolCaptureLayerGeometry,
    QgsNewNameDialog,
)

from qcity.core import LayerType, get_project_controller, DatabaseUtils, LayerUtils
from qcity.core.utils import wrapped_edits


class ProjectGuiUtils:
    """
    Utilities for project related GUI logic
    """

    @staticmethod
    def get_new_name(
        layer_type: LayerType, parent_pk: int, parent: Optional[QWidget] = None
    ) -> Optional[str]:
        """
        Gets the name for a new object
        """
        project_controller = get_project_controller()
        existing_names = project_controller.get_unique_names(layer_type, parent_pk)

        dialog = QgsNewNameDialog(
            initial="",
            existing=existing_names,
            cs=Qt.CaseSensitivity.CaseSensitive,
            parent=parent,
        )

        dialog.setWindowTitle(
            QCoreApplication.tr("Create {}").format(
                layer_type.as_title_case(plural=False)
            )
        )
        dialog.setAllowEmptyName(False)
        dialog.setOverwriteEnabled(False)
        dialog.setHintString(
            QCoreApplication.tr("Input {} name").format(
                layer_type.as_sentence_case(plural=False)
            )
        )
        dialog.setConflictingNameWarning(
            QCoreApplication.tr("A {} with this name already exists").format(
                layer_type.as_sentence_case(plural=False)
            )
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        return dialog.name()
