from typing import Optional

import json
import os
import shutil

from qgis.PyQt.QtWidgets import (
    QWidget,
    QFileDialog,
    QGraphicsOpacityEffect,
    QListWidgetItem,
)
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication, Qt, QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsVectorFileWriter,
    QgsFields,
    QgsField,
    QgsCoordinateTransformContext,
    QgsFeatureRequest,
    QgsVectorLayer,
    QgsProject,
    QgsFeature,
    Qgis,
    QgsFileUtils,
    QgsRelation,
)
from qgis.gui import QgsDockWidget, QgsCollapsibleGroupBox

from .widget_tab_building_levels import WidgetUtilsBuildingLevels
from .widget_tab_statistics import WidgetUtilsStatistics
from ..core import SETTINGS_MANAGER
from ..gui.gui_utils import GuiUtils
from qcity.gui.widget_tab_development_sites import WidgetUtilsDevelopmentSites

from qcity.gui.widget_tab_project_areas import WidgetUtilsProjectArea
from ..utils.utils import get_qgis_type
from ..core.database import DatabaseUtils
from ..core.project import ProjectUtils


class TabDockWidget(QgsDockWidget):
    """
    Main dock widget.
    """

    def __init__(self, project, iface) -> None:
        super(TabDockWidget, self).__init__()
        self.setObjectName("MainDockWidget")

        uic.loadUi(GuiUtils.get_ui_file_path("dockwidget_main.ui"), self)

        self.toolButton_project_area_add.setIcon(GuiUtils.get_icon('add.svg'))
        self.toolButton_project_area_remove.setIcon(GuiUtils.get_icon('remove.svg'))
        self.toolButton_project_area_rename.setIcon(GuiUtils.get_icon('rename.svg'))
        self.pushButton_import_project_areas.setIcon(GuiUtils.get_icon('import.svg'))

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
        WidgetUtilsBuildingLevels(self)
        WidgetUtilsStatistics(self)

    def set_add_button_activation(self) -> None:
        """Sets the add button for the base layers enabled/disabled, based on the current item text"""
        if self.comboBox_base_layers.currentIndex() == "Add base layers":
            self.pushButton_add_base_layer.setEnabled(False)
        else:
            self.pushButton_add_base_layer.setEnabled(True)

    def set_base_layer_items(self):
        """Adds all possible base layers to the selection combobox"""
        self.comboBox_base_layers.addItems(SETTINGS_MANAGER.get_base_layers_items())

    def create_new_project_database(self, file_name: Optional[str] = None, selected_filter: str = ".gpkg") -> None:
        """Opens a QFileDialog and returns the path to the new project Geopackage."""
        # Have the file_name as an argument to enable testing
        if not file_name:
            file_name, selected_filter = QFileDialog.getSaveFileName(
                self, self.tr("Choose Project Database Path"),
                SETTINGS_MANAGER.last_used_database_folder(),
                "GeoPackage (*.gpkg)"
            )

        if not file_name:
            return None

        file_name = QgsFileUtils.addExtensionFromFilter(file_name, selected_filter)
        SETTINGS_MANAGER.set_last_used_database_folder(os.path.split(file_name)[0])

        SETTINGS_MANAGER.set_database_path(file_name)

        self.listWidget_project_areas.clear()
        self.label_current_project_area.setText("Project")

        self.listWidget_development_sites.clear()
        self.label_current_development_site.setText("Project")

        gpkg_path = SETTINGS_MANAGER.get_database_path()

        DatabaseUtils.create_base_tables(
            gpkg_path
        )

        self.enable_widgets()

        ProjectUtils.set_associated_database_path(self.project, gpkg_path)
        ProjectUtils.add_database_layers_to_project(self.project, gpkg_path)
        ProjectUtils.create_layer_relations(self.project)

        self.iface.messageBar().pushMessage(
            self.tr("Success"),
            self.tr(f"Project database created: {file_name}"),
            level=Qgis.Success,
        )

    def load_project_database(self, file_name: str, selected_filter: str = "") -> None:
        """Loads a project database from a .gpkg file."""
        # Have the file_name as an argument to enable testing
        if not file_name:
            file_name, selected_filter = QFileDialog.getOpenFileName(
                self, self.tr("Choose Project Database Path"),
                SETTINGS_MANAGER.last_used_database_folder(),
                "GeoPackage (*.gpkg)"
            )

        if file_name == "":
            return None

        file_name = QgsFileUtils.addExtensionFromFilter(file_name, selected_filter)
        SETTINGS_MANAGER.set_last_used_database_folder(os.path.split(file_name)[0])

        self.listWidget_project_areas.clear()
        SETTINGS_MANAGER.set_database_path(file_name)

        ProjectUtils.set_associated_database_path(self.project, file_name)
        ProjectUtils.add_database_layers_to_project(self.project, file_name)
        area_layer = ProjectUtils.get_project_area_layer(self.project)
        feats = area_layer.getFeatures()
        for feat in feats:
            self.listWidget_project_areas.addItem(feat["name"])

        # Click on first project area item to initialize all other listwidgets
        for widget in [
            self.listWidget_project_areas,
            self.listWidget_development_sites,
            self.listWidget_building_levels,
        ]:
            widget.setCurrentRow(0)
            item = widget.currentItem()
            if item:
                widget.itemClicked.emit(item)

        self.groupbox_dwellings.setEnabled(True)
        self.groupbox_car_parking.setEnabled(True)
        self.groupbox_bike_parking.setEnabled(True)

        self.enable_widgets()

        ProjectUtils.create_layer_relations(self.project)

        self.iface.messageBar().pushMessage(
            self.tr("Success"),
            self.tr(f"Project database loaded: {file_name}"),
            level=Qgis.Success,
        )

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
                if isinstance(child, QgsCollapsibleGroupBox):
                    child.setCollapsed(True)
                child.setDisabled(True)

    @staticmethod
    def tr(message: str) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("X", message)

    def get_feature_of_layer_by_name(
        self, layer: QgsVectorLayer, item: QListWidgetItem
    ) -> QgsFeature:
        """Returns the feature with the name of the item"""
        filter_expression = f"\"name\" = '{item.text()}'"
        request = QgsFeatureRequest().setFilterExpression(filter_expression)
        iterator = layer.getFeatures(request)

        return next(iterator)

    def action_maptool_emit(self, kind: str) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.current_digitisation_type = kind
        SETTINGS_MANAGER.add_feature_clicked.emit(True)
