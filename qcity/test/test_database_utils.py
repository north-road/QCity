import unittest
import os
import tempfile

from qgis.PyQt.QtCore import QVariant, QDate

from qgis.core import (
    QgsVectorLayer
)

from qcity.core import DatabaseUtils, LayerType

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
            date_idx = fields.lookupField('year')
            field = fields[date_idx]
            self.assertEqual(field.type(), QVariant.Int)
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

    def test_field_default(self):
        self.assertIsNone(
            DatabaseUtils.get_field_default(LayerType.ProjectAreas, "xxxx")
        )

        self.assertEqual(
            DatabaseUtils.get_field_default(LayerType.ProjectAreas, "date"),
             QDate.currentDate().year()
        )

        self.assertEqual(
            DatabaseUtils.get_field_default(LayerType.ProjectAreas, "dwelling_size_3_bedroom"),
             50
        )
        self.assertEqual(
            DatabaseUtils.get_field_default(LayerType.DevelopmentSites, "site_status"),
             'P'
        )
        self.assertEqual(
            DatabaseUtils.get_field_default(LayerType.BuildingLevels, "level_height"),
             6
        )
