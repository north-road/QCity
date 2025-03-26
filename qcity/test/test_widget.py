import unittest

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProject
from qgis.core import QgsSettings

from qcity.gui.widget import TabDockWidget
from qcity.test.utilities import get_qgis_app, IFACE

from qcity.core import SETTINGS_MANAGER


class WidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCity_Digitizing_Test")
        QCoreApplication.setOrganizationDomain("qcity_digitizing")
        QCoreApplication.setApplicationName("qcity_digitizing")

        get_qgis_app()
        QgsSettings().clear()

    def test_config_ui(self):
        ui = TabDockWidget(QgsProject(), IFACE)
        ui.show()
