from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QFileDialog
)
from qgis.core import (
    QgsFeature,
    QgsVectorLayer
)

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
            self.remove_current_selection
        )

        self.og_widget.toolButton_project_area_rename.clicked.connect(
            self.rename_current_selection
        )

        self.og_widget.pushButton_import_project_areas.clicked.connect(
            self.import_project_area_geometries
        )

    def delete_feature_and_child_objects(self, feature_id: int) -> bool:
        return PROJECT_CONTROLLER.delete_project_area(feature_id)

    def set_feature(self, feature: QgsFeature):
        super().set_feature(feature)

        PROJECT_CONTROLLER.set_current_project_area(feature.id())

        # todo hide others from RENDERER only!!
        # area_layer.setSubsetString(f"\"fid\" = '{feature.id()}'")

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
