import unittest
import os
import tempfile

from qgis.PyQt.QtCore import QVariant

from qgis.core import (
    QgsVectorLayer,
    QgsSettings,
    QgsCoordinateReferenceSystem,
)

from qcity.core.database import DatabaseUtils
from qcity.core.settings import SETTINGS_MANAGER

from qcity.test.utilities import get_qgis_app

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestDatabaseUtils(unittest.TestCase):

    def test_create_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            self.assertTrue(
                os.path.exists(gpkg_path)
            )

            vl = QgsVectorLayer(gpkg_path + "|layername=project_areas")
            self.assertTrue(vl.isValid())
            self.assertEqual(vl.featureCount(), 0)
            fields = vl.fields()
            car_parking_2_bedroom_idx = fields.lookupField('car_parking_2_bedroom')
            field = fields[car_parking_2_bedroom_idx]
            self.assertEqual(field.type(), QVariant.Int)
            dwelling_size_3_bedroom_idx = fields.lookupField('dwelling_size_3_bedroom')
            field = fields[dwelling_size_3_bedroom_idx]
            self.assertEqual(field.type(), QVariant.Double)

            vl = QgsVectorLayer(gpkg_path + "|layername=development_sites")
            self.assertTrue(vl.isValid())
            self.assertEqual(vl.featureCount(), 0)
            fields = vl.fields()
            date_idx = fields.lookupField('date')
            field = fields[date_idx]
            self.assertEqual(field.type(), QVariant.Date)
            site_owner_idx = fields.lookupField('site_owner')
            field = fields[site_owner_idx]
            self.assertEqual(field.type(), QVariant.String)

            vl = QgsVectorLayer(gpkg_path + "|layername=building_levels")
            self.assertTrue(vl.isValid())
            self.assertEqual(vl.featureCount(), 0)
            fields = vl.fields()
            office_floorspace_idx = fields.lookupField('office_floorspace')
            field = fields[office_floorspace_idx]
            self.assertEqual(field.type(), QVariant.Double)
