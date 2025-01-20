import unittest
import os

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis._core import QgsCoordinateReferenceSystem

from qgis.core import (
    QgsProject,
    QgsSettings,
)

from qcity.gui.widget import TabDockWidget
from qcity.test.utilities import get_qgis_app
from qcity.utils.widget_tab_project_areas import WidgetUtilsProjectArea

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class QCityProjectAreaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCiy_project_areas")
        QCoreApplication.setOrganizationDomain("qcity_project_areas")
        QCoreApplication.setApplicationName("qcity_project_areas")

        _, CANVAS, cls.iface, cls.PARENT = get_qgis_app()
        QgsSettings().clear()

        cls.project = QgsProject()

        cls.CANVAS = CANVAS
        cls.CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3857"))
        cls.CANVAS.setFrameStyle(0)
        cls.CANVAS.resize(600, 400)
        assert cls.CANVAS.width() == 600
        assert cls.CANVAS.height() == 400

    def test_create_database(self) -> None:
        widget = TabDockWidget(self.project, self.iface)
        path = os.path.join(test_data_path, "test_database.gpkg")
        WidgetUtilsProjectArea(widget).create_new_project_database(path)

        self.assertTrue(
            os.path.exists(os.path.join(test_data_path, "test_database.gpkg"))
        )
        self.assertEqual(widget.label_current_project_area.text(), "Project")

        os.remove(path)

    def test_add_base_layers(self) -> None:
        widget = TabDockWidget(self.project, self.iface)
        WidgetUtilsProjectArea(widget).add_base_layers()

        # This needs to be updated if the base layers are changed
        layer_name = "test_point_4326"
        layers = self.project.mapLayersByName(layer_name)
        self.assertTrue(layers is not None)

    def test_load_project(self) -> None:
        path = os.path.join(test_data_path, "filled_test_database.gpkg")
        widget = TabDockWidget(self.project, self.iface)
        WidgetUtilsProjectArea(widget).load_project_database(path)

        # This needs to be updated if the base layers are changed
        self.assertEqual(widget.listWidget_project_areas.item(0).text(), "1")

    def test_update_project_area_parameters(self):
        path = os.path.join(test_data_path, "filled_test_database.gpkg")
        widget = TabDockWidget(self.project, self.iface)

        value = widget.spinBox_dwellings_size_1.value()
        self.assertEqual(value, 0)

        WidgetUtilsProjectArea(widget).load_project_database(path)

        value = widget.spinBox_bicycle_parking_bedroom_dwelling_1.value()
        self.assertEqual(value, 3)

        item = widget.listWidget_project_areas.item(1)
        WidgetUtilsProjectArea(widget).update_project_area_parameters(item)

        for sub_widget in widget.findChildren((QSpinBox, QDoubleSpinBox)):
            self.assertNotEqual(sub_widget.value(), 0)

    def test_zoom_to_project_area(self) -> None:
        pass
