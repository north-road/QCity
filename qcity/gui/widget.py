import os
import sqlite3

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox
from qgis import processing
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtCore import QCoreApplication
from qgis._core import QgsVectorLayer
from qgis.core import QgsProject
from qgis.gui import (
    QgsDockWidget,
)

from ..core import SETTINGS_MANAGER
from ..gui.gui_utils import GuiUtils
import shutil


class TabDockWidget(QgsDockWidget):
    """
    Main dock widget.
    """

    def __init__(self, project, iface) -> None:
        super(TabDockWidget, self).__init__()
        self.setObjectName("SlopeDigitizingLiveResultsDockWidget")

        uic.loadUi(GuiUtils.get_ui_file_path("dockwidget_main.ui"), self)

        self.project = project
        self.iface = iface
        self.set_base_layer_items()

        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self._default_project_area_parameters_path = os.path.join(
            self.plugin_path, "..", "data", "default_project_area_parameters.json"
        )

        self.pushButton_add_base_layer.clicked.connect(self.add_base_layers)
        self.pushButton_create_database.clicked.connect(
            self.create_new_project_database
        )
        self.pushButton_load_database.clicked.connect(self.load_project_database)

        self.toolButton_project_area_remove.clicked.connect(self.remove_selected_areas)

        self.lineEdit_current_project_area.returnPressed.connect(
            self.update_layer_name_gpkg
        )

        self.listWidget_project_areas.itemClicked.connect(
            lambda item: self.zoom_to_project_area(item)
        )

        for widget in self.findChildren((QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(
                lambda value, widget=widget: SETTINGS_MANAGER.set_spinbox_value(
                    widget, value
                )
            )  # This does work indeed, despite the marked error

        self.listWidget_project_areas.currentItemChanged.connect(
            self.update_project_area_parameters
        )

    def set_base_layer_items(self):
        """Adds all possible base layers to the selection combobox"""
        self.comboBox_base_layers.addItems(SETTINGS_MANAGER.get_base_layers_items())

    def add_base_layers(self) -> None:
        """Adds the selected layer in the combo box to the canvas."""
        base_project_path = os.path.join(
            self.plugin_path,
            "..",
            "data",
            "projects",
            f"{self.comboBox_base_layers.currentText()}.qgz",
        )
        print(base_project_path)
        temp_project = QgsProject()
        temp_project.read(base_project_path)
        layers = [layer for layer in temp_project.mapLayers().values()]

        for layer in layers:
            self.project.addMapLayer(layer)

    def create_new_project_database(self) -> None:
        """Opens a QFileDialog and returns the path to the new project Geopackage."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, self.tr("Choose Project Database Path"), "*.gpkg"
        )
        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            shutil.copyfile(
                os.path.join(
                    self.plugin_path, "..", "data", "base_project_database.gpkg"
                ),
                file_name,
            )
            self.toolButton_project_area_add.clicked.connect(self.action_maptool_emit)

            self.listWidget_project_areas.clear()
            self.lineEdit_current_project_area.setEnabled(True)

            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(None)

        else:
            # TODO: message bar here
            print("not a gpkg file")

    def load_project_database(self) -> None:
        """Loads a project database from a .gpkg file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, self.tr("Choose Project Database Path"), "*.gpkg"
        )
        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            self.toolButton_project_area_add.clicked.connect(self.action_maptool_emit)

            areas = SETTINGS_MANAGER.get_project_areas_items()
            self.listWidget_project_areas.clear()
            self.listWidget_project_areas.addItems(
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

            self.lineEdit_current_project_area.setEnabled(True)

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

    def remove_selected_areas(self) -> None:
        """Removes selected area from Qlistwidget, map and geopackage."""
        tbr_areas = self.listWidget_project_areas.selectedItems()

        if tbr_areas:
            rows = {
                self.listWidget_project_areas.row(item): item.text()
                for item in tbr_areas
            }

            for key, value in rows.items():
                self.listWidget_project_areas.takeItem(key)

                layers = self.project.mapLayersByName(value)
                if layers:
                    layer = layers[0]
                    self.project.removeMapLayer(layer.id())

                # Don't like this yet
                try:
                    conn = sqlite3.connect(SETTINGS_MANAGER.get_database_path())
                    cursor = conn.cursor()

                    cursor.execute(f"DROP TABLE '{value}'")
                    cursor.execute(
                        f"DROP TABLE '{SETTINGS_MANAGER.area_parameter_prefix}{value}'"
                    )

                    cursor.close()
                    conn.close()

                    self.iface.mapCanvas().refresh()
                except Exception as e:
                    print(f"Failed to drop table {value}: {e}")

            self.label_current_project_area.setText("Project")
            self.lineEdit_current_project_area.setText("")

    def update_layer_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        old_layer_name = self.listWidget_project_areas.selectedItems()[0]
        name = self.lineEdit_current_project_area.text()
        try:
            processing.run(
                "native:spatialiteexecutesql",
                {
                    "DATABASE": SETTINGS_MANAGER.get_database_path(),
                    "SQL": f'ALTER TABLE "{old_layer_name.text()}" RENAME TO "{name}"',
                },
            )
        except Exception as e:
            raise e

        old_item_id = self.listWidget_project_areas.row(old_layer_name)
        self.listWidget_project_areas.takeItem(old_item_id)
        self.listWidget_project_areas.addItem(name)

        self.label_current_project_area.setText(name)

    def zoom_to_project_area(self, item) -> None:
        """Sets the canvas extent to the clicked layer"""
        name = item.text()
        uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={name}"
        layer = QgsVectorLayer(uri, name, "ogr")
        extent = layer.extent()
        self.iface.mapCanvas().setExtent(extent)
        self.iface.mapCanvas().refresh()
        del layer

    def update_project_area_parameters(self) -> None:
        """
        Updates the parameter-spin-boxes of the project area to the currently selected one.
        """
        widget = (
            self.listWidget_project_areas.currentItem()
            or self.listWidget_project_areas.item(0)
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
                widget = self.findChild((QSpinBox, QDoubleSpinBox), widget_name)
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(widget_values_dict[widget.objectName()]))
                else:
                    widget.setValue(widget_values_dict[widget.objectName()])

            # Close the connection
            cursor.close()
            conn.close()

    @staticmethod
    def tr(message) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("X", message)
