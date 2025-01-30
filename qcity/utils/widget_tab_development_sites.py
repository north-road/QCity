import sqlite3

from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox
from qgis.PyQt.QtCore import QObject

from ..core import SETTINGS_MANAGER


class WidgetUtilsDevelopmentSites(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self.og_widget = widget

        self.og_widget.toolButton_development_site_add.clicked.connect(
            self.action_maptool_emit
        )

    def action_maptool_emit(self) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.add_project_area_clicked.emit(True)

    def remove_selected_sites(self) -> None:
        """Removes selected area from Qlistwidget, map and geopackage."""
        tbr_sites = self.og_widget.listWidget_development_sites.selectedItems()

        if tbr_sites:
            rows = {
                self.og_widget.listWidget_development_sites.row(item): item.text()
                for item in tbr_sites
            }

            for key, table_name in rows.items():
                self.og_widget.listWidget_development_sites.takeItem(key)

                layers = self.og_widget.project.mapLayersByName(table_name)
                if layers:
                    layer = layers[0]
                    self.og_widget.project.removeMapLayer(layer.id())

                try:
                    with sqlite3.connect(SETTINGS_MANAGER.get_database_path()) as conn:
                        cursor = conn.cursor()

                        cursor.execute(f"DROP TABLE '{SETTINGS_MANAGER.development_site_prefix}{table_name}'")
                        cursor.execute(
                            f"DROP TABLE '{SETTINGS_MANAGER.development_site_parameter_prefix}{table_name}'"
                        )
                        cursor.execute(
                            f"""DELETE FROM gpkg_contents WHERE table_name = '{SETTINGS_MANAGER.development_site_parameter_prefix}{table_name}';"""
                        )
                        cursor.execute(
                            f"""DELETE FROM gpkg_contents WHERE table_name = '{SETTINGS_MANAGER.development_site_prefix}{table_name}';"""
                        )
                        cursor.execute(
                            f"DELETE FROM gpkg_geometry_columns WHERE table_name = '{SETTINGS_MANAGER.development_site_prefix}{table_name}';"
                        )
                        cursor.execute(
                            f"DELETE FROM gpkg_spatial_ref_sys WHERE srs_id = '{SETTINGS_MANAGER.development_site_prefix}{table_name}';"
                        )

                    self.og_widget.iface.mapCanvas().refresh()
                except Exception as e:
                    raise e

            self.og_widget.label_current_developement_site.setText("Project")
            self.og_widget.lineEdit_current_development_site.setText("")

            """if self.og_widget.listWidget_development_sites.count() < 1:
                SETTINGS_MANAGER.set_current_project_area_parameter_table_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                self.og_widget.tabWidget_project_area_parameters.setEnabled(False)"""