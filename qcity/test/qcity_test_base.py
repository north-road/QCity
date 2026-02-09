import unittest

from qgis.core import QgsProject

from qcity.core.project import get_project_controller, reset_project_controller


class QCityTestBase(unittest.TestCase):
    """
    QCity Test base class
    """

    def setUp(self):
        _ = get_project_controller()

    def tearDown(self):
        QgsProject.instance().clear()
        reset_project_controller()
