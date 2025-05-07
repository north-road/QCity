from qgis.PyQt.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QListWidgetItem,
    QDialog,
    QFileDialog
)
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsFeature,
    QgsVectorLayer,
    QgsProject,
    QgsReferencedRectangle
)
from qgis.gui import QgsNewNameDialog

from qcity.core import SETTINGS_MANAGER, LayerType
from qcity.core.project import ProjectUtils
from .page_controller import PageController


class ProjectAreasPageController(PageController):
    """
    Page controller for the project areas page
    """
    def __init__(self, og_widget, tab_widget, list_widget, current_label):
        super().__init__(LayerType.ProjectAreas, og_widget, tab_widget, list_widget, current_label)
        self.skip_fields_for_widgets = ("fid", "name")

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

        self.og_widget.pushButton_import_project_areas.clicked.connect(
            self.import_project_area_geometries
        )

    def remove_selected_areas(self) -> None:
        """Removes selected area from QListwidget, map and geopackage."""
        tbr_areas = self.list_widget.selectedItems()

        if tbr_areas:
            rows = {
                self.list_widget.row(item): item.text()
                for item in tbr_areas
            }

            for key, table_name in rows.items():
                self.list_widget.takeItem(key)

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

            if self.list_widget.count() < 1:
                self.current_feature_id = None
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                self.og_widget.groupbox_car_parking.setEnabled(False)
                self.og_widget.groupbox_bike_parking.setEnabled(False)
                self.og_widget.groupbox_dwellings.setEnabled(False)

    def set_feature(self, feature: QgsFeature):
        """
        Updates the development site listwidget to only contain sites within the current project area
        """
        area_layer = self.get_layer()
        area_layer.setSubsetString("")

        super().set_feature(feature)

        site_layer = ProjectUtils.get_development_sites_layer(QgsProject.instance())
        level_layer = ProjectUtils.get_building_levels_layer(QgsProject.instance())

        self.og_widget.listWidget_development_sites.clear()

        site_layer.setSubsetString(f'project_area_pk = {feature.id()}')
        for feat in site_layer.getFeatures():
            item = QListWidgetItem(self.og_widget.listWidget_development_sites)
            item.setText(feat["name"])
            item.setData(Qt.UserrRole, feat.id())
            self.og_widget.listWidget_development_sites.addItem(item)

        area_layer.setSubsetString(f"\"fid\" = '{feature.id()}'")

#        level_layer.setSubsetString("FALSE")

        feature_bbox = QgsReferencedRectangle(feature.geometry().boundingBox(), area_layer.crs())

        self.og_widget.iface.mapCanvas().setReferencedExtent(feature_bbox)
        self.og_widget.iface.mapCanvas().refresh()

    def update_area_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.list_widget.selectedItems()[0]
        old_feat_name = widget.text()

        existing_names = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
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

        old_item_id = self.list_widget.row(widget)
        self.list_widget.addItem(new_feat_name)

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
        item_to_select = self.list_widget.findItems(
            new_feat_name, Qt.MatchExactly
        )[0]
        self.list_widget.setCurrentItem(item_to_select)

        self.og_widget.label_current_project_area.setText(new_feat_name)

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
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
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

            self.list_widget.addItem(feature_name)

        item = self.list_widget.findItems(
            feature_name, Qt.MatchExactly
        )[0]
        row = self.list_widget.row(item)
        self.list_widget.setCurrentRow(row)

        if not self.list_widget.isEnabled():
            self.list_widget.setEnabled(True)
