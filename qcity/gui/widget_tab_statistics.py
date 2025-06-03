import csv

from qgis.PyQt.QtCore import QObject, QDir, QUrl
from qgis.PyQt.QtWidgets import QLabel, QFileDialog
from qgis.core import Qgis, QgsFileUtils
from qgis.utils import iface
from qcity.core import PROJECT_CONTROLLER, SETTINGS_MANAGER


class WidgetUtilsStatistics(QObject):
    STATS_MAPPING = {
        "commercial_floorspace": "label_statistics_dev_stats_commercial_floorspace",
        "office_floorspace": "label_statistics_dev_stats_office_floorspace",
        "residential_floorspace": "label_statistics_dev_stats_residential_floorspace",
        "count_1_bedroom_dwellings": "label_statistics_dev_stats_1_bedroom_dwellings",
        "count_2_bedroom_dwellings": "label_statistics_dev_stats_2_bedroom_dwellings",
        "count_3_bedroom_dwellings": "label_statistics_dev_stats_3_bedroom_dwellings",
        "count_4_bedroom_dwellings": "label_statistics_dev_stats_4_bedroom_dwellings",
        "commercial_car_bays": "label_statistics_car_parking_stats_commercial_car_parks",
        "office_car_bays": "label_statistics_car_parking_stats_office_car_bays",
        "residential_car_bays": "label_statistics_car_parking_stats_residential_car_bays",
        "commercial_bicycle_bays": "label_statistics_bike_parking_stats_commercial_bike_parks",
        "office_bicycle_bays": "label_statistics_bike_parking_stats_office_bike_bays",
        "residential_bicycle_bays": "label_statistics_bike_parking_stats_residential_bike_bays",
    }

    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.og_widget = og_widget

        PROJECT_CONTROLLER.project_area_added.connect(
            self.populate_project_area_combo_box
        )
        PROJECT_CONTROLLER.project_area_deleted.connect(
            self.populate_project_area_combo_box
        )
        PROJECT_CONTROLLER.project_area_layer_changed.connect(
            self.populate_project_area_combo_box
        )

        self.og_widget.button_update_stats.clicked.connect(
            self.update_development_statistics
        )

        self.og_widget.comboBox_statistics_projects.currentIndexChanged.connect(
            self._invalidate_stats
        )
        PROJECT_CONTROLLER.project_area_attribute_changed.connect(
            self._invalidate_stats
        )
        PROJECT_CONTROLLER.development_site_added.connect(self._invalidate_stats)
        PROJECT_CONTROLLER.development_site_deleted.connect(self._invalidate_stats)
        PROJECT_CONTROLLER.development_site_attribute_changed.connect(
            self._invalidate_stats
        )
        PROJECT_CONTROLLER.building_level_added.connect(self._invalidate_stats)
        PROJECT_CONTROLLER.building_level_deleted.connect(self._invalidate_stats)
        PROJECT_CONTROLLER.building_level_attribute_changed.connect(
            self._invalidate_stats
        )

        self._invalidate_stats()

        self.populate_project_area_combo_box()

        self.og_widget.pushButton_csv_export.clicked.connect(self.export_statistics_csv)

    def update_development_statistics(self) -> None:
        """
        Accumulates the values of all properties belonging to building levels and sets the values in the statistics tab
        """
        totals = PROJECT_CONTROLLER.calculate_project_area_stats(
            self.og_widget.comboBox_statistics_projects.currentData()
        )
        if not totals:
            return

        for stat, widget_name in WidgetUtilsStatistics.STATS_MAPPING.items():
            label = self.og_widget.findChild(QLabel, widget_name)
            if label:
                label.setText(str(round(totals[stat], 2)))

        self.og_widget.button_update_stats.setStyleSheet("")
        self.og_widget.button_update_stats.setText("Update")

    def export_statistics_csv(self) -> None:
        """Exports the statistics tab to a CSV file."""
        last_path = SETTINGS_MANAGER.last_used_export_path()
        csv_filename, _ = QFileDialog.getSaveFileName(
            self.og_widget, self.tr("Export to CSV"), last_path, "CSV Files (*.csv)"
        )
        if not csv_filename:
            return

        csv_filename = QgsFileUtils.addExtensionFromFilter(csv_filename, "*.csv")
        SETTINGS_MANAGER.set_last_used_export_path(csv_filename)

        totals = PROJECT_CONTROLLER.calculate_project_area_stats(
            self.og_widget.comboBox_statistics_projects.currentData()
        )

        with open(csv_filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Statistic", "Value"])

            for key, value in totals.items():
                writer.writerow([key, value])

        iface.messageBar().pushMessage(
            self.tr("Export to CSV"),
            self.tr('Successfully exported statistics to <a href="{}">{}</a>').format(
                QUrl.fromLocalFile(csv_filename).toString(),
                QDir.toNativeSeparators(csv_filename),
            ),
            Qgis.MessageLevel.Success,
            0,
        )

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

    def _invalidate_stats(self):
        """
        Invalidates current stats when anything changes
        """
        for _, widget_name in WidgetUtilsStatistics.STATS_MAPPING.items():
            label = self.og_widget.findChild(QLabel, widget_name)
            if label:
                label.setText("-")
        self.og_widget.button_update_stats.setStyleSheet("color: red")
        self.og_widget.button_update_stats.setText("Requires Update")
