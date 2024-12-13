import math
import os
import unittest
from typing import Union

import numpy as np
from qgis.PyQt.QtCore import Qt, QEvent, QPoint, QCoreApplication
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsPointXY,
    QgsReferencedRectangle,
    Qgis,
)
from qgis.gui import QgsMapMouseEvent, QgsMapCanvas, QgsAdvancedDigitizingDockWidget
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProject,
    QgsRectangle,
    QgsSettings,
)

from slope_digitizing_tools.gui.widget import (
    SlopeDigitizingConfigDockWidget,
    SlopeDigitizingLiveResultsDockWidget,
)
from slope_digitizing_tools.test.utilities import get_qgis_app
from slope_digitizing_tools.utils.maptools import DrawLineTool
from slope_digitizing_tools.core import SETTINGS_MANAGER, SlopeType

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class MapToolsTest(unittest.TestCase):
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

        cls.project = QgsProject.instance()

        cls.CANVAS = QgsMapCanvas()
        cls.CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3857"))
        cls.CANVAS.setFrameStyle(0)
        cls.CANVAS.resize(600, 400)
        assert cls.CANVAS.width() == 600
        assert cls.CANVAS.height() == 400

    def test_digitizing(self) -> None:
        raster_layer = QgsRasterLayer(test_data_path + "/dem.tif", "raster")
        self.assertTrue(raster_layer.isValid())
        self.project.addMapLayer(raster_layer)

        self.CANVAS.setReferencedExtent(
            QgsReferencedRectangle(
                QgsRectangle(
                    -348802.30022384965559468,
                    6631007.70089999958872795,
                    -344918.46147615037625656,
                    6633917.53619999997317791,
                ),
                raster_layer.crs(),
            )
        )

        dlg_config = SlopeDigitizingConfigDockWidget()
        message_bar = self.iface.messageBar()
        dlg_live_display = SlopeDigitizingLiveResultsDockWidget()

        vector_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "lineLayer", "memory")
        self.assertTrue(vector_layer.isValid())

        vector_layer.startEditing()
        self.project.addMapLayer(vector_layer)
        cad_dock_widget = QgsAdvancedDigitizingDockWidget(self.CANVAS, self.PARENT)

        self.map_tool = DrawLineTool(
            map_canvas=self.CANVAS,
            cad_dock_widget=cad_dock_widget,
            message_bar=message_bar,
            dlg_live_display=dlg_live_display,
            dlg_config=dlg_config.config_widget,
            iface=self.iface,
        )

        points = [
            QgsPointXY(-3.11693883358920898, 51.06443827159174731),
            QgsPointXY(-3.11420457677549445, 51.06271990702814634),
            QgsPointXY(-3.11420457677549445, 51.06100147867827133),
        ]
        # no raster, no error
        self.map_tool.canvasReleaseEvent(self.click_from_middle())
        SETTINGS_MANAGER.set_dem_layer(raster_layer)

        self.map_tool.canvasReleaseEvent(self.click_from_middle())
        np.testing.assert_almost_equal(self.map_tool.points, [points[0]], decimal=4)
        self.assertAlmostEqual(self.map_tool.last_click_raster_value, 93.0, delta=1)

        # test slope
        rise = 2
        SETTINGS_MANAGER.set_slope_type(SlopeType.Percent)
        slope_percent = self.map_tool.get_slope_in_percent(
            QgsPointXY(-346671.66768200841033831, 6632395.65581297129392624), rise
        )
        self.assertAlmostEqual(slope_percent, -21.14052922875632, delta=1)
        slope_user_units = self.map_tool.convert_slope_in_percent_to_target_units(
            slope_percent
        )
        self.assertAlmostEqual(slope_user_units, -21.14052922875632, delta=1)
        SETTINGS_MANAGER.set_slope_type(SlopeType.Degrees)
        slope_percent = self.map_tool.get_slope_in_percent(
            QgsPointXY(-346671.66768200841033831, 6632395.65581297129392624), rise
        )
        self.assertAlmostEqual(slope_percent, -21.14052922875632, delta=1)
        slope_user_units = self.map_tool.convert_slope_in_percent_to_target_units(
            slope_percent
        )
        self.assertAlmostEqual(slope_user_units, -11.93687376414342, delta=1)
        self.assertEqual(math.degrees(math.atan(slope_percent / 100)), slope_user_units)

        self.map_tool.canvasReleaseEvent(self.click_from_middle(x=50, y=50))
        self.assertEqual(self.map_tool.last_click_raster_value, 68.0)
        self.assertAlmostEqual(self.map_tool.last_map_point.x(), -346671, delta=10)
        self.assertAlmostEqual(self.map_tool.last_map_point.y(), 6632395, delta=10)

        np.testing.assert_almost_equal(self.map_tool.points, points[:2], decimal=4)

        dlg_config.config_widget.comboBox_distance_unit.setCurrentIndex(0)
        self.assertEqual(SETTINGS_MANAGER.get_distance_unit(), Qgis.DistanceUnit.Meters)

        self.map_tool.canvasReleaseEvent(self.click_from_middle(x=50, y=100))
        self.assertEqual(len(self.map_tool.rubber_bands), 2)
        self.assertEqual(
            self.map_tool.widget.lineEdit_overallDistance.text(), "4.93 mm"
        )

        self.map_tool.canvasReleaseEvent(self.click_from_middle("right", 100, 50))
        vector_layer.commitChanges()
        np.testing.assert_almost_equal(
            vector_layer.getFeatures().__next__().geometry().asPolyline(),
            points,
            decimal=4,
        )

    def click_from_middle(
        self, type: str = "left", x: int = 0, y: int = 0
    ) -> Union[QgsMapMouseEvent, None]:
        if type == "left":
            click = Qt.LeftButton
        elif type == "right":
            click = Qt.RightButton
        else:
            return
        return QgsMapMouseEvent(
            self.CANVAS,
            QEvent.MouseButtonRelease,
            QPoint(self.CANVAS.width() // 2 + x, self.CANVAS.height() // 2 + y),
            click,
            click,
            Qt.NoModifier,
        )
