import os
import unittest
import tempfile

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtTest import QSignalSpy

from qgis.core import Qgis, QgsSettings, QgsRasterLayer, QgsProject, QgsVectorLayer
from qcity.core import SettingsManager
from qcity.test.utilities import get_qgis_app

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestSettingsManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCity_Digitizing_Test")
        QCoreApplication.setOrganizationDomain("qcity_digitizing")
        QCoreApplication.setApplicationName("qcity_digitizing")

        get_qgis_app()

        QgsSettings().clear()
        cls.settings_manager = SettingsManager()

    def test_pass(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
