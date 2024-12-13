import os
import unittest
import tempfile

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtTest import QSignalSpy

from qgis.core import Qgis, QgsSettings, QgsRasterLayer, QgsProject, QgsVectorLayer
from slope_digitizing_tools.core import SettingsManager, SlopeType, ConstraintAction
from slope_digitizing_tools.test.utilities import get_qgis_app

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestSettingsManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("Slope_Digitizing_Test")
        QCoreApplication.setOrganizationDomain("slope_digitizing")
        QCoreApplication.setApplicationName("slope_digitizing")

        get_qgis_app()

        QgsSettings().clear()
        cls.settings_manager = SettingsManager()
        cls.settings_manager.reload()

    def test_low_color(self):
        spy = QSignalSpy(self.settings_manager.colors_changed)
        new_color = QColor(255, 0, 0)
        self.settings_manager.set_low_color(new_color)
        self.assertEqual(self.settings_manager.get_low_color(), new_color)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_color)

        # Set the same color again, signal should not be emitted
        self.settings_manager.set_low_color(new_color)
        self.assertEqual(len(spy), 1)

    def test_mid_color(self):
        spy = QSignalSpy(self.settings_manager.colors_changed)
        new_color = QColor(0, 255, 0)
        self.settings_manager.set_mid_color(new_color)
        self.assertEqual(self.settings_manager.get_mid_color(), new_color)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_color)

        # Set the same color again, signal should not be emitted
        self.settings_manager.set_mid_color(new_color)
        self.assertEqual(len(spy), 1)

    def test_high_color(self):
        spy = QSignalSpy(self.settings_manager.colors_changed)
        new_color = QColor(0, 0, 255)
        self.settings_manager.set_high_color(new_color)
        self.assertEqual(self.settings_manager.get_high_color(), new_color)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_color)

        # Set the same color again, signal should not be emitted
        self.settings_manager.set_high_color(new_color)
        self.assertEqual(len(spy), 1)

    def test_extreme_color(self):
        spy = QSignalSpy(self.settings_manager.colors_changed)
        new_color = QColor(255, 255, 0)
        self.settings_manager.set_extreme_color(new_color)
        self.assertEqual(self.settings_manager.get_extreme_color(), new_color)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_color)

        # Set the same color again, signal should not be emitted
        self.settings_manager.set_extreme_color(new_color)
        self.assertEqual(len(spy), 1)

    def test_distance_unit(self):
        spy = QSignalSpy(self.settings_manager.distance_unit_changed)
        new_unit = Qgis.DistanceUnit.Feet
        self.settings_manager.set_distance_unit(new_unit)
        self.assertEqual(self.settings_manager.get_distance_unit(), new_unit)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_unit)

        # Set the same unit again, signal should not be emitted
        self.settings_manager.set_distance_unit(new_unit)
        self.assertEqual(len(spy), 1)

    def test_slope_type(self):
        spy = QSignalSpy(self.settings_manager.slope_type_changed)
        new_slope_type = SlopeType.Percent
        self.settings_manager.set_slope_type(new_slope_type)
        self.assertEqual(self.settings_manager.get_slope_type(), new_slope_type)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_slope_type)

        # Set the same slope type again, signal should not be emitted
        self.settings_manager.set_slope_type(new_slope_type)
        self.assertEqual(len(spy), 1)

    def test_rise_low_threshold(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_threshold = 4.0
        self.settings_manager.set_rise_low_threshold(new_threshold)
        self.assertEqual(self.settings_manager.get_rise_low_threshold(), new_threshold)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_threshold)

        # Set the same threshold again, signal should not be emitted
        self.settings_manager.set_rise_low_threshold(new_threshold)
        self.assertEqual(len(spy), 1)

    def test_fall_low_threshold(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_threshold = -6.0
        self.settings_manager.set_fall_low_threshold(new_threshold)
        self.assertEqual(self.settings_manager.get_fall_low_threshold(), new_threshold)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_threshold)

        # Set the same threshold again, signal should not be emitted
        self.settings_manager.set_fall_low_threshold(new_threshold)
        self.assertEqual(len(spy), 1)

    def test_rise_mid_threshold(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_threshold = 6.0
        self.settings_manager.set_rise_mid_threshold(new_threshold)
        self.assertEqual(self.settings_manager.get_rise_mid_threshold(), new_threshold)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_threshold)

        # Set the same threshold again, signal should not be emitted
        self.settings_manager.set_rise_mid_threshold(new_threshold)
        self.assertEqual(len(spy), 1)

    def test_fall_mid_threshold(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_threshold = -9.0
        self.settings_manager.set_fall_mid_threshold(new_threshold)
        self.assertEqual(self.settings_manager.get_fall_mid_threshold(), new_threshold)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_threshold)

        # Set the same threshold again, signal should not be emitted
        self.settings_manager.set_fall_mid_threshold(new_threshold)
        self.assertEqual(len(spy), 1)

    def test_rise_high_threshold(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_threshold = 9.0
        self.settings_manager.set_rise_high_threshold(new_threshold)
        self.assertEqual(self.settings_manager.get_rise_high_threshold(), new_threshold)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_threshold)

        # Set the same threshold again, signal should not be emitted
        self.settings_manager.set_rise_high_threshold(new_threshold)
        self.assertEqual(len(spy), 1)

    def test_fall_high_threshold(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_threshold = -13.0
        self.settings_manager.set_fall_high_threshold(new_threshold)
        self.assertEqual(self.settings_manager.get_fall_high_threshold(), new_threshold)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_threshold)

        # Set the same threshold again, signal should not be emitted
        self.settings_manager.set_fall_high_threshold(new_threshold)
        self.assertEqual(len(spy), 1)

    def test_rise_limit(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_limit = 13.0
        self.settings_manager.set_rise_limit(new_limit)
        self.assertEqual(self.settings_manager.get_rise_limit(), new_limit)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_limit)

        # Set the same limit again, signal should not be emitted
        self.settings_manager.set_rise_limit(new_limit)
        self.assertEqual(len(spy), 1)

    def test_fall_limit(self):
        spy = QSignalSpy(self.settings_manager.thresholds_changed)
        new_limit = -16.0
        self.settings_manager.set_fall_limit(new_limit)
        self.assertEqual(self.settings_manager.get_fall_limit(), new_limit)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_limit)

        # Set the same limit again, signal should not be emitted
        self.settings_manager.set_fall_limit(new_limit)
        self.assertEqual(len(spy), 1)

    def test_slope_limit_action(self):
        spy = QSignalSpy(self.settings_manager.slope_limit_action_changed)
        new_action = ConstraintAction.PreventSegment
        self.settings_manager.set_slope_limit_action(new_action)
        self.assertEqual(self.settings_manager.get_slope_limit_action(), new_action)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], new_action)

        # Set the same action again, signal should not be emitted
        self.settings_manager.set_slope_limit_action(new_action)
        self.assertEqual(len(spy), 1)

    def test_dem_layer(self):
        QgsProject.instance().clear()

        self.assertIsNone(self.settings_manager.get_dem_layer())
        raster_layer = QgsRasterLayer(test_data_path + "/dem.tif", "raster")
        self.assertTrue(raster_layer.isValid())

        QgsProject.instance().addMapLayer(raster_layer)
        spy = QSignalSpy(self.settings_manager.dem_layer_changed)
        self.settings_manager.set_dem_layer(raster_layer)
        self.assertEqual(self.settings_manager.get_dem_layer(), raster_layer)

        self.assertEqual(len(spy), 1)

        # delete layer, check again
        QgsProject.instance().removeMapLayer(raster_layer)
        self.assertIsNone(self.settings_manager.get_dem_layer())
        self.assertEqual(len(spy), 2)

        # test persistence of dem layer in project
        raster_layer = QgsRasterLayer(test_data_path + "/dem.tif", "raster1")
        QgsProject.instance().addMapLayer(raster_layer)
        raster_layer2 = QgsRasterLayer(test_data_path + "/dem.tif", "raster2")
        QgsProject.instance().addMapLayer(raster_layer2)
        self.settings_manager.set_dem_layer(raster_layer2)
        self.assertEqual(len(spy), 3)

        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertTrue(QgsProject.instance().write(temp_dir + "/test.qgs"))

            QgsProject.instance().clear()
            self.assertIsNone(self.settings_manager.get_dem_layer())
            self.assertEqual(len(spy), 4)

            self.assertTrue(QgsProject.instance().read(temp_dir + "/test.qgs"))

            self.assertEqual(self.settings_manager.get_dem_layer().name(), "raster2")
            self.assertEqual(len(spy), 5)

    def test_polygon_constraint_layer(self):
        QgsProject.instance().clear()

        self.assertIsNone(self.settings_manager.get_polygon_constraint_layer())
        vector_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "poly_layer", "memory")
        self.assertTrue(vector_layer.isValid())

        QgsProject.instance().addMapLayer(vector_layer)
        spy = QSignalSpy(self.settings_manager.polygon_constraint_layer_changed)
        self.settings_manager.set_polygon_constraint_layer(vector_layer)
        self.assertEqual(
            self.settings_manager.get_polygon_constraint_layer(), vector_layer
        )

        self.assertEqual(len(spy), 1)

        # delete layer, check again
        QgsProject.instance().removeMapLayer(vector_layer)
        self.assertIsNone(self.settings_manager.get_polygon_constraint_layer())
        self.assertEqual(len(spy), 2)

        # test persistence of constraint layer in project
        vector_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "poly_layer1", "memory")
        QgsProject.instance().addMapLayer(vector_layer)
        vector_layer2 = QgsVectorLayer("Polygon?crs=EPSG:4326", "poly_layer2", "memory")
        QgsProject.instance().addMapLayer(vector_layer2)
        self.settings_manager.set_polygon_constraint_layer(vector_layer2)
        self.assertEqual(len(spy), 3)

        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertTrue(QgsProject.instance().write(temp_dir + "/test.qgs"))

            QgsProject.instance().clear()
            self.assertIsNone(self.settings_manager.get_polygon_constraint_layer())
            self.assertEqual(len(spy), 4)

            self.assertTrue(QgsProject.instance().read(temp_dir + "/test.qgs"))

            self.assertEqual(
                self.settings_manager.get_polygon_constraint_layer().name(),
                "poly_layer2",
            )
            self.assertEqual(len(spy), 5)


if __name__ == "__main__":
    unittest.main()
