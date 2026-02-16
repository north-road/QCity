import math
from qgis.PyQt.QtCore import Qt, QItemSelectionModel
from qgis.core import (
    NULL,
    Qgis,
    QgsFeature,
    QgsFeatureRequest,
    QgsDistanceArea,
    QgsProject,
    QgsExpression,
)

from qcity.core import (
    LayerType,
    get_project_controller,
    DatabaseUtils,
    SETTINGS_MANAGER,
    utils,
)
from .page_controller import PageController, FeatureListModel


class BuildingLevelsPageController(PageController):
    """
    Page controller for the building levels page
    """

    def __init__(
        self,
        og_widget: "QCityDockWidget",
        tab_widget,
        list_view,
        list_filter_line_edit,
        list_bounds_filter_toggle_button,
    ):
        super().__init__(
            LayerType.BuildingLevels,
            og_widget,
            tab_widget,
            list_view,
            list_filter_line_edit,
            list_bounds_filter_toggle_button,
        )
        self.skip_fields_for_widgets = ["fid", "name", "development_site_pk"]

        self.og_widget.base_height.setProperty("decimals", 2)

        project_controller = get_project_controller()
        project_controller.development_site_changed.connect(
            self.on_development_site_changed
        )
        project_controller.building_level_added.connect(self._on_building_level_added)
        project_controller.building_level_deleted.connect(
            self._on_building_level_deleted
        )
        project_controller.project_area_attribute_changed.connect(
            self._update_residential_space_total
        )
        project_controller.building_level_geometry_changed.connect(
            self._update_residential_space_total
        )
        project_controller.building_level_heights_recalculated.connect(
            self._update_building_level_height
        )

        self.og_widget.toolButton_building_level_add.clicked.connect(
            self.add_feature_clicked
        )

        self.og_widget.toolButton_building_level_duplicate.clicked.connect(
            self.duplicate_feature_clicked
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
            self.og_widget.percent_residential_floorspace,
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

    def _update_building_level_height(self):
        """
        Updates building level height widgets
        """
        feature = self.get_feature_by_id(self.current_feature_id)
        if not feature.isValid():
            return

        self.set_feature(feature)

    def _update_residential_space_total(self):
        """
        Update total residential space label
        """
        if self.current_feature_id is None:
            self.clear_feature()
            return

        total = 0
        for w in (
            self.og_widget.percent_1_bedroom_floorspace,
            self.og_widget.percent_2_bedroom_floorspace,
            self.og_widget.percent_3_bedroom_floorspace,
            self.og_widget.percent_4_bedroom_floorspace,
        ):
            total += w.value()

        self.og_widget.residential_sum.setText(str(round(total, 2)))
        f = self.og_widget.residential_sum.font()
        f.setBold(True)
        self.og_widget.residential_sum.setFont(f)
        if total > 100:
            self.og_widget.residential_sum.setStyleSheet("color: red")
        else:
            self.og_widget.residential_sum.setStyleSheet("")

        feature = self.get_feature_by_id(self.current_feature_id)
        da = QgsDistanceArea()
        da.setEllipsoid(QgsProject.instance().ellipsoid())
        da.setSourceCrs(
            self.get_layer().crs(), QgsProject.instance().transformContext()
        )

        floor_area_m2 = da.convertAreaMeasurement(
            da.measureArea(feature.geometry()), Qgis.AreaUnit.SquareMeters
        )
        if math.isnan(floor_area_m2):
            self.clear_feature()
            return

        total_residential_area = (
            self.og_widget.percent_residential_floorspace.value() / 100 * floor_area_m2
        )
        total_bedroom_area = []
        for w in (
            self.og_widget.percent_1_bedroom_floorspace,
            self.og_widget.percent_2_bedroom_floorspace,
            self.og_widget.percent_3_bedroom_floorspace,
            self.og_widget.percent_4_bedroom_floorspace,
        ):
            total_bedroom_area.append(w.value() / 100 * total_residential_area)

        project_controller = get_project_controller()
        project_area_feature = project_controller.get_project_area_layer().getFeature(
            project_controller.current_project_area_fid
        )
        dwelling_sizes = []
        for bedroom_size_field in (
            "dwelling_size_1_bedroom",
            "dwelling_size_2_bedroom",
            "dwelling_size_3_bedroom",
            "dwelling_size_4_bedroom",
        ):
            dwelling_sizes.append(project_area_feature[bedroom_size_field])

        for bedroom, label in enumerate(
            [
                self.og_widget.label_1bed_size,
                self.og_widget.label_2bed_size,
                self.og_widget.label_3bed_size,
                self.og_widget.label_4bed_size,
            ]
        ):
            label.setText(str(round(dwelling_sizes[bedroom], 2)))

        for bedroom, label in enumerate(
            [
                self.og_widget.label_1bed_unallocated,
                self.og_widget.label_2bed_unallocated,
                self.og_widget.label_3bed_unallocated,
                self.og_widget.label_4bed_unallocated,
            ]
        ):
            label.setText(
                str(round(total_bedroom_area[bedroom] % dwelling_sizes[bedroom], 2))
            )

        total_yield = 0
        for label_index, label in enumerate(
            [
                self.og_widget.label_1bed_yield,
                self.og_widget.label_2bed_yield,
                self.og_widget.label_3bed_yield,
                self.og_widget.label_4bed_yield,
            ]
        ):
            bedroom_yield = int(
                total_bedroom_area[label_index] // dwelling_sizes[label_index]
            )
            total_yield += bedroom_yield
            label.setText(str(bedroom_yield))
        self.og_widget.label_residential_yield.setText(str(total_yield))

        total_leftover_residential = sum(
            total_bedroom_area[bedroom] % dwelling_sizes[bedroom]
            for bedroom in range(4)
        )
        self.og_widget.label_residential_unallocated.setText(
            str(round(total_leftover_residential, 2))
        )

    def _on_building_level_added(self, feature: QgsFeature):
        """
        Called when a new development site is created
        """
        if (
            feature[DatabaseUtils.foreign_key_for_layer(self.layer_type)]
            != get_project_controller().current_development_site_fid
        ):
            return

        self.add_feature_to_list(feature, add_to_top=True)

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
        self.list_model.clear()
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

        self.clear_feature()

        for feat in level_layer.getFeatures(request):
            self.add_feature_to_list(feat, set_current=False)

    def clear_feature(self):
        super().clear_feature()

        self.og_widget.floorspace_sum.clear()
        self.og_widget.residential_sum.clear()
        self.og_widget.level_index.clear()
        self.og_widget.base_height.clear()
        self.og_widget.label_1bed_size.clear()
        self.og_widget.label_2bed_size.clear()
        self.og_widget.label_3bed_size.clear()
        self.og_widget.label_4bed_size.clear()
        self.og_widget.label_1bed_yield.clear()
        self.og_widget.label_2bed_yield.clear()
        self.og_widget.label_3bed_yield.clear()
        self.og_widget.label_4bed_yield.clear()
        self.og_widget.label_residential_yield.clear()
        self.og_widget.label_1bed_unallocated.clear()
        self.og_widget.label_2bed_unallocated.clear()
        self.og_widget.label_3bed_unallocated.clear()
        self.og_widget.label_4bed_unallocated.clear()
        self.og_widget.label_residential_unallocated.clear()

    def set_feature(self, feature: QgsFeature):
        super().set_feature(feature)
        get_project_controller().set_current_building_level(feature.id())
        if self.current_feature_id is None:
            self.og_widget.collapsibleGroupBox_building_levels_development_statistics.setTitle(
                "Level Composition"
            )
        else:
            item_text = self.list_model.data(
                self.list_model.index_for_feature_id(self.current_feature_id)
            )
            self.og_widget.collapsibleGroupBox_building_levels_development_statistics.setTitle(
                "Level Composition ({})".format(item_text)
            )

        self._update_residential_space_total()

    def duplicate_feature_clicked(self):
        """
        Duplicates the selected building level from the list widget.
        """
        selected_indices = self.list_view.selectionModel().selectedIndexes()
        if not selected_indices:
            return

        feature_id = selected_indices[0].data(FeatureListModel.FEATURE_ID_ROLE)
        feature_name = selected_indices[0].data(Qt.ItemDataRole.DisplayRole)

        building_level_feature = QgsFeature(self.get_feature_by_id(feature_id))

        new_feature_name = self.tr("{} copy").format(feature_name)
        building_level_feature[DatabaseUtils.name_field_for_layer(self.layer_type)] = (
            new_feature_name
        )

        project_controller = get_project_controller()

        parent_pk = project_controller.current_development_site_fid

        building_level_feature["level_index"] = (
            project_controller.get_next_building_level(parent_pk)
        )
        building_level_feature["base_height"] = (
            project_controller.get_floor_base_height(
                parent_pk, building_level_feature["level_index"]
            )
        )
        building_level_feature["fid"] = NULL

        with utils.wrapped_edits(self.get_layer()) as edits:
            edits.addFeature(building_level_feature)

    def delete_feature_and_child_objects(self, feature_id: int) -> bool:
        return get_project_controller().delete_building_level(feature_id)

    def move_up(self):
        self._move_current_layer(up=True)

    def move_down(self):
        self._move_current_layer(up=False)

    def _move_current_layer(self, up: bool):
        selected_indices = self.list_view.selectionModel().selectedIndexes()
        if not selected_indices:
            return

        selected_index = self.proxy_model.mapToSource(selected_indices[0])
        feature_id = self.list_model.data(
            selected_index, FeatureListModel.FEATURE_ID_ROLE
        )
        if get_project_controller().move_building_level(feature_id, up):
            self.list_model.move_row(selected_index, up)
            self.list_view.selectionModel().select(
                self.proxy_model.mapFromSource(
                    self.list_model.index_for_feature_id(feature_id)
                ),
                QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
