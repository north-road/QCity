from qgis.PyQt.QtCore import Qt
from qgis.core import QgsExpression, QgsFeature, QgsFeatureRequest

from qcity.core import LayerType, PROJECT_CONTROLLER, DatabaseUtils, SETTINGS_MANAGER
from .page_controller import PageController


class BuildingLevelsPageController(PageController):
    """
    Page controller for the building levels page
    """

    def __init__(self, og_widget: "QCityDockWidget", tab_widget, list_widget):
        super().__init__(LayerType.BuildingLevels, og_widget, tab_widget, list_widget)
        self.skip_fields_for_widgets = ["fid", "name", "development_site_pk"]

        PROJECT_CONTROLLER.development_site_changed.connect(
            self.on_development_site_changed
        )
        PROJECT_CONTROLLER.building_level_added.connect(self._on_building_level_added)
        PROJECT_CONTROLLER.building_level_deleted.connect(
            self._on_building_level_deleted
        )

        self.og_widget.toolButton_building_level_add.clicked.connect(
            self.add_feature_clicked
        )

        self.og_widget.toolButton_building_level_remove.clicked.connect(
            self.remove_current_selection
        )

        self.og_widget.toolButton_building_level_rename.clicked.connect(
            self.rename_current_selection
        )

        self.og_widget.button_move_up.clicked.connect(self.move_up)
        self.og_widget.button_move_down.clicked.connect(self.move_down)

        for w in (
            self.og_widget.percent_commercial_floorspace,
            self.og_widget.percent_office_floorspace,
            self.og_widget.percent_residential_floorspace,
        ):
            w.valueChanged.connect(self._update_floorspace_total)

        for w in (
            self.og_widget.percent_1_bedroom_floorspace,
            self.og_widget.percent_2_bedroom_floorspace,
            self.og_widget.percent_3_bedroom_floorspace,
            self.og_widget.percent_4_bedroom_floorspace,
        ):
            w.valueChanged.connect(self._update_residential_space_total)

    def _update_floorspace_total(self):
        """
        Update total floorspace label
        """

        total = 0
        for w in (
            self.og_widget.percent_commercial_floorspace,
            self.og_widget.percent_office_floorspace,
            self.og_widget.percent_residential_floorspace,
        ):
            total += w.value()

        self.og_widget.floorspace_sum.setText(str(total))
        f = self.og_widget.floorspace_sum.font()
        f.setBold(True)
        self.og_widget.floorspace_sum.setFont(f)
        if total > 100:
            self.og_widget.floorspace_sum.setStyleSheet("color: red")
        else:
            self.og_widget.floorspace_sum.setStyleSheet("")

    def _update_residential_space_total(self):
        """
        Update total residential space label
        """

        total = 0
        for w in (
            self.og_widget.percent_1_bedroom_floorspace,
            self.og_widget.percent_2_bedroom_floorspace,
            self.og_widget.percent_3_bedroom_floorspace,
            self.og_widget.percent_4_bedroom_floorspace,
        ):
            total += w.value()

        self.og_widget.residential_sum.setText(str(total))
        f = self.og_widget.residential_sum.font()
        f.setBold(True)
        self.og_widget.residential_sum.setFont(f)
        if total > 100:
            self.og_widget.residential_sum.setStyleSheet("color: red")
        else:
            self.og_widget.residential_sum.setStyleSheet("")

    def _on_building_level_added(self, feature: QgsFeature):
        """
        Called when a new development site is created
        """
        if (
            feature[DatabaseUtils.foreign_key_for_layer(self.layer_type)]
            != PROJECT_CONTROLLER.current_development_site_fid
        ):
            return

        self.add_feature_to_list(feature)

    def _on_building_level_deleted(self, feature_id: int):
        """
        Called when a building level is deleted
        """
        self.remove_item_from_list(feature_id)

    def on_development_site_changed(self, development_site_fid: int):
        """
        Called when the current development site FID is changed
        """
        level_layer = self.get_layer()
        self.list_widget.clear()
        foreign_key = DatabaseUtils.foreign_key_for_layer(self.layer_type)

        filter_expression = QgsExpression.createFieldEqualityExpression(
            foreign_key, development_site_fid
        )
        if SETTINGS_MANAGER.use_layer_subset_filters():
            level_layer.setSubsetString(filter_expression)

        request = QgsFeatureRequest()
        request.setFilterExpression(filter_expression)
        request.setOrderBy(
            QgsFeatureRequest.OrderBy(
                [QgsFeatureRequest.OrderByClause("level_index", ascending=False)]
            )
        )

        for feat in level_layer.getFeatures(request):
            self.add_feature_to_list(feat, set_current=False)

    def delete_feature_and_child_objects(self, feature_id: int) -> bool:
        return PROJECT_CONTROLLER.delete_building_level(feature_id)

    def move_up(self):
        self._move_current_layer(up=True)

    def move_down(self):
        self._move_current_layer(up=False)

    def _move_current_layer(self, up: bool):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        feature_id = selected_items[0].data(Qt.UserRole)
        if PROJECT_CONTROLLER.move_building_level(feature_id, up):
            old_row = self.list_widget.row(selected_items[0])
            item = self.list_widget.takeItem(old_row)
            if up:
                self.list_widget.insertItem(old_row - 1, item)
            else:
                self.list_widget.insertItem(old_row + 1, item)
            self.list_widget.setCurrentRow(self.list_widget.row(item))
