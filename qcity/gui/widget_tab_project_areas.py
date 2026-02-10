from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import QgsFeature, QgsVectorLayer

from qcity.core import SETTINGS_MANAGER, LayerType, get_project_controller
from .page_controller import PageController


class ProjectAreasPageController(PageController):
    """
    Page controller for the project areas page
    """

    def __init__(
        self, og_widget, tab_widget, list_view, list_filter_line_edit, current_label
    ):
        super().__init__(
            LayerType.ProjectAreas,
            og_widget,
            tab_widget,
            list_view,
            list_filter_line_edit,
            current_label,
        )
        self.skip_fields_for_widgets = ("fid", "name")

        project_controller = get_project_controller()
        project_controller.project_area_added.connect(self._on_project_area_added)
        project_controller.project_area_deleted.connect(self._on_project_area_deleted)

        self.og_widget.toolButton_project_area_add.clicked.connect(
            self.add_feature_clicked
        )

        self.og_widget.toolButton_project_area_remove.clicked.connect(
            self.remove_current_selection
        )

        self.og_widget.toolButton_project_area_rename.clicked.connect(
            self.rename_current_selection
        )

        project_controller.project_area_layer_changed.connect(
            self.populate_project_area_combo_box
        )

        self.populate_project_area_combo_box()

    def populate_project_area_combo_box(self):
        """
        Populates the project area list
        """
        area_layer = self.get_layer()
        if not area_layer:
            return

        self.list_model.clear()
        feats = area_layer.getFeatures()
        for feat in feats:
            self.add_feature_to_list(feat)

    def _on_project_area_added(self, feature: QgsFeature):
        """
        Called when a new project area is created
        """
        self.add_feature_to_list(feature)

    def _on_project_area_deleted(self, feature_id: int):
        """
        Called when a project area is deleted
        """
        self.remove_item_from_list(feature_id)

    def delete_feature_and_child_objects(self, feature_id: int) -> bool:
        return get_project_controller().delete_project_area(feature_id)

    def set_feature(self, feature: QgsFeature):
        super().set_feature(feature)
        get_project_controller().set_current_project_area(feature.id())
