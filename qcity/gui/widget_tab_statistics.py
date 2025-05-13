import csv

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from qgis.PyQt.QtWidgets import QLabel
from qgis.PyQt.QtCore import QObject
from qgis.core import QgsVectorLayer, QgsFeatureRequest
from qcity.core import SETTINGS_MANAGER, PROJECT_CONTROLLER, LayerType


class WidgetUtilsStatistics(QObject):
    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.totals = dict()
        self.og_widget = og_widget

        PROJECT_CONTROLLER.project_area_added.connect(
            self.populate_project_area_combo_box
        )
        PROJECT_CONTROLLER.project_area_deleted.connect(
            self.populate_project_area_combo_box
        )

        self.og_widget.comboBox_statistics_projects.activated.connect(
            self.update_development_statistics
        )

        self.populate_project_area_combo_box()

        self.og_widget.pushButton_csv_export.clicked.connect(self.export_statistics_csv)

    def update_development_statistics(self) -> None:
        """Accumulates the values of all spinBoxes belonging to building levels and sets the values in the statistics tab"""
        stats_mapping = {
            "label_statistics_dev_stats_commercial_floorspace": "doubleSpinBox_building_levels_commercial_floorspace",
            "label_statistics_dev_stats_office_floorspace": "doubleSpinBox_building_levels_office_floorspace",
            "label_statistics_dev_stats_residential_floorspace": "doubleSpinBox_building_levels_residential_floorspace",
            "label_statistics_dev_stats_1_bedroom_dwellings": "spinBox_building_levels_1_bedroom_dwellings",
            "label_statistics_dev_stats_2_bedroom_dwellings": "spinBox_building_levels_2_bedroom_dwellings",
            "label_statistics_dev_stats_3_bedroom_dwellings": "spinBox_building_levels_3_bedroom_dwellings",
            "label_statistics_dev_stats_4_bedroom_dwellings": "spinBox_building_levels_4_bedroom_dwellings",
            "label_statistics_car_parking_stats_commercial_car_parks": "spinBox_building_levels_commercial_car_parks",
            "label_statistics_car_parking_stats_office_car_bays": "spinBox_building_levels_office_car_bays",
            "label_statistics_car_parking_stats_residential_car_bays": "spinBox_building_levels_residential_car_bays",
            "label_statistics_bike_parking_stats_commercial_bike_parks": "spinBox_building_levels_commercial_bike_parks",
            "label_statistics_bike_parking_stats_office_bike_bays": "spinBox_building_levels_office_bike_bays",
            "label_statistics_bike_parking_stats_residential_bike_bays": "spinBox_building_levels_residential_bike_bays",
        }

        self.totals = {widget_name: 0 for widget_name in stats_mapping}

        level_features = self.get_levels()

        for feat in level_features:
            for widget_name, attr in stats_mapping.items():
                self.totals[widget_name] += feat[attr]

        for widget_name, total in self.totals.items():
            label = self.og_widget.findChild(QLabel, widget_name)
            if label:
                label.setText(str(total))

    def export_statistics_csv(self) -> None:
        """Exports the statistics tab to a CSV file."""
        csv_filename, _ = QFileDialog.getSaveFileName(
            self.og_widget, self.tr("Choose CSV Path"), "*.csv"
        )

        if csv_filename and csv_filename.endswith(".csv"):
            with open(csv_filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Statistic", "Value"])

                for key, value in self.totals.items():
                    clean_key = key.replace("label_statistics_", "")
                    writer.writerow([clean_key, value])
        else:
            QMessageBox.warning(
                self.og_widget, "Could not save csv file!", "Wrong filename specified."
            )

    def get_levels(self) -> list[str]:
        """Returns building levels of the current project area by geometry"""
        gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.project_area_prefix}"
        area_layer = QgsVectorLayer(
            gpkg_path, SETTINGS_MANAGER.project_area_prefix, "ogr"
        )
        gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.building_level_prefix}"
        level_layer = QgsVectorLayer(
            gpkg_path, SETTINGS_MANAGER.building_level_prefix, "ogr"
        )

        selected_area_name = self.og_widget.comboBox_statistics_projects.currentText()

        filter_expression = f"\"name\" = '{selected_area_name}'"

        old_subset_string = area_layer.subsetString()
        area_layer.setSubsetString("")
        request = QgsFeatureRequest().setFilterExpression(filter_expression)
        iterator = area_layer.getFeatures(request)
        area_layer.setSubsetString(old_subset_string)

        filter_feature = next(iterator)

        feats = list()
        for feat in level_layer.getFeatures():
            if feat.geometry().within(filter_feature.geometry()):
                feats.append(feat)

        return feats

    def populate_project_area_combo_box(self) -> None:
        """
        Populates the project area combo box
        """
        area_layer = PROJECT_CONTROLLER.get_project_area_layer()
        if not area_layer or not area_layer.isValid():
            return

        name_to_id = {
            feature["name"]: feature.id() for feature in area_layer.getFeatures()
        }
        names_sorted = sorted(list(name_to_id.keys()), key=str.casefold)
        self.og_widget.comboBox_statistics_projects.clear()
        for name in names_sorted:
            self.og_widget.comboBox_statistics_projects.addItem(name, name_to_id[name])

