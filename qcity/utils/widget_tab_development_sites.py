
from qgis.PyQt.QtCore import QObject

from ..core import SETTINGS_MANAGER


class WidgetUtilsDevelopmentSites(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self.og_widget = widget

        self.og_widget.toolButton_development_site_add.clicked.connect(
            self.action_maptool_emit
        )

    def action_maptool_emit(self) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.add_project_area_clicked.emit(True)
