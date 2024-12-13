import unittest

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import Qgis
from qgis.core import QgsSettings

from slope_digitizing_tools.gui.widget import SlopeDigitizingConfigDockWidget
from slope_digitizing_tools.test.utilities import get_qgis_app

from slope_digitizing_tools.core import SETTINGS_MANAGER


class WidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("Slope_Digitizing_Test")
        QCoreApplication.setOrganizationDomain("slope_digitizing")
        QCoreApplication.setApplicationName("slope_digitizing")

        get_qgis_app()
        QgsSettings().clear()
        SETTINGS_MANAGER.reload()

    def test_config_ui(self):
        self.assertEqual(SETTINGS_MANAGER.get_distance_unit(), Qgis.DistanceUnit.Meters)
        self.assertEqual(
            SETTINGS_MANAGER.get_fall_high_threshold(),
            SETTINGS_MANAGER.DEFAULT_FALL_HIGH,
        )

        ui = SlopeDigitizingConfigDockWidget()
        ui.show()

        # should be no change
        self.assertEqual(SETTINGS_MANAGER.get_distance_unit(), Qgis.DistanceUnit.Meters)
        self.assertEqual(
            SETTINGS_MANAGER.get_fall_high_threshold(),
            SETTINGS_MANAGER.DEFAULT_FALL_HIGH,
        )

        self.assertTrue(ui.isVisible())
        ui.config_widget.spinBox_fall_high.setValue(-13)
        self.assertEqual(SETTINGS_MANAGER.get_fall_high_threshold(), -13)
        self.assertEqual(SETTINGS_MANAGER.get_distance_unit(), Qgis.DistanceUnit.Meters)

        ui.config_widget.comboBox_distance_unit.setCurrentIndex(
            ui.config_widget.comboBox_distance_unit.findData(
                int(Qgis.DistanceUnit.Feet.value)
            )
        )
        self.assertEqual(SETTINGS_MANAGER.get_fall_high_threshold(), -13)
        self.assertEqual(SETTINGS_MANAGER.get_distance_unit(), Qgis.DistanceUnit.Feet)
