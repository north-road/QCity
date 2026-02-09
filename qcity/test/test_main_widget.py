import unittest
import os
import tempfile

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsProject,
    QgsSettings,
    QgsCoordinateReferenceSystem,
)

from qcity.gui.qcity_dock import QCityDockWidget
from qcity.test.utilities import get_qgis_app
from qcity.test.qcity_test_base import QCityTestBase

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class QCityProjectMainWidgetTest(QCityTestBase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCiy_project_areas")
        QCoreApplication.setOrganizationDomain("qcity_project_areas")
        QCoreApplication.setApplicationName("qcity_project_areas")

        _, CANVAS, cls.iface, cls.PARENT = get_qgis_app()
        QgsSettings().clear()

    def test_create_database(self) -> None:
        widget = QCityDockWidget(QgsProject.instance(), self.iface)

        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "test_database.gpkg")
            widget.create_new_project_database(path)
            self.assertTrue(
                os.path.exists(os.path.join(temp_dir, "test_database.gpkg"))
            )
            self.assertEqual(widget.label_current_project_area.text(), "Project")
        self.delete_qobject(widget)

    def test_add_base_layers(self) -> None:
        widget = QCityDockWidget(QgsProject.instance(), self.iface)
        widget.add_base_layers()

        # This needs to be updated if the base layers are changed
        layer_name = "test_point_4326"
        layers = QgsProject.instance().mapLayersByName(layer_name)
        self.assertTrue(layers is not None)
        self.delete_qobject(widget)

    def test_load_project(self) -> None:
        path = os.path.join(test_data_path, "filled_test_database.gpkg")
        widget = QCityDockWidget(QgsProject.instance(), self.iface)
        widget.load_project_database(path)

        # This needs to be updated if the base layers are changed
        self.assertEqual(widget.listWidget_project_areas.item(0).text(), "1")
        self.delete_qobject(widget)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(QCityProjectMainWidgetTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
