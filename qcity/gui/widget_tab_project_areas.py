import sqlite3

from qgis.PyQt.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QListWidgetItem,
)
from qgis.PyQt.QtCore import QObject, Qt
from qgis.core import QgsVectorLayer

from qcity.core import SETTINGS_MANAGER


class WidgetUtilsProjectArea(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self.og_widget = widget

        self.og_widget.toolButton_project_area_add.clicked.connect(
            self.action_maptool_emit
        )

        self.og_widget.toolButton_project_area_remove.clicked.connect(
            self.remove_selected_areas
        )

        self.og_widget.lineEdit_current_project_area.returnPressed.connect(
            self.update_layer_name_gpkg
        )

        self.og_widget.listWidget_project_areas.itemClicked.connect(
            lambda item: self.zoom_to_project_area(item)
        )

        for widget in self.findChildren((QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(
                lambda value, widget=widget: SETTINGS_MANAGER.set_spinbox_value(
                    widget, value
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
        """Removes selected area from Qlistwidget, map and geopackage."""
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
                    layer = layers[0]
                    self.og_widget.project.removeMapLayer(layer.id())

                try:
                    with sqlite3.connect(SETTINGS_MANAGER.get_database_path()) as conn:
                        cursor = conn.cursor()

                        cursor.execute(
                            f"DROP TABLE '{SETTINGS_MANAGER.area_prefix}{table_name}'"
                        )
                        cursor.execute(
                            f"DROP TABLE '{SETTINGS_MANAGER.area_parameter_prefix}{table_name}'"
                        )
                        cursor.execute(
                            f"""DELETE FROM gpkg_contents WHERE table_name = '{SETTINGS_MANAGER.area_parameter_prefix}{table_name}';"""
                        )
                        cursor.execute(
                            f"""DELETE FROM gpkg_contents WHERE table_name = '{SETTINGS_MANAGER.area_prefix}{table_name}';"""
                        )
                        cursor.execute(
                            f"DELETE FROM gpkg_geometry_columns WHERE table_name = '{SETTINGS_MANAGER.area_prefix}{table_name}';"
                        )
                        cursor.execute(
                            f"DELETE FROM gpkg_spatial_ref_sys WHERE srs_id = '{SETTINGS_MANAGER.area_prefix}{table_name}';"
                        )

                    self.og_widget.iface.mapCanvas().refresh()
                except Exception as e:
                    raise e

            self.og_widget.label_current_project_area.setText("Project")
            self.og_widget.lineEdit_current_project_area.setText("")

            if self.og_widget.listWidget_project_areas.count() < 1:
                SETTINGS_MANAGER.set_current_project_area_parameter_table_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                self.og_widget.tabWidget_project_area_parameters.setEnabled(False)

    def update_layer_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.og_widget.listWidget_project_areas.selectedItems()[0]
        old_layer_name = widget.text()
        layer_name = self.og_widget.lineEdit_current_project_area.text()

        old_item_id = self.og_widget.listWidget_project_areas.row(widget)
        self.og_widget.listWidget_project_areas.takeItem(old_item_id)
        self.og_widget.listWidget_project_areas.addItem(layer_name)

        try:
            database_path = SETTINGS_MANAGER.get_database_path()
            with sqlite3.connect(database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f'ALTER TABLE "{SETTINGS_MANAGER.area_prefix}{old_layer_name}" RENAME TO "{SETTINGS_MANAGER.area_prefix}{layer_name}"'
                )
                cursor.execute(
                    f"UPDATE gpkg_contents SET table_name = '{SETTINGS_MANAGER.area_prefix}{layer_name}' WHERE table_name = '{SETTINGS_MANAGER.area_prefix}{old_layer_name}';"
                )
                cursor.execute(
                    f"UPDATE gpkg_geometry_columns SET table_name = '{SETTINGS_MANAGER.area_prefix}{layer_name}' WHERE table_name = '{SETTINGS_MANAGER.area_prefix}{old_layer_name}'; "
                )

                parameter_name = f"{SETTINGS_MANAGER.area_parameter_prefix}{layer_name}"
                old_parameter_name = (
                    f"{SETTINGS_MANAGER.area_parameter_prefix}{old_layer_name}"
                )
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
        item_to_select = self.og_widget.listWidget_project_areas.findItems(
            layer_name, Qt.MatchExactly
        )[0]
        self.og_widget.listWidget_project_areas.setCurrentItem(item_to_select)
        SETTINGS_MANAGER.set_current_project_area_parameter_table_name(
            item_to_select.text()
        )

        self.og_widget.label_current_project_area.setText(layer_name)

    def zoom_to_project_area(self, item) -> None:
        """Sets the canvas extent to the clicked layer"""
        name = item.text()
        SETTINGS_MANAGER.set_current_project_area_parameter_table_name(name)
        uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.area_prefix}{name}"
        layer = QgsVectorLayer(uri, name, "ogr")
        extent = layer.extent()
        self.og_widget.iface.mapCanvas().setExtent(extent)
        self.og_widget.iface.mapCanvas().refresh()
        del layer

    def update_project_area_parameters(self, item: QListWidgetItem) -> None:
        """
        Updates the parameter-spin-boxes of the project area to the currently selected one.
        """
        if item:
            table_name = item.text()

            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(table_name)

            with sqlite3.connect(SETTINGS_MANAGER.get_database_path()) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f"SELECT widget_name, value FROM '{SETTINGS_MANAGER.area_parameter_prefix}{table_name}'"
                )

                widget_values_dict = {row[0]: row[1] for row in cursor.fetchall()}
                for widget_name in widget_values_dict.keys():
                    widget = self.og_widget.findChild(
                        (QSpinBox, QDoubleSpinBox), widget_name
                    )
                    if isinstance(widget, QSpinBox):
                        widget.setValue(int(widget_values_dict[widget_name]))
                    else:
                        widget.setValue(widget_values_dict[widget_name])

                self.og_widget.label_current_project_area.setText(table_name)

    def action_maptool_emit(self) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.add_project_area_clicked.emit(True)
