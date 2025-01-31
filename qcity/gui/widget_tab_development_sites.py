import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QListWidgetItem, QComboBox, QWidget

from qcity.core import SETTINGS_MANAGER


class WidgetUtilsDevelopmentSites(QObject):
    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.og_widget = og_widget

        self.og_widget.toolButton_development_site_add.clicked.connect(
            self.action_maptool_emit
        )

        self.og_widget.toolButton_development_site_remove.clicked.connect(
            self.remove_selected_sites
        )

        self.og_widget.lineEdit_current_development_site.returnPressed.connect(
            self.update_site_name_gpkg
        )

        self.og_widget.lineEdit_development_site_address.textChanged.connect(
            lambda value,
            widget=self.og_widget.lineEdit_development_site_address: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.lineEdit_development_site_owner.textChanged.connect(
            lambda value,
            widget=self.og_widget.lineEdit_development_site_owner: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.lineEdit_development_site_year.textChanged.connect(
            lambda value,
            widget=self.og_widget.lineEdit_development_site_year: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.comboBox_development_site_status.currentIndexChanged.connect(
            lambda value,
            widget=self.og_widget.comboBox_development_site_status: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.listWidget_development_sites.currentItemChanged.connect(
            lambda item: self.update_development_site_parameters(item)
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

                        cursor.execute(
                            f"DROP TABLE '{SETTINGS_MANAGER.development_site_prefix}{table_name}'"
                        )
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

            self.og_widget.label_current_development_site.setText("Project")
            self.og_widget.lineEdit_current_development_site.setText("")

            if self.og_widget.listWidget_development_sites.count() < 1:
                SETTINGS_MANAGER.set_current_development_site_parameter_table_name(None)
                # for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                # widget.setValue(0)
                # self.og_widget.tabWidget_project_area_parameters.setEnabled(False)

    def update_site_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.og_widget.listWidget_development_sites.selectedItems()[0]
        old_layer_name = widget.text()
        layer_name = self.og_widget.lineEdit_current_development_site.text()
        self.og_widget.lineEdit_current_development_site.clear()

        old_item_id = self.og_widget.listWidget_development_sites.row(widget)
        self.og_widget.listWidget_development_sites.takeItem(old_item_id)
        self.og_widget.listWidget_development_sites.addItem(layer_name)

        try:
            database_path = SETTINGS_MANAGER.get_database_path()
            with sqlite3.connect(database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f'ALTER TABLE "{SETTINGS_MANAGER.development_site_prefix}{old_layer_name}" RENAME TO "{SETTINGS_MANAGER.development_site_prefix}{layer_name}"'
                )
                cursor.execute(
                    f"UPDATE gpkg_contents SET table_name = '{SETTINGS_MANAGER.development_site_prefix}{layer_name}' WHERE table_name = '{SETTINGS_MANAGER.development_site_prefix}{old_layer_name}';"
                )
                cursor.execute(
                    f"UPDATE gpkg_geometry_columns SET table_name = '{SETTINGS_MANAGER.development_site_prefix}{layer_name}' WHERE table_name = '{SETTINGS_MANAGER.development_site_prefix}{old_layer_name}'; "
                )

                parameter_name = (
                    f"{SETTINGS_MANAGER.development_site_parameter_prefix}{layer_name}"
                )
                old_parameter_name = f"{SETTINGS_MANAGER.development_site_parameter_prefix}{old_layer_name}"
                cursor.execute(
                    f"UPDATE gpkg_contents SET table_name = '{old_parameter_name}' WHERE table_name = '{parameter_name}';"
                )
                cursor.execute(
                    f"ALTER TABLE '{old_parameter_name}' RENAME TO '{parameter_name}'"
                )
                conn.commit()

        except Exception as e:
            raise e

        # Set selection to changed item
        item_to_select = self.og_widget.listWidget_development_sites.findItems(
            layer_name, Qt.MatchExactly
        )[0]
        self.og_widget.listWidget_development_sites.setCurrentItem(item_to_select)
        SETTINGS_MANAGER.set_current_project_area_parameter_table_name(
            item_to_select.text()
        )

        self.og_widget.label_current_project_area.setText(layer_name)

    def update_development_site_parameters(self, item: QListWidgetItem) -> None:
        """
        Updates the line edits and combobox of the development sites tab to the currently selected site.
        """
        if item:
            table_name = item.text()

            SETTINGS_MANAGER.set_current_development_site_parameter_table_name(
                table_name
            )

            with sqlite3.connect(SETTINGS_MANAGER.get_database_path()) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f"SELECT widget_name, value_float, value_string, value_bool FROM '{SETTINGS_MANAGER.development_site_parameter_prefix}{table_name}'"
                )

                widget_values_dict = {row[0]: row[1:] for row in cursor.fetchall()}
                for widget_name in widget_values_dict.keys():
                    widget = self.og_widget.findChild(QWidget, widget_name)

                    if isinstance(widget, QLineEdit):
                        widget.setText(widget_values_dict[widget_name][1])
                        print(widget_values_dict)
                    elif isinstance(widget, QComboBox):
                        widget.setCurrentIndex(int(widget_values_dict[widget_name][0]))

                self.og_widget.label_current_project_area.setText(table_name)
