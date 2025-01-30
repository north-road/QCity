import os
import shutil

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget, QFileDialog, QListWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication
from qgis._core import QgsVectorLayer, QgsProject
from qgis.gui import (
    QgsDockWidget,
)

from ..core import SETTINGS_MANAGER
from ..gui.gui_utils import GuiUtils
from ..utils.widget_tab_development_sites import WidgetUtilsDevelopmentSites

from ..utils.widget_tab_project_areas import WidgetUtilsProjectArea


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

        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self._default_project_area_parameters_path = os.path.join(
            self.plugin_path, "..", "data", "default_project_area_parameters.json"
        )

        # Disable everything except database buttons
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            for child in tab.findChildren(QWidget):
                if child in [
                    self.pushButton_create_database,
                    self.pushButton_load_database,
                ]:
                    continue
                child.setDisabled(True)

        # Tab no. 1 things
        util_project_area = WidgetUtilsProjectArea(self)
        self.pushButton_add_base_layer.clicked.connect(
            self.add_base_layers
        )
        self.pushButton_create_database.clicked.connect(
            self.create_new_project_database
        )
        self.pushButton_load_database.clicked.connect(
            self.load_project_database
        )

        self.toolButton_project_area_remove.clicked.connect(
            util_project_area.remove_selected_areas
        )

        self.lineEdit_current_project_area.returnPressed.connect(
            util_project_area.update_layer_name_gpkg
        )

        self.listWidget_project_areas.itemClicked.connect(
            lambda item: util_project_area.zoom_to_project_area(item)
        )

        for widget in self.findChildren((QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(
                lambda value, widget=widget: SETTINGS_MANAGER.set_spinbox_value(
                    widget, value
                )
            )  # This does work indeed, despite the marked error

        self.listWidget_project_areas.currentItemChanged.connect(
            lambda item: util_project_area.update_project_area_parameters(item)
        )

        # Tab no.2 things
        util_development_site = WidgetUtilsDevelopmentSites(self)

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
                    self.plugin_path,
                    "..",
                    "data",
                    "base_project_database.gpkg",
                ),
                file_name,
            )

            self.listWidget_project_areas.clear()
            self.lineEdit_current_project_area.setEnabled(True)

            self.lineEdit_current_project_area.setText("")
            self.label_current_project_area.setText("Project")

            self.enable_widgets()

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

        self.lineEdit_current_project_area.setEnabled(True)

        self.listWidget_project_areas.setCurrentRow(0)

        self.tabWidget_project_area_parameters.setEnabled(True)

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

    def add_base_layers(self) -> None:
        """Adds the selected layer in the combo box to the canvas."""
        base_project_path = os.path.join(
            self.plugin_path,
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

    def enable_widgets(self):
        """
        Set all widgets to be enabled.
        """
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            for child in tab.findChildren(QWidget):
                child.setDisabled(False)

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
