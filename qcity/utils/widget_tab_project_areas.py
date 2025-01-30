import os
import shutil
import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QFileDialog,
    QListWidgetItem,
    QWidget, QListWidget,
)
from qgis.PyQt.QtCore import QObject
from qgis._core import QgsVectorLayer, QgsProject

from ..core import SETTINGS_MANAGER


class WidgetUtilsProjectArea(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self.og_widget = widget

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

                        cursor.execute(f"DROP TABLE '{table_name}'")
                        cursor.execute(
                            f"DROP TABLE '{SETTINGS_MANAGER.area_parameter_prefix}{table_name}'"
                        )
                        cursor.execute(
                            f"""DELETE FROM gpkg_contents WHERE table_name = '{SETTINGS_MANAGER.area_parameter_prefix}{table_name}';"""
                        )
                        cursor.execute(
                            f"""DELETE FROM gpkg_contents WHERE table_name = '{table_name}';"""
                        )
                        cursor.execute(
                            f"DELETE FROM gpkg_geometry_columns WHERE table_name = '{table_name}';"
                        )
                        cursor.execute(
                            f"DELETE FROM gpkg_spatial_ref_sys WHERE srs_id = '{table_name}';"
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
                    f'ALTER TABLE "{old_layer_name}" RENAME TO "{layer_name}"'
                )
                cursor.execute(
                    f"UPDATE gpkg_contents SET table_name = '{layer_name}' WHERE table_name = '{old_layer_name}';"
                )
                cursor.execute(
                    f"UPDATE gpkg_geometry_columns SET table_name = '{layer_name}' WHERE table_name = '{old_layer_name}'; "
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
        uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={name}"
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

    def add_base_layers(self) -> None:
        """Adds the selected layer in the combo box to the canvas."""
        base_project_path = os.path.join(
            self.og_widget.plugin_path,
            "..",
            "data",
            "projects",
            f"{self.og_widget.comboBox_base_layers.currentText()}.qgz",
        )
        temp_project = QgsProject()
        temp_project.read(base_project_path)
        layers = [layer for layer in temp_project.mapLayers().values()]

        for layer in layers:
            self.og_widget.project.addMapLayer(layer)

    def create_new_project_database(self, file_name: str = "") -> None:
        """Opens a QFileDialog and returns the path to the new project Geopackage."""
        # Have the file_name as an argument to enable testing
        if not file_name:
            file_name, _ = QFileDialog.getSaveFileName(
                self.og_widget,
                self.og_widget.tr("Choose Project Database Path"),
                "*.gpkg",
            )
        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            SETTINGS_MANAGER.save_database_path_with_project_name()
            shutil.copyfile(
                os.path.join(
                    self.og_widget.plugin_path,
                    "..",
                    "data",
                    "base_project_database.gpkg",
                ),
                file_name,
            )

            self.og_widget.listWidget_project_areas.clear()
            self.og_widget.lineEdit_current_project_area.setEnabled(True)

            self.og_widget.lineEdit_current_project_area.setText("")
            self.og_widget.label_current_project_area.setText("Project")

            self.enable_widgets()

            self.og_widget.toolButton_project_area_add.clicked.connect(
                self.action_maptool_emit
            )

        else:
            # TODO: message bar here
            print("not a gpkg file")

    def load_project_database(self, file_name: str = "") -> None:
        """Loads a project database from a .gpkg file."""
        # Have the file_name as an argument to enable testing
        if not file_name:
            file_name, _ = QFileDialog.getOpenFileName(
                self.og_widget,
                self.og_widget.tr("Choose Project Database Path"),
                "*.gpkg",
            )

        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            SETTINGS_MANAGER.save_database_path_with_project_name()

            self.add_layers_to_widget_and_canvas(self.og_widget.listWidget_project_areas)
            self.add_layers_to_widget_and_canvas(self.og_widget.listWidget_development_sites)

        self.og_widget.lineEdit_current_project_area.setEnabled(True)

        self.og_widget.listWidget_project_areas.setCurrentRow(0)

        self.og_widget.tabWidget_project_area_parameters.setEnabled(True)

        self.enable_widgets()

    def add_layers_to_widget_and_canvas(self, widget: QListWidget) -> None:
        all_items = SETTINGS_MANAGER.get_project_items()
        widget.clear()

        if widget.objectName() == "listWidget_development_sites":
            prefix = SETTINGS_MANAGER.development_site_prefix
            parameter_prefix = SETTINGS_MANAGER.development_site_parameter_prefix
        elif widget.objectName() == "listWidget_project_areas":
            prefix = SETTINGS_MANAGER.area_prefix
            parameter_prefix = SETTINGS_MANAGER.area_parameter_prefix

        items = [
            item
            for item in all_items
            if item.startswith(prefix)
               and not item.startswith(parameter_prefix)
        ]

        widget.addItems(
            [item[len(prefix):] for item in items]
        )

        for item in items:
            uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={item}"
            layer = QgsVectorLayer(uri, item, "ogr")

            QgsProject.instance().addMapLayer(layer)

        """if items:
            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(items[0])"""

    def action_maptool_emit(self) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.add_project_area_clicked.emit(True)

    def enable_widgets(self):
        """
        Set all widgets to be enabled.
        """
        for i in range(self.og_widget.tabWidget.count()):
            tab = self.og_widget.tabWidget.widget(i)
            for child in tab.findChildren(QWidget):
                child.setDisabled(False)
