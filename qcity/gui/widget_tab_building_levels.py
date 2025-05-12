from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QListWidgetItem,
    QSpinBox,
    QDoubleSpinBox,
)
from qgis.core import QgsVectorLayer, QgsExpression

from qcity.core import SETTINGS_MANAGER, LayerType, PROJECT_CONTROLLER, DatabaseUtils
from .page_controller import PageController


class BuildingLevelsPageController(PageController):
    """
    Page controller for the building levels page
    """

    def __init__(self, og_widget: 'QCityDockWidget', tab_widget, list_widget):
        super().__init__(LayerType.BuildingLevels, og_widget, tab_widget, list_widget)
        self.skip_fields_for_widgets = ['fid', 'name', 'development_site_pk', 'level_height']

        PROJECT_CONTROLLER.development_site_changed.connect(self.on_development_site_changed)

        self.og_widget.toolButton_building_level_add.clicked.connect(
            self.add_feature_clicked
        )

        self.og_widget.toolButton_building_level_remove.clicked.connect(
            self.remove_selected_sites
        )

        self.og_widget.toolButton_building_level_rename.clicked.connect(
            self.rename_current_selection
        )

    def on_development_site_changed(self, development_site_fid: int):
        """
        Called when the current development site FID is changed
        """
        level_layer = self.get_layer()
        self.list_widget.clear()
        foreign_key = DatabaseUtils.foreign_key_for_layer(self.layer_type)
        name_field = DatabaseUtils.name_field_for_layer(self.layer_type)
        level_layer.setSubsetString(
            QgsExpression.createFieldEqualityExpression(foreign_key, development_site_fid))
        for feat in level_layer.getFeatures():
            item = QListWidgetItem(self.list_widget)
            item.setText(feat[name_field])
            item.setData(Qt.UserRole, feat.id())
            self.list_widget.addItem(item)

    def remove_selected_sites(self) -> None:
        """Removes selected level from Qlistwidget, map and geopackage."""
        tbr_levels = self.og_widget.listWidget_building_levels.selectedItems()

        if tbr_levels:
            rows = {
                self.og_widget.listWidget_building_levels.row(item): item.text()
                for item in tbr_levels
            }

            for key, table_name in rows.items():
                self.og_widget.listWidget_building_levels.takeItem(key)

                layers = self.og_widget.project.mapLayersByName(table_name)
                if layers:
                    self.og_widget.project.removeMapLayer(layers[0].id())

                gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.building_level_prefix}"
                layer = QgsVectorLayer(
                    gpkg_path, SETTINGS_MANAGER.building_level_prefix, "ogr"
                )
                layer.startEditing()

                feature_ids = [
                    feat.id()
                    for feat in layer.getFeatures()
                    if feat["name"] == table_name
                ]

                if feature_ids:
                    for fid in feature_ids:
                        layer.deleteFeature(fid)
                layer.commitChanges()

                del layer

            if self.og_widget.listWidget_building_levels.count() < 1:
                SETTINGS_MANAGER.set_current_building_level_feature_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                    # self.og_widget.tabWidget_project_level_parameters.setEnabled(False)
