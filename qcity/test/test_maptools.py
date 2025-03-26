import os
import unittest
from typing import Union
from unittest.mock import patch

import numpy as np
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

from qcity.gui.widget import TabDockWidget
from qcity.test.utilities import get_qgis_app
from qcity.utils.maptools import DrawPolygonTool

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


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
                QgsCoordinateReferenceSystem(3857),
            )
        )

        self.widget = TabDockWidget(self.project, self.iface)
        message_bar = self.iface.messageBar()

        self.map_tool = DrawPolygonTool(
            map_canvas=self.iface.mapCanvas(),
            cad_dock_widget=QgsAdvancedDigitizingDockWidget(self.CANVAS),
            message_bar=message_bar,
            dlg=self.widget,
            iface=self.iface,
        )

        self.widget.load_project_database("test_data/empty_test_database.gpkg", "gpkg")
        self.widget.toolButton_project_area_add.clicked.emit()

        points = [
            QgsPointXY(-346976.04375941428588703, 6632700.0318903774023056),
            QgsPointXY(-346915.16854393307585269, 6632639.15667489636689425),
            QgsPointXY(-346884.73093619249993935, 6632608.71906715538352728),
        ]

        self.map_tool.canvasReleaseEvent(self.click_from_middle())
        self.map_tool.canvasReleaseEvent(self.click_from_middle(x=10, y=10))
        self.map_tool.canvasReleaseEvent(self.click_from_middle(x=15, y=15))

        np.testing.assert_almost_equal(self.map_tool.points, points, decimal=4)

        self.map_tool.canvasReleaseEvent(self.click_from_middle(type="right"))

        self.assertTrue(self.widget.listWidget_project_areas.item(0), "test")

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
