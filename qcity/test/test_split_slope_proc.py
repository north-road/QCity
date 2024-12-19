import unittest
import os

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsPointXY,
    QgsVectorLayer,
    QgsProcessingContext,
    QgsCoordinateTransformContext,
    QgsSettings,
    QgsProcessingFeatureSource,
)
from slope_digitizing_tools.test.utilities import get_qgis_app
from slope_digitizing_tools.core import SETTINGS_MANAGER

from ..proc.split_slope_proc import SplitSlopeAlgorithm


test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class SplitLinesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("Slope_Digitizing_Test")
        QCoreApplication.setOrganizationDomain("slope_digitizing")
        QCoreApplication.setApplicationName("slope_digitizing")

        _, __, cls.iface, cls.PARENT = get_qgis_app()
        QgsSettings().clear()
        SETTINGS_MANAGER.reload()

        # raster layer in EPSG:3857
        cls.raster_layer = QgsRasterLayer(test_data_path + "/dem.tif", "raster")
        assert cls.raster_layer.isValid()

    def test_getDist(self):
        alg = SplitSlopeAlgorithm()
        context = QgsProcessingContext()
        context.setProject(QgsProject.instance())
        context.setEllipsoid("EPSG:7019")
        context.setTransformContext(QgsCoordinateTransformContext())

        line_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "lineLayer", "memory")
        self.assertTrue(line_layer.isValid())
        line_layer_source = QgsProcessingFeatureSource(line_layer, context)

        alg.create_distance_area_calculators(line_layer_source, context)

        dist = alg._lines_distance_area.measureLine(
            QgsPointXY(10, 20), QgsPointXY(11, 20)
        )
        self.assertAlmostEqual(dist, 104646, delta=100)

    def test_getRasterValueAtPoint(self):
        point = QgsPointXY(-347889, 6632414)
        value = SplitSlopeAlgorithm.getRasterValueAtPoint(point, self.raster_layer)
        self.assertAlmostEqual(value, 81.0)

    def test_transform_to_dem_crs(self):
        point = QgsPointXY(-3.1235934, 59.5799964)
        line_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "lineLayer", "memory")

        self.assertTrue(line_layer.isValid())
        self.assertTrue(self.raster_layer.isValid())

        self.assertEqual(line_layer.crs().authid(), "EPSG:4326")
        self.assertEqual(self.raster_layer.crs().authid(), "EPSG:3857")
        context = QgsProcessingContext()
        transformed = SplitSlopeAlgorithm.transform_to_dem_crs(
            point, line_layer, self.raster_layer, context
        )
        self.assertEqual(
            transformed,
            QgsPointXY(-347716.82673323008930311, 8306816.54346549138426781),
        )
