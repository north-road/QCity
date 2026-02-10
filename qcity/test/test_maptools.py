import os
import unittest
import tempfile

from typing import Union

from qgis.PyQt.QtCore import Qt, QEvent, QPoint, QCoreApplication
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsReferencedRectangle,
)
from qgis.gui import QgsMapMouseEvent
from qgis.core import (
    QgsProject,
    QgsRectangle,
    QgsSettings,
)

from qcity.core import DatabaseUtils, get_project_controller
from qcity.gui.qcity_dock import QCityDockWidget
from qcity.test.utilities import get_qgis_app
from qcity.gui.maptools import DrawPolygonTool
from qcity.test.qcity_test_base import QCityTestBase


class MapToolsTest(QCityTestBase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCity_Digitizing_Test")
        QCoreApplication.setOrganizationDomain("qcity_digitizing")
        QCoreApplication.setApplicationName("qcity_digitizing")

        _, __, cls.iface, CANVAS = get_qgis_app()
        QgsSettings().clear()

        cls.iface.mapCanvas().setDestinationCrs(
            QgsCoordinateReferenceSystem("EPSG:3857")
        )

    def mocked_get_new_name(self):
        return "new_name"

    def test_digitizing(self) -> None:
        self.iface.mapCanvas().setReferencedExtent(
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

        widget = QCityDockWidget(QgsProject.instance(), self.iface)
        widget.show()
        widget.ensurePolished()

        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(gpkg_path)

            map_tool = DrawPolygonTool(
                map_canvas=self.iface.mapCanvas(),
                cad_dock_widget=self.iface.cadDockWidget(),
            )
            map_tool.get_new_name = self.mocked_get_new_name

            widget.load_project_database(gpkg_path, "gpkg")
            widget.toolButton_project_area_add.clicked.emit()

            map_tool.canvasReleaseEvent(self.click_from_middle())
            map_tool.canvasReleaseEvent(self.click_from_middle(x=10, y=10))
            map_tool.canvasReleaseEvent(self.click_from_middle(x=15, y=15))

            map_tool.canvasReleaseEvent(self.click_from_middle(type="right"))

            self.assertTrue(
                widget.listWidget_project_areas.model().data(
                    widget.listWidget_project_areas.model().index(0, 0)
                ),
                "test",
            )

            self.delete_qobject(map_tool)
            self.delete_qobject(widget)

    def click_from_middle(
        self, type: str = "left", x: int = 0, y: int = 0
    ) -> Union[QgsMapMouseEvent, None]:
        if type == "left":
            click = Qt.MouseButton.LeftButton
        elif type == "right":
            click = Qt.MouseButton.RightButton
        else:
            return
        return QgsMapMouseEvent(
            self.iface.mapCanvas(),
            QEvent.Type.MouseButtonRelease,
            QPoint(
                self.iface.mapCanvas().width() // 2 + x,
                self.iface.mapCanvas().height() // 2 + y,
            ),
            click,
            click,
            Qt.KeyboardModifier.NoModifier,
        )


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MapToolsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
