import unittest
import os

from qgis.PyQt.QtWidgets import QSpinBox, QDoubleSpinBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis._core import QgsCoordinateReferenceSystem

from qgis.core import (
    QgsProject,
    QgsSettings,
)

from qcity.gui.qcity_dock import QCityDockWidget
from qcity.test.utilities import get_qgis_app
from qcity.gui.widget_tab_project_areas import ProjectAreasPageController

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

    def test_update_project_area_parameters(self):
        path = os.path.join(test_data_path, "filled_test_database.gpkg")
        widget = QCityDockWidget(self.project, self.iface)

        value = widget.spinBox_dwellings_size_1.value()
        self.assertEqual(value, 0)

        widget.load_project_database(path)

        value = widget.spinBox_bicycle_parking_bedroom_dwelling_1.value()
        self.assertEqual(value, 3)

        item = widget.listWidget_project_areas.item(1)
        ProjectAreasPageController(widget).update_project_area_parameters(item)

        for sub_widget in widget.findChildren((QSpinBox, QDoubleSpinBox)):
            self.assertNotEqual(sub_widget.value(), 0)

    def test_zoom_to_project_area(self) -> None:
        pass
