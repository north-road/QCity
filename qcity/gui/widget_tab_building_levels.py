import sqlite3

from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtWidgets import (
    QListWidgetItem,
    QComboBox,
    QWidget,
    QDialog,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
)
from qgis.core import QgsVectorLayer, QgsFeatureRequest, QgsProject
from qgis.gui import QgsNewNameDialog

from qcity.core import SETTINGS_MANAGER


class WidgetUtilsBuildingLevels(QObject):
    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.og_widget = og_widget

        self.og_widget.toolButton_building_level_add.clicked.connect(
            lambda: self.action_maptool_emit(SETTINGS_MANAGER.building_level_prefix)
        )

        self.og_widget.toolButton_building_level_remove.clicked.connect(
            self.remove_selected_sites
        )

        self.og_widget.toolButton_building_level_rename.clicked.connect(
            self.update_site_name_gpkg
        )

        self.og_widget.listWidget_building_levels.currentItemChanged.connect(
            lambda item: self.update_building_level_parameters(item)
        )

        self.og_widget.listWidget_building_levels.currentItemChanged.connect(
            lambda item: self.update_building_level_listwidget(item)
        )

        for widget in self.og_widget.tab_development_sites.findChildren(
            (QSpinBox, QDoubleSpinBox)
        ):
            widget.valueChanged.connect(
                lambda value,
                widget=widget: SETTINGS_MANAGER.save_widget_value_to_settings(
                    widget, value, SETTINGS_MANAGER.building_level_prefix
                )
            )  # This does work indeed, despite the marked error

    def update_building_level_listwidget(self, item: QListWidgetItem) -> None:
        """Updates the listwidget of the building levels to show only building levels within the active project area."""
        site_layer = QgsProject.instance().mapLayer(
            SETTINGS_MANAGER.get_building_level_layer_id()
        )
        area_layer = QgsProject.instance().mapLayer(
            SETTINGS_MANAGER.get_project_area_layer_id()
        )

        name = self.og_widget.listWidget_project_areas.currentItem().text()

        request = QgsFeatureRequest().setFilterExpression(f"\"name\" = '{name}'")
        iterator = area_layer.getFeatures(request)
        filter_feature = next(iterator)
        filter_geom_wkt = filter_feature.geometry().asWkt()

        sql_filter = f"ST_Within($geometry, ST_GeomFromText('{filter_geom_wkt}', 4326)) and \"name\" = '{item.text()}'"
        site_layer.setSubsetString(sql_filter)

    def action_maptool_emit(self, kind) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.current_digitisation_type = kind
        SETTINGS_MANAGER.add_feature_clicked.emit(True)

    def remove_selected_sites(self) -> None:
        """Removes selected area from Qlistwidget, map and geopackage."""
        tbr_areas = self.og_widget.listWidget_building_levels.selectedItems()

        if tbr_areas:
            rows = {
                self.og_widget.listWidget_building_levels.row(item): item.text()
                for item in tbr_areas
            }

            for key, table_name in rows.items():
                self.og_widget.listWidget_building_levels.takeItem(key)

                layers = self.og_widget.project.mapLayersByName(table_name)
                if layers:
                    self.og_widget.project.removeMapLayer(layers[0].id())

                gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.project_area_prefix}"
                layer = QgsVectorLayer(gpkg_path, SETTINGS_MANAGER.project_area_prefix, "ogr")
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
                SETTINGS_MANAGER.set_current_building_level_parameter_table_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                    # self.og_widget.tabWidget_project_area_parameters.setEnabled(False)

    def update_site_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.og_widget.listWidget_building_levels.selectedItems()[0]
        old_feat_name = widget.text()

        existing_names = [
            self.og_widget.listWidget_building_levels.item(i).text()
            for i in range(self.og_widget.listWidget_building_levels.count())
        ]

        dialog = QgsNewNameDialog(
            initial="",
            existing=existing_names,
            cs=Qt.CaseSensitivity.CaseSensitive,
            parent=self.og_widget.iface.mainWindow(),
        )

        dialog.setWindowTitle(self.tr("Rename"))
        dialog.setAllowEmptyName(False)
        dialog.setHintString(self.tr("Enter a name for the development site"))

        if dialog.exec_() != QDialog.DialogCode.Accepted:
            return

        new_feat_name = dialog.name()

        old_item_id = self.og_widget.listWidget_building_levels.row(widget)
        self.og_widget.listWidget_building_levels.takeItem(old_item_id)
        self.og_widget.listWidget_building_levels.addItem(new_feat_name)

        layer = QgsVectorLayer(f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.building_level_prefix}",
                                                     SETTINGS_MANAGER.building_level_prefix, "ogr")
        if layer:
            layer.startEditing()
            for feature in layer.getFeatures():
                if feature["name"] == old_feat_name:
                    feature["name"] = new_feat_name
                    layer.updateFeature(feature)
            layer.commitChanges()

        # Set selection to changed item
        item_to_select = self.og_widget.listWidget_building_levels.findItems(
            new_feat_name, Qt.MatchExactly
        )[0]
        self.og_widget.listWidget_building_levels.setCurrentItem(item_to_select)
        SETTINGS_MANAGER.set_current_building_level_parameter_table_name(
            item_to_select.text()
        )

    def update_building_level_parameters(self, item: QListWidgetItem) -> None:
        """
        Updates the line edits and combobox of the development sites tab to the currently selected site.
        """
        if item:
            feature_name = item.text()

            SETTINGS_MANAGER.set_current_building_level_parameter_table_name(
                feature_name

            )
            gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.building_level_prefix}"

            layer = QgsVectorLayer(gpkg_path, feature_name, "ogr")
            request = QgsFeatureRequest().setFilterExpression(
                f"\"name\" = '{feature_name}'"
            )
            iterator = layer.getFeatures(request)
            feature = next(iterator)

            feature_dict = feature.attributes()
            col_names = [field.name() for field in layer.fields()]
            widget_values_dict = dict(zip(col_names, feature_dict))

            for widget_name in widget_values_dict.keys():
                if widget_name in ["fid", "name"]:
                    pass
                widget = self.og_widget.findChild(QWidget, widget_name)

                if isinstance(widget, QSpinBox):
                    widget.setValue(int(widget_values_dict[widget_name]))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(widget_values_dict[widget_name])