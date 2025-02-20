import sqlite3

from qgis.PyQt.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QListWidgetItem,
    QDialog,
)
from qgis.PyQt.QtCore import QObject, Qt
from qgis.core import QgsVectorLayer, QgsFeatureRequest, QgsProject
from qgis.gui import QgsNewNameDialog

from qcity.core import SETTINGS_MANAGER


class WidgetUtilsProjectArea(QObject):
    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.og_widget = og_widget

        self.og_widget.toolButton_project_area_add.clicked.connect(
            self.action_maptool_emit
        )

        self.og_widget.toolButton_project_area_remove.clicked.connect(
            self.remove_selected_areas
        )

        self.og_widget.toolButton_project_area_rename.clicked.connect(
            self.update_area_name_gpkg
        )

        self.og_widget.listWidget_project_areas.itemClicked.connect(
            lambda item: self.zoom_to_project_area(item)
        )

        for widget in self.og_widget.tab_project_areas.findChildren(
            (QSpinBox, QDoubleSpinBox)
        ):
            widget.valueChanged.connect(
                lambda value,
                widget=widget: SETTINGS_MANAGER.save_widget_value_to_settings(
                    widget, value, "project_areas"
                )
            )  # This does work indeed, despite the marked error

        self.og_widget.listWidget_project_areas.currentItemChanged.connect(
            lambda item: self.update_project_area_parameters(item)
        )

        # Load associated database when project is loaded on startup
        # TODO: Connect this so it also loads when a project is loaded while in session
        self.load_saved_database_path()

    def load_saved_database_path(self):
        path = SETTINGS_MANAGER.get_database_path_with_project_name()
        if path:
            self.load_project_database(path)

    def remove_selected_areas(self) -> None:
        """Removes selected area from QListwidget, map and geopackage."""
        tbr_areas = self.og_widget.listWidget_project_areas.selectedItems()

        if tbr_areas:
            rows = {
                self.og_widget.listWidget_project_areas.row(item): item.text()
                for item in tbr_areas
            }

            for key, table_name in rows.items():
                self.og_widget.listWidget_project_areas.takeItem(key)

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

            self.og_widget.label_current_project_area.setText("Project Area")

            if self.og_widget.listWidget_project_areas.count() < 1:
                SETTINGS_MANAGER.set_current_project_area_parameter_table_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                self.og_widget.groupbox_car_parking.setEnabled(False)
                self.og_widget.groupbox_bike_parking.setEnabled(False)
                self.og_widget.groupbox_dwellings.setEnabled(False)

    def update_area_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.og_widget.listWidget_project_areas.selectedItems()[0]
        old_feat_name = widget.text()

        existing_names = [
            self.og_widget.listWidget_project_areas.item(i).text()
            for i in range(self.og_widget.listWidget_project_areas.count())
        ]

        dialog = QgsNewNameDialog(
            initial="",
            existing=existing_names,
            cs=Qt.CaseSensitivity.CaseSensitive,
            parent=self.og_widget.iface.mainWindow(),
        )

        dialog.setWindowTitle(self.tr("Rename"))
        dialog.setAllowEmptyName(False)
        dialog.setHintString(self.tr("Enter a name for the project area"))

        if dialog.exec_() != QDialog.DialogCode.Accepted:
            return

        new_feat_name = dialog.name()

        old_item_id = self.og_widget.listWidget_project_areas.row(widget)
        self.og_widget.listWidget_project_areas.takeItem(old_item_id)
        self.og_widget.listWidget_project_areas.addItem(new_feat_name)

        layer = QgsVectorLayer(
            f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.project_area_prefix}",
            SETTINGS_MANAGER.project_area_prefix, "ogr")
        if layer:
            layer.startEditing()
            for feature in layer.getFeatures():
                if feature["name"] == old_feat_name:
                    feature["name"] = new_feat_name
                    layer.updateFeature(feature)
            layer.commitChanges()

        # Set selection to changed item
        item_to_select = self.og_widget.listWidget_project_areas.findItems(
            new_feat_name, Qt.MatchExactly
        )[0]
        self.og_widget.listWidget_project_areas.setCurrentItem(item_to_select)
        SETTINGS_MANAGER.set_current_project_area_parameter_table_name(
            item_to_select.text()
        )

        self.og_widget.label_current_project_area.setText(new_feat_name)

    def zoom_to_project_area(self, item) -> None:
        """Sets the canvas extent to the clicked layer"""
        name = item.text()
        SETTINGS_MANAGER.set_current_project_area_parameter_table_name(name)
        layer = QgsProject.instance().mapLayer(
            SETTINGS_MANAGER.get_project_area_layer_id()
        )
        layer.setSubsetString(f"name='{name}'")

        site_layer = QgsProject.instance().mapLayer(
            SETTINGS_MANAGER.get_development_site_layer_id()
        )
        sql_filter = "FALSE"
        site_layer.setSubsetString(sql_filter)

        extent = layer.extent()
        self.og_widget.iface.mapCanvas().setExtent(extent)
        self.og_widget.iface.mapCanvas().refresh()

    def update_project_area_parameters(self, item: QListWidgetItem) -> None:
        """
        Updates the parameter-spin-boxes of the project area to the currently selected one.
        """
        if item:
            feature_name = item.text()

            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(feature_name)

            gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.project_area_prefix}"

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
                    continue
                widget = self.og_widget.findChild(
                    (QSpinBox, QDoubleSpinBox), widget_name
                )
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(widget_values_dict[widget_name]))
                else:
                    widget.setValue(widget_values_dict[widget_name])

            self.og_widget.label_current_project_area.setText(feature_name)

    def action_maptool_emit(self) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.add_feature_clicked.emit(True)
