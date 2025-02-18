import json
import os
import shutil

from qgis.PyQt.QtWidgets import (
    QWidget,
    QFileDialog,
    QListWidget,
    QGraphicsOpacityEffect,
)
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication, Qt, QVariant
from qgis.PyQt.QtGui import QColor
from qgis._core import (
    QgsVectorFileWriter,
    QgsFields,
    QgsField,
    QgsCoordinateTransformContext,
)
from qgis.core import QgsVectorLayer, QgsProject
from qgis.gui import (
    QgsDockWidget,
)

from ..core import SETTINGS_MANAGER
from ..gui.gui_utils import GuiUtils
from qcity.gui.widget_tab_development_sites import WidgetUtilsDevelopmentSites

from qcity.gui.widget_tab_project_areas import WidgetUtilsProjectArea


class TabDockWidget(QgsDockWidget):
    """
    Main dock widget.
    """

    def __init__(self, project, iface) -> None:
        super(TabDockWidget, self).__init__()
        self.setObjectName("MainDockWidget")

        uic.loadUi(GuiUtils.get_ui_file_path("dockwidget_main.ui"), self)

        self.project = project
        self.iface = iface
        self.set_base_layer_items()

        self.opacity_effect = QGraphicsOpacityEffect()

        self.disable_widgets()

        self.pushButton_add_base_layer.clicked.connect(self.add_base_layers)
        self.pushButton_create_database.clicked.connect(
            self.create_new_project_database
        )
        self.pushButton_load_database.clicked.connect(self.load_project_database)

        self.comboBox_base_layers.currentIndexChanged.connect(
            self.set_add_button_activation
        )
        self.comboBox_base_layers.setItemData(
            0, QColor(0, 0, 0, 100), Qt.ItemDataRole.ForegroundRole
        )

        # Initialize tabs
        WidgetUtilsProjectArea(self)
        WidgetUtilsDevelopmentSites(self)

    def set_add_button_activation(self) -> None:
        """Sets the add button for the base layers enabled/disabled, based on the current item text"""
        if self.comboBox_base_layers.currentIndex() == "Add base layers":
            self.pushButton_add_base_layer.setEnabled(False)
        else:
            self.pushButton_add_base_layer.setEnabled(True)

    def set_base_layer_items(self):
        """Adds all possible base layers to the selection combobox"""
        self.comboBox_base_layers.addItems(SETTINGS_MANAGER.get_base_layers_items())

    def create_new_project_database(self, file_name: str = "") -> None:
        """Opens a QFileDialog and returns the path to the new project Geopackage."""
        # Have the file_name as an argument to enable testing
        if not file_name:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                self.tr("Choose Project Database Path"),
                "*.gpkg",
            )
        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            SETTINGS_MANAGER.save_database_path_with_project_name()
            shutil.copyfile(
                os.path.join(
                    SETTINGS_MANAGER.plugin_path,
                    "..",
                    "data",
                    "base_project_database.gpkg",
                ),
                file_name,
            )

            self.listWidget_project_areas.clear()
            self.label_current_project_area.setText("Project")

            self.listWidget_development_sites.clear()
            self.label_current_development_site.setText("Project")

            self.create_base_tables(
                SETTINGS_MANAGER.area_prefix,
                SETTINGS_MANAGER._default_project_area_parameters_path,
            )
            self.create_base_tables(
                SETTINGS_MANAGER.development_site_prefix,
                SETTINGS_MANAGER._default_project_development_site_path,
            )

            self.enable_widgets()

            uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.area_prefix}"
            self.area_layer = QgsVectorLayer(uri, SETTINGS_MANAGER.area_prefix, "ogr")

            uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.development_site_prefix}"
            self.dev_site_layer = QgsVectorLayer(
                uri, SETTINGS_MANAGER.development_site_prefix, "ogr"
            )

            QgsProject.instance().addMapLayer(self.area_layer)
            QgsProject.instance().addMapLayer(self.dev_site_layer)

            SETTINGS_MANAGER.set_project_layer_ids(self.area_layer, self.dev_site_layer)

        else:
            # TODO: message bar here
            print("not a gpkg file")

    def load_project_database(self, file_name: str = "") -> None:
        """Loads a project database from a .gpkg file."""
        # Have the file_name as an argument to enable testing
        if not file_name:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                self.tr("Choose Project Database Path"),
                "*.gpkg",
            )

        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            SETTINGS_MANAGER.save_database_path_with_project_name()

            self.add_layers_to_widget_and_canvas(self.listWidget_project_areas)
            self.add_layers_to_widget_and_canvas(self.listWidget_development_sites)

        self.listWidget_project_areas.setCurrentRow(0)

        self.groupbox_dwellings.setEnabled(True)
        self.groupbox_car_parking.setEnabled(True)
        self.groupbox_bike_parking.setEnabled(True)

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
            if item.startswith(prefix) and not item.startswith(parameter_prefix)
        ]

        widget.addItems([item[len(prefix) :] for item in items])

        for item in items:
            uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={item}"
            layer = QgsVectorLayer(uri, item, "ogr")

            QgsProject.instance().addMapLayer(layer)

        """if items:
            SETTINGS_MANAGER.set_current_project_area_parameter_table_name(items[0])"""

    def add_base_layers(self) -> None:
        """Adds the selected layer in the combo box to the canvas."""
        base_project_path = os.path.join(
            SETTINGS_MANAGER.plugin_path,
            "..",
            "data",
            "projects",
            f"{self.comboBox_base_layers.currentText()}.qgz",
        )
        temp_project = QgsProject()
        temp_project.read(base_project_path)
        layers = [layer for layer in temp_project.mapLayers().values()]

        for layer in layers:
            self.project.addMapLayer(layer)

        self.comboBox_base_layers.setCurrentIndex(0)
        self.pushButton_add_base_layer.setEnabled(False)

    def enable_widgets(self) -> None:
        """
        Set all widgets to be enabled.
        """
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            for child in tab.findChildren(QWidget):
                child.setDisabled(False)

        self.pushButton_add_base_layer.setEnabled(False)

    def disable_widgets(self) -> None:
        """
        Set all widgets to be disabled except database buttons.
        """
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            for child in tab.findChildren(QWidget):
                if child in [
                    self.pushButton_create_database,
                    self.pushButton_load_database,
                ]:
                    continue
                child.setDisabled(True)

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

    def create_base_tables(self, table_name: str, path: str) -> QgsVectorLayer:
        """Creates a GeoPackage layer with attributes based on JSON data."""
        gpkg_path = SETTINGS_MANAGER.get_database_path()

        get_qgis_type = lambda key: (
            QVariant.Double
            if "doubleSpinBox" in key
            else QVariant.Int
            if "spinBox" in key or "comboBox" in key
            else QVariant.String
            if "lineEdit" in key
            else QVariant.String
        )

        with open(path, "r") as file:
            data = json.load(file)

        fields = QgsFields()
        fields.append(QgsField("name", QVariant.String))
        for key in data.keys():
            fields.append(QgsField(key, get_qgis_type(key)))

        layer = QgsVectorLayer("Polygon?crs=EPSG:4326", table_name, "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = table_name
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

        error = QgsVectorFileWriter.writeAsVectorFormatV2(
            layer, gpkg_path, QgsCoordinateTransformContext(), options
        )

        if not error[0] == QgsVectorFileWriter.NoError:
            raise Exception(f"Error adding layer to GeoPackage: {error[1]}")
