import csv

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from qgis.PyQt.QtWidgets import QSpinBox, QDoubleSpinBox, QLabel
from qgis.PyQt.QtCore import QObject
from qgis.core import QgsVectorLayer
from qcity.core import SETTINGS_MANAGER


class WidgetUtilsStatistics(QObject):
    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.totals = dict()
        self.og_widget = og_widget

        for box in [
            self.og_widget.collapsibleGroupBox_building_levels_development_statistics,
            self.og_widget.collapsibleGroupBox_building_levels_car_parking_statistics,
            self.og_widget.collapsibleGroupBox_building_levels_bike_parking_statistics,
        ]:
            for child in box.findChildren((QSpinBox, QDoubleSpinBox)):
                child.valueChanged.connect(self.update_development_statistics)

        self.og_widget.pushButton_csv_export.clicked.connect(
            self.export_statistics_csv
        )

    def update_development_statistics(self) -> None:
        """Accumulates the values of all spinBoxes belonging to building levels and sets the values in the statistics tab"""
        gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.building_level_prefix}"
        layer = QgsVectorLayer(gpkg_path, SETTINGS_MANAGER.building_level_prefix, "ogr")

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

        for feat in layer.getFeatures():
            for widget_name, attr in stats_mapping.items():
                self.totals[widget_name] += feat[attr]

        for widget_name, total in self.totals.items():
            label = self.og_widget.findChild(QLabel, widget_name)
            if label:
                label.setText(str(total))

    def export_statistics_csv(self) -> None:
        """Exports the statistics tab to a CSV file."""
        csv_filename, _ = QFileDialog.getSaveFileName(self.og_widget, self.tr("Choose CSV Path"), "*.csv")

        if csv_filename and csv_filename.endswith(".csv"):
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Statistic", "Value"])

                for key, value in self.totals.items():
                    clean_key = key.replace("label_statistics_", "")
                    writer.writerow([clean_key, value])
        else:
            QMessageBox.warning(self.og_widget, "Could not save csv file!", "Wrong filename specified.")