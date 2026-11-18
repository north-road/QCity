import os
import unittest
import tempfile

from qgis.PyQt.QtCore import QCoreApplication, QDir
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtTest import QSignalSpy

from qgis.core import (
    Qgis,
    QgsSettings,
    QgsRasterLayer,
    QgsProject,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
)
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

    def test_default_database_crs(self):
        """
        Test default database crs
        """
        self.settings_manager.set_default_database_crs(QgsCoordinateReferenceSystem())
        self.assertEqual(
            self.settings_manager.default_database_crs().authid(),
            SettingsManager.DEFAULT_DATABASE_CRS,
        )
        self.settings_manager.set_default_database_crs(
            QgsCoordinateReferenceSystem("EPSG:3111")
        )
        self.assertEqual(
            self.settings_manager.default_database_crs().authid(), "EPSG:3111"
        )


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSettingsManager)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
