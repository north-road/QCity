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

from qcity.core import SETTINGS_MANAGER, LayerType, PROJECT_CONTROLLER
from .page_controller import PageController


class ProjectAreasPageController(PageController):
    """
    Page controller for the project areas page
    """
    def __init__(self, og_widget, tab_widget, list_widget, current_label):
        super().__init__(LayerType.ProjectAreas, og_widget, tab_widget, list_widget, current_label)
        self.skip_fields_for_widgets = ("fid", "name")

        self.og_widget.toolButton_project_area_add.clicked.connect(
            self.add_feature_clicked
        )

        self.og_widget.toolButton_project_area_remove.clicked.connect(
            self.remove_selected_areas
        )

        self.og_widget.toolButton_project_area_rename.clicked.connect(
            self.rename_area
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
        area_layer = self.get_layer()
        area_layer.setSubsetString("")

        super().set_feature(feature)

        PROJECT_CONTROLLER.set_current_project_area(feature.id())

        area_layer.setSubsetString(f"\"fid\" = '{feature.id()}'")

        feature_bbox = QgsReferencedRectangle(feature.geometry().boundingBox(), area_layer.crs())

        self.og_widget.iface.mapCanvas().setReferencedExtent(feature_bbox)
        self.og_widget.iface.mapCanvas().refresh()

    def rename_area(self) -> None:
        """
        Renames the selected area
        """
        selected_item = self.list_widget.selectedItems()[0]
        feature_id = selected_item.data(Qt.UserRole)

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

        dialog.setWindowTitle(self.tr("Rename Project Area"))
        dialog.setAllowEmptyName(False)
        dialog.setHintString(self.tr("Enter a new name for the project area"))

        if dialog.exec_() != QDialog.DialogCode.Accepted:
            return

        new_feat_name = dialog.name()
        selected_item.setText(new_feat_name)
        self.current_item_label.setText(new_feat_name)

        layer = self.get_layer()
        layer.startEditing()
        layer.changeAttributeValue(feature_id, layer.fields().lookupField("name"), new_feat_name)
        layer.commitChanges()

    def import_project_area_geometries(self):
        """Imports geometries as project areas from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Vector File",
            "",
            "Vector Files (*.shp *.geojson *.gpkg *.kml)",
        )

        layer = QgsVectorLayer(file_path, "Loaded Layer", "ogr")

        area_layer = PROJECT_CONTROLLER.get_project_area_layer()

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
