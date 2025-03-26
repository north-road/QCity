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

    def create_new_project_database(self, file_name: str = "") -> None:
        """Opens a QFileDialog and returns the path to the new project Geopackage."""
        # Have the file_name as an argument to enable testing
        if not file_name:
            file_name, selected_filter = QFileDialog.getSaveFileName(
                self, self.tr("Choose Project Database Path"), "", "GeoPackage (*.gpkg)"
            )

        if file_name == "":
            return None

        file_name = QgsFileUtils.addExtensionFromFilter(file_name, selected_filter)

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
            SETTINGS_MANAGER.project_area_prefix,
            SETTINGS_MANAGER._default_project_area_parameters_path,
        )
        self.create_base_tables(
            SETTINGS_MANAGER.development_site_prefix,
            SETTINGS_MANAGER._default_project_development_site_path,
        )
        self.create_base_tables(
            SETTINGS_MANAGER.building_level_prefix,
            SETTINGS_MANAGER._default_project_building_level_path,
        )

        self.enable_widgets()

        self.add_area_and_site_layers_to_canvas()

        self.add_layer_relations()

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
                self, self.tr("Choose Project Database Path"), "", "GeoPackage (*.gpkg)"
            )

        if file_name == "":
            return None

        file_name = QgsFileUtils.addExtensionFromFilter(file_name, selected_filter)

        self.listWidget_project_areas.clear()
        SETTINGS_MANAGER.set_database_path(file_name)
        SETTINGS_MANAGER.save_database_path_with_project_name()

        self.add_area_and_site_layers_to_canvas()
        feats = self.area_layer.getFeatures()
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

        self.add_layer_relations()

        self.iface.messageBar().pushMessage(
            self.tr("Success"),
            self.tr(f"Project database loaded: {file_name}"),
            level=Qgis.Success,
        )

    def add_area_and_site_layers_to_canvas(self) -> None:
        """Adds the layers from the gpkg to the canvas"""
        # TODO: Rename method to mention all layers are loaded
        database_path = SETTINGS_MANAGER.get_database_path()

        self.area_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.project_area_prefix}",
            SETTINGS_MANAGER.project_area_prefix,
            "ogr",
        )
        self.development_site_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.development_site_prefix}",
            SETTINGS_MANAGER.development_site_prefix,
            "ogr",
        )
        self.building_level_layer = QgsVectorLayer(
            f"{database_path}|layername={SETTINGS_MANAGER.building_level_prefix}",
            SETTINGS_MANAGER.building_level_prefix,
            "ogr",
        )

        for layer in (
            self.area_layer,
            self.development_site_layer,
            self.building_level_layer,
        ):
            QgsProject.instance().addMapLayer(layer)

        SETTINGS_MANAGER.set_project_layer_ids(
            self.area_layer, self.development_site_layer, self.building_level_layer
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

    def create_base_tables(self, table_name: str, path: str) -> None:
        """Creates a GeoPackage layer with attributes based on JSON data."""
        gpkg_path = SETTINGS_MANAGER.get_database_path()

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

    def add_layer_relations(self) -> None:
        """Adds relations between layers to the QGIS project."""
        relation_manager = self.project.relationManager()
        existing_relations = {rel.name() for rel in relation_manager.relations().values()}

        if "project_area_to_development_sites" in existing_relations and "development_sites_to_building_levels" in existing_relations:
            return None

        project_area_layer = self.project.mapLayer(SETTINGS_MANAGER.get_project_area_layer_id())
        development_site_layer = self.project.mapLayer(SETTINGS_MANAGER.get_development_site_layer_id())
        building_level_layer = self.project.mapLayer(SETTINGS_MANAGER.get_building_level_layer_id())

        relations = [
            ("project_area_to_development_sites", project_area_layer, development_site_layer),
            ("development_sites_to_building_levels", development_site_layer, building_level_layer),
        ]

        for name, ref_layer, refg_layer in relations:
            relation = QgsRelation()
            relation.setName(name)
            relation.setReferencedLayer(ref_layer.id())
            relation.setReferencingLayer(refg_layer.id())
            relation.addFieldPair("primary_key", "fid")
            relation.setId(f"relation_id_{refg_layer.name()}_{ref_layer.name()}")
            relation.setStrength(QgsRelation.Association)
            relation_manager.addRelation(relation)
