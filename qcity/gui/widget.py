import os

from qgis import processing
from qgis.PyQt import uic, sip
from qgis.PyQt.QtWidgets import QFrame, QWidget, QComboBox, QFileDialog
from qgis.PyQt.QtCore import QCoreApplication
from qgis._core import QgsVectorLayer
from qgis.core import QgsProject, Qgis, QgsUnitTypes, QgsStringUtils
from qgis.gui import (
    QgsColorButton,
    QgsDoubleSpinBox,
    QgsPanelWidget,
    QgsDockWidget,
    QgsPanelWidgetStack,
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
        self.database_pat: str = None
        self.setObjectName("SlopeDigitizingLiveResultsDockWidget")

        uic.loadUi(GuiUtils.get_ui_file_path("dockwidget_main.ui"), self)

        self.project = project
        self.iface = iface
        self.set_base_layer_items()

        self.plugin_path = os.path.dirname(os.path.realpath(__file__))

        self.pushButton_add_base_layer.clicked.connect(self.add_base_layers)
        self.pushButton_create_database.clicked.connect(
            self.create_new_project_database
        )
        self.pushButton_load_database.clicked.connect(
            self.load_project_database
        )

        self.toolButton_project_area_remove.clicked.connect(self.remove_selected_areas)


    def set_base_layer_items(self):
        self.comboBox_base_layers.addItems(SETTINGS_MANAGER.get_base_layers_items())

    def add_base_layers(self) -> None:
        """Adds the selected layer in the combo box to the canvas."""
        base_project_path = os.path.join(
            self.plugin_path,
            "..",
            "data",
            f"{self.comboBox_base_layers.currentText()}.qgz",
        )
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
                os.path.join(self.plugin_path, "..", "base_project_database.gpkg"),
                file_name,
            )
            self.toolButton_project_area_add.clicked.connect(
                self.action_maptool_emit
            )


    def load_project_database(self) -> None:
        """Loads a project database from a .gpkg file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, self.tr("Choose Project Database Path"), "*.gpkg"
        )
        if file_name and file_name.endswith(".gpkg"):
            SETTINGS_MANAGER.set_database_path(file_name)
            self.toolButton_project_area_add.clicked.connect(
                self.action_maptool_emit
            )

            areas = SETTINGS_MANAGER.get_project_areas_items()
            self.listWidget_project_areas.clear()
            self.listWidget_project_areas.addItems(areas)

            for area in areas:
                uri = f"{SETTINGS_MANAGER.get_database_path()}|layername={area}"
                layer = QgsVectorLayer(uri, area, 'ogr')
                QgsProject.instance().addMapLayer(layer)


    def action_maptool_emit(self):
        """ Emitted when plus button is clicked. """
        SETTINGS_MANAGER.add_project_area_clicked.emit(True)

    def remove_selected_areas(self):
        """ Removes selected area from Qlistwidget, map and geopackage. """
        tbr_areas = self.listWidget_project_areas.selectedItems()

        if tbr_areas:
            rows = {self.listWidget_project_areas.row(item): item.text() for item in tbr_areas}

            for key, value in rows.items():
                self.listWidget_project_areas.takeItem(key)

                layers = self.project.mapLayersByName(value)
                if layers:
                    layer = layers[0]
                    self.project.removeMapLayer(layer.id())

                # Don't like this yet
                try:
                    processing.run(
                        "native:spatialiteexecutesql",
                        {
                            'DATABASE': f"{SETTINGS_MANAGER.get_database_path()}|layername={value}",
                            'SQL': f"DROP TABLE \"{value}\""
                        }
                    )
                    self.iface.mapCanvas().refresh()
                except Exception as e:
                    print(f"Failed to drop table {value}: {e}")

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
