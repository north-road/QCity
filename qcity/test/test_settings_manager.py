import os
import unittest
import tempfile

from qgis.PyQt.QtCore import QCoreApplication, QDir
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtTest import QSignalSpy

from qgis.core import Qgis, QgsSettings, QgsRasterLayer, QgsProject, QgsVectorLayer
from qcity.core import SettingsManager
from qcity.test.utilities import get_qgis_app

from qcity.test.qcity_test_base import QCityTestBase

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestSettingsManager(QCityTestBase):
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

    def test_last_used_db_folder(self):
        """
        Test last used database folder
        """
        self.assertEqual(
            self.settings_manager.last_used_database_folder(), QDir.homePath()
        )
        self.settings_manager.set_last_used_database_folder("/home/test/dbs")
        self.assertEqual(
            self.settings_manager.last_used_database_folder(), "/home/test/dbs"
        )


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSettingsManager)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
