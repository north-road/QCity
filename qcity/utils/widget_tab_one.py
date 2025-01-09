import os
import shutil
import sqlite3

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QFileDialog
from qgis.PyQt.QtCore import QObject
from qgis._core import QgsVectorLayer, QgsProject

from ..core import SETTINGS_MANAGER

class WidgetUtilsProjectArea(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self.og_widget = widget

    def remove_selected_areas(self) -> None:
        """Removes selected area from Qlistwidget, map and geopackage."""
        tbr_areas = self.og_widget.listWidget_project_areas.selectedItems()

        if tbr_areas:
            rows = {
                self.og_widget.listWidget_project_areas.row(item): item.text()
                for item in tbr_areas
            }

            for key, value in rows.items():
                self.og_widget.listWidget_project_areas.takeItem(key)

                layers = self.og_widget.project.mapLayersByName(value)
                if layers:
                    layer = layers[0]
                    self.og_widget.project.removeMapLayer(layer.id())

                try:
                    conn = sqlite3.connect(SETTINGS_MANAGER.get_database_path())
                    cursor = conn.cursor()

                    cursor.execute(f"DROP TABLE '{value}'")
                    cursor.execute(
                        f"DROP TABLE '{SETTINGS_MANAGER.area_parameter_prefix}{value}'"
                    )

                    cursor.close()
                    conn.close()

                    self.og_widget.iface.mapCanvas().refresh()
                except Exception as e:
                    print(f"Failed to drop table {value}: {e}")

            self.og_widget.label_current_project_area.setText("Project")
            self.og_widget.lineEdit_current_project_area.setText("")


    def update_layer_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.og_widget.listWidget_project_areas.selectedItems()[0]
        old_layer_name = widget.text()
        layer_name = self.og_widget.lineEdit_current_project_area.text()
        try:
            database_path = SETTINGS_MANAGER.get_database_path()
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()

            cursor.execute(f'ALTER TABLE "{old_layer_name}" RENAME TO "{layer_name}"')
            cursor.execute(f'ALTER TABLE "{SETTINGS_MANAGER.area_parameter_prefix}{old_layer_name}" RENAME TO "{SETTINGS_MANAGER.area_parameter_prefix}{layer_name}"')

            self.og_widget.project.removeMapLayer(self.og_widget.project.mapLayersByName(old_layer_name)[0].id())
            uri = f"{database_path}|layername={layer_name}"
            layer = QgsVectorLayer(uri, layer_name, "ogr")
            QgsProject.instance().addMapLayer(layer)

            cursor.close()
            conn.close()
        except Exception as e:
            raise e

        old_item_id = self.og_widget.listWidget_project_areas.row(widget)
        self.og_widget.listWidget_project_areas.takeItem(old_item_id)
        self.og_widget.listWidget_project_areas.addItem(layer_name)

        self.og_widget.label_current_project_area.setText(layer_name)

    def zoom_to_project_area(self, item) -> None:
        """Sets the canvas extent to the clicked layer"""
        name = item.text()
        uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={name}"
        layer = QgsVectorLayer(uri, name, "ogr")
        extent = layer.extent()
        self.og_widget.iface.mapCanvas().setExtent(extent)
        self.og_widget.iface.mapCanvas().refresh()
        del layer

    def update_project_area_parameters(self) -> None:
        """
        Updates the parameter-spin-boxes of the project area to the currently selected one.
        """
        widget = (
            self.og_widget.listWidget_project_areas.currentItem()
            or self.og_widget.listWidget_project_areas.item(0)
        )

        if widget:
            table_name = widget.text()

            if SETTINGS_MANAGER.area_parameter_prefix in table_name:
                SETTINGS_MANAGER.set_current_project_area_parameter_table_name(
                    table_name
                )
            else:
                SETTINGS_MANAGER.set_current_project_area_parameter_table_name(
                    f"{SETTINGS_MANAGER.area_parameter_prefix}{table_name}"
                )

            conn = sqlite3.connect(SETTINGS_MANAGER.get_database_path())
            cursor = conn.cursor()

            cursor.execute(
                f"SELECT widget_name, value FROM {SETTINGS_MANAGER.get_current_project_area_parameter_table_name()}"
            )

            widget_values_dict = {row[0]: row[1] for row in cursor.fetchall()}

            for widget_name in widget_values_dict.keys():
                widget = self.og_widget.findChild((QSpinBox, QDoubleSpinBox), widget_name)
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(widget_values_dict[widget.objectName()]))
                else:
                    widget.setValue(widget_values_dict[widget.objectName()])

            # Close the connection
            cursor.close()
            conn.close()

    def add_base_layers(self) -> None:
        """Adds the selected layer in the combo box to the canvas."""
        base_project_path = os.path.join(
            self.og_widget.plugin_path,
            "..",
            "data",
            "projects",
            f"{self.og_widget.comboBox_base_layers.currentText()}.qgz",
        )
        print(base_project_path)
        temp_project = QgsProject()
        temp_project.read(base_project_path)
        layers = [layer for layer in temp_project.mapLayers().values()]

        for layer in layers:
            self.og_widget.project.addMapLayer(layer)

    def create_new_project_database(self) -> None:
        """Opens a QFileDialog and returns the path to the new project Geopackage."""
        file_name, _ = QFileDialog.getSaveFileName(
            self.og_widget, self.og_widget.tr("Choose Project Database Path"), "*.gpkg"
        )
        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            shutil.copyfile(
                os.path.join(
                    self.og_widget.plugin_path, "..", "data", "base_project_database.gpkg"
                ),
                file_name,
            )
            self.og_widget.toolButton_project_area_add.clicked.connect(self.action_maptool_emit)

            self.og_widget.listWidget_project_areas.clear()
            self.og_widget.lineEdit_current_project_area.setEnabled(True)

            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(None)

            self.og_widget.lineEdit_current_project_area.setText("")
            self.og_widget.label_current_project_area.setText("Project")

        else:
            # TODO: message bar here
            print("not a gpkg file")

    def load_project_database(self) -> None:
        """Loads a project database from a .gpkg file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self.og_widget, self.og_widget.tr("Choose Project Database Path"), "*.gpkg"
        )
        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            self.og_widget.toolButton_project_area_add.clicked.connect(self.action_maptool_emit)

            areas = SETTINGS_MANAGER.get_project_areas_items()
            self.og_widget.listWidget_project_areas.clear()
            self.og_widget.listWidget_project_areas.addItems(
                [
                    item
                    for item in areas
                    if SETTINGS_MANAGER.area_parameter_prefix not in item
                ]
            )

            for area in areas:
                if "" not in area:
                    uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={area}"
                    layer = QgsVectorLayer(uri, area, "ogr")
                    QgsProject.instance().addMapLayer(layer)

            self.og_widget.lineEdit_current_project_area.setEnabled(True)

            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(None)
            for area in areas:
                # take the first areas' parameter file and use that
                if SETTINGS_MANAGER.area_parameter_prefix in area:
                    SETTINGS_MANAGER.set_current_project_area_parameter_table_name(area)
                    self.update_project_area_parameters()
                    break

    def action_maptool_emit(self) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.add_project_area_clicked.emit(True)