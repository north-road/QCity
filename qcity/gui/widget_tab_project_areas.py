from qgis.PyQt.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QListWidgetItem,
    QDialog,
    QFileDialog,
    QWidget
)
from qgis.PyQt.QtCore import QObject, Qt
from qgis.core import (
    QgsFeature,
    QgsVectorLayer,
    QgsProject,
    QgsCoordinateTransform,
)
from qgis.gui import QgsNewNameDialog

from qcity.core import SETTINGS_MANAGER
from qcity.core.project import ProjectUtils


class WidgetUtilsProjectArea(QObject):
    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.og_widget = og_widget

        self.og_widget.toolButton_project_area_add.clicked.connect(
            lambda: self.og_widget.action_maptool_emit(
                SETTINGS_MANAGER.project_area_prefix
            )
        )

        self.og_widget.toolButton_project_area_remove.clicked.connect(
            self.remove_selected_areas
        )

        self.og_widget.toolButton_project_area_rename.clicked.connect(
            self.update_area_name_gpkg
        )

        self.og_widget.listWidget_project_areas.itemClicked.connect(
            lambda item: SETTINGS_MANAGER.set_current_project_area_feature_name(
                item.text()
            )
        )

        self.og_widget.listWidget_project_areas.itemClicked.connect(
            lambda item: self.zoom_to_project_area(item)
        )

        self.og_widget.pushButton_import_project_areas.clicked.connect(
            self.import_project_area_geometries
        )

        for spinBox in self.og_widget.tab_project_areas.findChildren(
            (QSpinBox, QDoubleSpinBox)
        ):
            spinBox.valueChanged.connect(
                lambda value,
                widget=spinBox: SETTINGS_MANAGER.save_widget_value_to_layer(
                    widget, value, SETTINGS_MANAGER.project_area_prefix
                )
            )

        self.og_widget.listWidget_project_areas.currentItemChanged.connect(
            lambda item: self.update_project_area_parameters(item)
        )

        self.og_widget.listWidget_project_areas.itemClicked.connect(
            lambda item: self.update_development_site_listwidget(item)
        )

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
                layer = QgsVectorLayer(
                    gpkg_path, SETTINGS_MANAGER.project_area_prefix, "ogr"
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

            self.og_widget.label_current_project_area.setText("Project Area")

            if self.og_widget.listWidget_project_areas.count() < 1:
                SETTINGS_MANAGER.set_current_project_area_feature_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                self.og_widget.groupbox_car_parking.setEnabled(False)
                self.og_widget.groupbox_bike_parking.setEnabled(False)
                self.og_widget.groupbox_dwellings.setEnabled(False)

    def update_development_site_listwidget(self, item: QListWidgetItem) -> None:
        """Updates the development site listwidget to only contain sites within the current project area"""
        area_layer = ProjectUtils.get_project_area_layer(QgsProject.instance())
        site_layer = ProjectUtils.get_development_sites_layer(QgsProject.instance())
        level_layer = ProjectUtils.get_building_levels_layer(QgsProject.instance())

        self.og_widget.listWidget_development_sites.clear()
        area_layer.setSubsetString("")
        site_layer.setSubsetString("")

        names = list()
        pk = SETTINGS_MANAGER.get_pk(SETTINGS_MANAGER.development_site_prefix)
        for feat in site_layer.getFeatures():
            if feat.id() == pk:
                name = feat["name"]
                self.og_widget.listWidget_development_sites.addItem(name)
                names.append(name)

        area_layer.setSubsetString(f"\"name\" = '{item.text()}'")
        name_filter = ", ".join(f"'{name}'" for name in names)
        site_layer.setSubsetString(f"name IN ({name_filter})")
        level_layer.setSubsetString("FALSE")

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
            SETTINGS_MANAGER.project_area_prefix,
            "ogr",
        )
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
        SETTINGS_MANAGER.set_current_project_area_feature_name(item_to_select.text())

        self.og_widget.label_current_project_area.setText(new_feat_name)

    def zoom_to_project_area(self, item: QListWidgetItem) -> None:
        """Sets the canvas extent to the clicked project area"""
        area_layer = ProjectUtils.get_project_area_layer(QgsProject.instance())
        area_layer.setSubsetString("")

        canvas_crs = self.og_widget.iface.mapCanvas().mapSettings().destinationCrs()
        layer_crs = area_layer.crs()

        feature = self.og_widget.get_feature_of_layer_by_name(area_layer, item)
        feature_bbox = feature.geometry().boundingBox()

        if layer_crs != canvas_crs:
            transform = QgsCoordinateTransform(
                layer_crs, canvas_crs, QgsProject.instance()
            )
            feature_bbox = transform.transformBoundingBox(feature_bbox)

        self.og_widget.iface.mapCanvas().setExtent(feature_bbox)
        self.og_widget.iface.mapCanvas().refresh()

    def update_project_area_parameters(self, item: QListWidgetItem) -> None:
        """
        Updates the parameter-spin-boxes of the project area to the currently selected one.
        """
        if item:
            feature_name = item.text()

            SETTINGS_MANAGER.set_current_project_area_feature_name(feature_name)

            gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.project_area_prefix}"

            layer = QgsVectorLayer(gpkg_path, feature_name, "ogr")

            feature = self.og_widget.get_feature_of_layer_by_name(layer, item)

            widget_values = feature.attributeMap()

            for field_name, value in widget_values.items():
                if field_name in ["fid", "name"]:
                    continue

                widget_name = field_name
                widget = self.og_widget.findChild(
                    (QWidget), widget_name
                )
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                else:
                    assert False

            self.og_widget.label_current_project_area.setText(feature_name)

    def import_project_area_geometries(self):
        """Imports geometries as project areas from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Vector File",
            "",
            "Vector Files (*.shp *.geojson *.gpkg *.kml)",
        )

        layer = QgsVectorLayer(file_path, "Loaded Layer", "ogr")

        area_layer = ProjectUtils.get_project_area_layer(QgsProject.instance())

        for feature in layer.getFeatures():
            items = []
            for index in range(self.og_widget.listWidget_project_areas.count()):
                item = self.og_widget.listWidget_project_areas.item(index)
                items.append(item.text())

            feature_name = str(feature.id())

            if not feature_name or feature_name in items:
                if feature_name in items:
                    # TODO: Replace with a proper message bar notification
                    print("Table name already exists.")
                continue

            attributes = SETTINGS_MANAGER.get_attributes_from_json("project_areas")

            new_feature = QgsFeature()
            new_feature.setGeometry(feature.geometry())

            new_feature.setAttributes([None] * len(area_layer.fields()))
            for key, value in attributes.items():
                if key in area_layer.fields().names():
                    new_feature.setAttribute(
                        area_layer.fields().indexFromName(key), value
                    )
            new_feature.setAttribute(
                area_layer.fields().indexFromName("name"), feature_name
            )

            area_layer.startEditing()
            area_layer.addFeature(new_feature)
            area_layer.commitChanges()

            self.og_widget.listWidget_project_areas.addItem(feature_name)

        item = self.og_widget.listWidget_project_areas.findItems(
            feature_name, Qt.MatchExactly
        )[0]
        row = self.og_widget.listWidget_project_areas.row(item)
        self.og_widget.listWidget_project_areas.setCurrentRow(row)

        if not self.og_widget.listWidget_project_areas.isEnabled():
            self.og_widget.listWidget_project_areas.setEnabled(True)
