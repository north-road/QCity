from qgis.core import Qgis, QgsVectorLayer, QgsFeature, QgsExpression

from qcity.core import SETTINGS_MANAGER, LayerType, PROJECT_CONTROLLER, DatabaseUtils
from .page_controller import PageController


class DevelopmentSitesPageController(PageController):
    """
    Page controller for the development sites page
    """

    def __init__(self, og_widget, tab_widget, list_widget, current_item_label):
        super().__init__(LayerType.DevelopmentSites, og_widget, tab_widget, list_widget, current_item_label)
        self.skip_fields_for_widgets = ['fid', 'name', 'project_area_pk']

        PROJECT_CONTROLLER.project_area_changed.connect(self.on_project_area_changed)
        PROJECT_CONTROLLER.development_site_added.connect(
            self._on_development_site_added
        )
        PROJECT_CONTROLLER.development_site_deleted.connect(
            self._on_development_site_deleted
        )
        PROJECT_CONTROLLER.development_site_attribute_changed.connect(
            self._on_development_site_attribute_changed
        )

        self.og_widget.toolButton_development_site_add.clicked.connect(
            self.add_feature_clicked
        )

        self.og_widget.toolButton_development_site_remove.clicked.connect(
            self.remove_current_selection
        )

        self.og_widget.toolButton_development_site_rename.clicked.connect(
            self.rename_current_selection
        )

        self.og_widget.auto_calculate_floorspace.toggled.connect(
            self._auto_calculate_floorspace_toggled
        )
        self.og_widget.auto_calculate_car_parking.toggled.connect(
            self._auto_calculate_car_parking_toggled
        )
        self.og_widget.auto_calculate_bicycle_parking.toggled.connect(
            self._auto_calculate_bicycle_parking_toggled
        )

    def _on_development_site_added(self, feature: QgsFeature):
        """
        Called when a new development site is created
        """
        if feature[
            DatabaseUtils.foreign_key_for_layer(self.layer_type)
        ] != PROJECT_CONTROLLER.current_project_area_fid:
            return

        self.add_feature_to_list(feature)

    def _on_development_site_deleted(self, feature_id: int):
        """
        Called when a development site is deleted
        """
        self.remove_item_from_list(feature_id)

    def _on_development_site_attribute_changed(self, feature_id: int, field_name: str, value):
        """
        Called when an attribute is changed for a development site
        """
        if feature_id != self.current_feature_id:
            return

        self._block_feature_updates = True
        self.set_widget_values({
            field_name: value
        })
        self._block_feature_updates = False

    def on_project_area_changed(self, project_area_fid: int):
        """
        Called when the current project area FID is changed
        """
        site_layer = self.get_layer()
        self.list_widget.clear()
        foreign_key = DatabaseUtils.foreign_key_for_layer(self.layer_type)
        site_layer.setSubsetString(
            QgsExpression.createFieldEqualityExpression(foreign_key, project_area_fid))

        for feat in site_layer.getFeatures():
            self.add_feature_to_list(feat, set_current=False)

    def delete_feature_and_child_objects(self, feature_id: int) -> bool:
        return PROJECT_CONTROLLER.delete_development_site(feature_id)

    def set_feature(self, feature: QgsFeature):
        super().set_feature(feature)
        PROJECT_CONTROLLER.set_current_development_site(feature.id())

    def _auto_calculate_floorspace_toggled(self, active: bool):
        """
        Called when the auto calculate floorspace option is toggled
        """
        if self._block_feature_updates or not active:
            return

        PROJECT_CONTROLLER.auto_calculate_development_site_floorspace(self.current_feature_id)

    def _auto_calculate_car_parking_toggled(self, active: bool):
        """
        Called when the auto calculate car parking option is toggled
        """
        if self._block_feature_updates or not active:
            return

        PROJECT_CONTROLLER.auto_calculate_development_site_car_parking(self.current_feature_id)

    def _auto_calculate_bicycle_parking_toggled(self, active: bool):
        """
        Called when the auto calculate bicycle parking option is toggled
        """
        if self._block_feature_updates or not active:
            return

        PROJECT_CONTROLLER.auto_calculate_development_site_bicycle_parking(self.current_feature_id)
