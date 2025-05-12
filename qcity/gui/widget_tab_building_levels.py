from qgis.core import QgsExpression, QgsFeature

from qcity.core import LayerType, PROJECT_CONTROLLER, DatabaseUtils
from .page_controller import PageController


class BuildingLevelsPageController(PageController):
    """
    Page controller for the building levels page
    """

    def __init__(self, og_widget: 'QCityDockWidget', tab_widget, list_widget):
        super().__init__(LayerType.BuildingLevels, og_widget, tab_widget, list_widget)
        self.skip_fields_for_widgets = ['fid', 'name', 'development_site_pk', 'level_height']

        PROJECT_CONTROLLER.development_site_changed.connect(self.on_development_site_changed)
        PROJECT_CONTROLLER.building_level_added.connect(
            self._on_building_level_added
        )
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

    def _on_building_level_added(self, feature: QgsFeature):
        """
        Called when a new development site is created
        """
        if feature[
            DatabaseUtils.foreign_key_for_layer(self.layer_type)
        ] != PROJECT_CONTROLLER.current_development_site_fid:
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
        level_layer.setSubsetString(
            QgsExpression.createFieldEqualityExpression(foreign_key, development_site_fid))

        for feat in level_layer.getFeatures():
            self.add_feature_to_list(feat, set_current=False)

    def delete_feature_and_child_objects(self, feature_id: int) -> bool:
        return PROJECT_CONTROLLER.delete_building_level(feature_id)
