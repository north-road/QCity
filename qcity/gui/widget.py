import os

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication
from qgis.gui import (
    QgsDockWidget,
)

from ..core import SETTINGS_MANAGER
from ..gui.gui_utils import GuiUtils

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
            util_project_area.add_base_layers
        )
        self.pushButton_create_database.clicked.connect(
            util_project_area.create_new_project_database
        )
        self.pushButton_load_database.clicked.connect(
            util_project_area.load_project_database
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

    def set_base_layer_items(self):
        """Adds all possible base layers to the selection combobox"""
        self.comboBox_base_layers.addItems(SETTINGS_MANAGER.get_base_layers_items())

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
