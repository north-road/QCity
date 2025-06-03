import os
import unittest
import tempfile

from typing import Union
from unittest.mock import patch

from qgis.PyQt.QtCore import Qt, QEvent, QPoint, QCoreApplication
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsPointXY,
    QgsReferencedRectangle,
)
from qgis.gui import QgsMapMouseEvent, QgsMapCanvas, QgsAdvancedDigitizingDockWidget
from qgis.core import (
    QgsProject,
    QgsRectangle,
    QgsSettings,
)

from qcity.core import DatabaseUtils, PROJECT_CONTROLLER
from qcity.gui.qcity_dock import QCityDockWidget
from qcity.test.utilities import get_qgis_app
from qcity.gui.maptools import DrawPolygonTool


class MapToolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCity_Digitizing_Test")
        QCoreApplication.setOrganizationDomain("qcity_digitizing")
        QCoreApplication.setApplicationName("qcity_digitizing")

        _, __, cls.iface, cls.PARENT = get_qgis_app()
        QgsSettings().clear()

        cls.project = QgsProject.instance()

        cls.CANVAS = QgsMapCanvas()
        cls.CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3857"))
        cls.CANVAS.setFrameStyle(0)
        cls.CANVAS.resize(600, 400)
        assert cls.CANVAS.width() == 600
        assert cls.CANVAS.height() == 400

    @patch("qgis.PyQt.QtWidgets.QInputDialog.getText")
    def test_digitizing(self, mock_get_text) -> None:
        mock_get_text.return_value = ("test", "gpkg")

        self.CANVAS.setReferencedExtent(
            QgsReferencedRectangle(
                QgsRectangle(
                    -348802.30022384965559468,
                    6631007.70089999958872795,
                    -344918.46147615037625656,
                    6633917.53619999997317791,
                ),
                QgsCoordinateReferenceSystem("EPSG:3857"),
            )
        )

        self.widget = QCityDockWidget(self.project, self.iface)

        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(gpkg_path)

            self.map_tool = DrawPolygonTool(
                map_canvas=self.iface.mapCanvas(),
                cad_dock_widget=QgsAdvancedDigitizingDockWidget(self.CANVAS),
            )

            self.widget.load_project_database(gpkg_path, "gpkg")
            self.widget.toolButton_project_area_add.clicked.emit()

            points = [
                QgsPointXY(-346976.04375941428588703, 6632700.0318903774023056),
                QgsPointXY(-346915.16854393307585269, 6632639.15667489636689425),
                QgsPointXY(-346884.73093619249993935, 6632608.71906715538352728),
            ]

            self.map_tool.canvasReleaseEvent(self.click_from_middle())
            self.map_tool.canvasReleaseEvent(self.click_from_middle(x=10, y=10))
            self.map_tool.canvasReleaseEvent(self.click_from_middle(x=15, y=15))

            self.assertAlmostEqual(self.map_tool.points[0].x(), points[0].x(), delta=10)
            self.assertAlmostEqual(self.map_tool.points[0].y(), points[0].y(), delta=10)
            self.assertAlmostEqual(self.map_tool.points[1].x(), points[1].x(), delta=10)
            self.assertAlmostEqual(self.map_tool.points[1].y(), points[1].y(), delta=10)
            self.assertAlmostEqual(self.map_tool.points[2].x(), points[2].x(), delta=10)
            self.assertAlmostEqual(self.map_tool.points[2].y(), points[2].y(), delta=10)

            self.map_tool.canvasReleaseEvent(self.click_from_middle(type="right"))

            self.assertTrue(self.widget.listWidget_project_areas.item(0), "test")

            PROJECT_CONTROLLER.cleanup()
            QgsProject.instance().clear()

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


if __name__ == "__main__":
    suite = unittest.makeSuite(MapToolsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
