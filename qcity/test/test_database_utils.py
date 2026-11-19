import unittest
import os
import tempfile

from qgis.PyQt.QtCore import QVariant, QDate

from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem

from qcity.core import DatabaseUtils, LayerType, SETTINGS_MANAGER

from qcity.test.qcity_test_base import QCityTestBase

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestDatabaseUtils(QCityTestBase):
    def test_qvariant_type_from_string(self):
        """
        Test qvariant_type_from_string
        """
        self.assertEqual(DatabaseUtils.qvariant_type_from_string("int"), QVariant.Int)
        self.assertEqual(
            DatabaseUtils.qvariant_type_from_string("double"), QVariant.Double
        )
        self.assertEqual(
            DatabaseUtils.qvariant_type_from_string("string"), QVariant.String
        )
        self.assertEqual(DatabaseUtils.qvariant_type_from_string("date"), QVariant.Date)
        self.assertEqual(DatabaseUtils.qvariant_type_from_string("bool"), QVariant.Bool)
        self.assertEqual(
            DatabaseUtils.qvariant_type_from_string("value_map"), QVariant.String
        )
        with self.assertRaises(KeyError):
            DatabaseUtils.qvariant_type_from_string("invalid_key")

    def test_create_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(gpkg_path)

            self.assertTrue(os.path.exists(gpkg_path))

            vl = QgsVectorLayer(gpkg_path + "|layername=project_areas")
            self.assertTrue(vl.isValid())
            self.assertEqual(vl.featureCount(), 0)
            fields = vl.fields()
            car_parking_2_bedroom_idx = fields.lookupField("car_parking_2_bedroom")
            field = fields[car_parking_2_bedroom_idx]
            self.assertEqual(field.type(), QVariant.Int)
            dwelling_size_3_bedroom_idx = fields.lookupField("dwelling_size_3_bedroom")
            field = fields[dwelling_size_3_bedroom_idx]
            self.assertEqual(field.type(), QVariant.Double)

            vl = QgsVectorLayer(gpkg_path + "|layername=development_sites")
            self.assertTrue(vl.isValid())
            self.assertEqual(vl.featureCount(), 0)
            fields = vl.fields()
            date_idx = fields.lookupField("year")
            field = fields[date_idx]
            self.assertEqual(field.type(), QVariant.Int)
            site_owner_idx = fields.lookupField("site_owner")
            field = fields[site_owner_idx]
            self.assertEqual(field.type(), QVariant.String)

            vl = QgsVectorLayer(gpkg_path + "|layername=building_levels")
            self.assertTrue(vl.isValid())
            self.assertEqual(vl.featureCount(), 0)
            fields = vl.fields()
            office_floorspace_idx = fields.lookupField("office_floorspace")
            field = fields[office_floorspace_idx]
            self.assertEqual(field.type(), QVariant.Double)

    def test_field_default(self):
        self.assertIsNone(
            DatabaseUtils.get_field_default(LayerType.ProjectAreas, "xxxx")
        )

        self.assertEqual(
            DatabaseUtils.get_field_default(LayerType.ProjectAreas, "date"),
            QDate.currentDate().year(),
        )

        self.assertEqual(
            DatabaseUtils.get_field_default(
                LayerType.ProjectAreas, "dwelling_size_3_bedroom"
            ),
            100,
        )
        self.assertEqual(
            DatabaseUtils.get_field_default(LayerType.DevelopmentSites, "site_status"),
            "P",
        )
        self.assertEqual(
            DatabaseUtils.get_field_default(LayerType.BuildingLevels, "level_height"), 3
        )

    def test_upgrade_table(self):
        """
        Test upgrading table definitions to latest
        """
        uri = f"Polygon?crs=epsg:4326&"
        layer = QgsVectorLayer(uri, "x", "memory")
        DatabaseUtils.upgrade_table(layer, LayerType.DevelopmentSites)

        field_idx = layer.fields().lookupField("base_height")
        self.assertNotEqual(field_idx, -1)

    def test_create_database_uses_configured_crs(self) -> None:
        original_crs = SETTINGS_MANAGER.default_database_crs()
        try:
            SETTINGS_MANAGER.set_default_database_crs(
                QgsCoordinateReferenceSystem("EPSG:3111")
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

                DatabaseUtils.create_base_tables(gpkg_path)

                vl = QgsVectorLayer(gpkg_path + "|layername=project_areas")
                self.assertTrue(vl.isValid())
                self.assertEqual(vl.crs().authid(), "EPSG:3111")

            SETTINGS_MANAGER.set_default_database_crs(
                QgsCoordinateReferenceSystem("EPSG:28356")
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

                DatabaseUtils.create_base_tables(gpkg_path)

                vl = QgsVectorLayer(gpkg_path + "|layername=project_areas")
                self.assertTrue(vl.isValid())
                self.assertEqual(vl.crs().authid(), "EPSG:28356")
        finally:
            SETTINGS_MANAGER.set_default_database_crs(original_crs)

    def test_copy_reprojected_geopackage(self) -> None:
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY

        original_crs = SETTINGS_MANAGER.default_database_crs()
        try:
            SETTINGS_MANAGER.set_default_database_crs(
                QgsCoordinateReferenceSystem("EPSG:28356")
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                source_gpkg = os.path.join(temp_dir, "source.gpkg")
                target_gpkg = os.path.join(temp_dir, "reprojected.gpkg")

                DatabaseUtils.create_base_tables(source_gpkg)

                sample_ring = [
                    QgsPointXY(334000.0, 6250000.0),
                    QgsPointXY(334100.0, 6250000.0),
                    QgsPointXY(334100.0, 6250100.0),
                    QgsPointXY(334000.0, 6250100.0),
                    QgsPointXY(334000.0, 6250000.0),
                ]
                sample_geom = QgsGeometry.fromPolygonXY([sample_ring])

                expected_layers = [
                    "project_areas",
                    "development_sites",
                    "building_levels",
                ]
                for layer_name in expected_layers:
                    edit_vl = QgsVectorLayer(
                        f"{source_gpkg}|layername={layer_name}", layer_name, "ogr"
                    )
                    self.assertTrue(edit_vl.isValid())
                    self.assertTrue(edit_vl.startEditing())

                    feat = QgsFeature(edit_vl.fields())
                    feat.setGeometry(sample_geom)
                    self.assertTrue(edit_vl.addFeature(feat))
                    self.assertTrue(edit_vl.commitChanges())

                DatabaseUtils.copy_reprojected_geopackage(
                    source_gpkg, target_gpkg, QgsCoordinateReferenceSystem("EPSG:4326")
                )

                self.assertTrue(os.path.exists(target_gpkg))

                for layer_name in expected_layers:
                    src_vl = QgsVectorLayer(
                        f"{source_gpkg}|layername={layer_name}", layer_name, "ogr"
                    )
                    dst_vl = QgsVectorLayer(
                        f"{target_gpkg}|layername={layer_name}", layer_name, "ogr"
                    )
                    self.assertTrue(src_vl.isValid())
                    self.assertTrue(dst_vl.isValid())
                    self.assertEqual(src_vl.crs().authid(), "EPSG:28356")
                    self.assertEqual(dst_vl.crs().authid(), "EPSG:4326")
                    self.assertEqual(src_vl.featureCount(), 1)
                    self.assertEqual(dst_vl.featureCount(), 1)
                    self.assertEqual(dst_vl.fields().names(), src_vl.fields().names())

                    src_feat = next(src_vl.getFeatures())
                    dst_feat = next(dst_vl.getFeatures())
                    self.assertTrue(src_feat.hasGeometry())
                    self.assertTrue(dst_feat.hasGeometry())

                    self.assertEqual(
                        dst_feat.geometry().asWkt(2),
                        "MultiPolygon (((151.21 -33.88, 151.21 -33.88, 151.21 -33.88, 151.21 -33.88, 151.21 -33.88)))",
                    )
        finally:
            SETTINGS_MANAGER.set_default_database_crs(original_crs)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseUtils)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
