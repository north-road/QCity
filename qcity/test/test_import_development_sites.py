import os
import tempfile
import unittest

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProject,
    QgsRectangle,
    QgsSettings,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
)

from qcity.core import (
    DatabaseUtils,
    get_project_controller,
    reset_project_controller,
)
from qcity.core.processing.import_development_sites import (
    ImportDevelopmentSitesAlgorithm,
)
from qcity.test.qcity_test_base import QCityTestBase
from qcity.test.utilities import get_qgis_app


class TestImportDevelopmentSitesAlgorithm(QCityTestBase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCity_import_development_sites")
        QCoreApplication.setOrganizationDomain("qcity_import_development_sites")
        QCoreApplication.setApplicationName("qcity_import_development_sites")

        get_qgis_app()
        QgsSettings().clear()

    def setUp(self):
        super().setUp()
        self.project = QgsProject.instance()
        self.project.clear()

        self._temp_dir = tempfile.TemporaryDirectory()
        self.gpkg_path = os.path.join(self._temp_dir.name, "test_database.gpkg")
        DatabaseUtils.create_base_tables(self.gpkg_path)

        self.controller = get_project_controller()
        self.controller.add_database_layers_to_project(self.project, self.gpkg_path)

        self.project_area_layer = self.controller.get_project_area_layer()
        self.development_site_layer = self.controller.get_development_sites_layer()

    def tearDown(self):
        super().tearDown()
        self._temp_dir.cleanup()

    def _add_project_area(self, name: str, rect: QgsRectangle) -> QgsFeature:
        self.project_area_layer.startEditing()
        self.create_project_area(self.project_area_layer, name, rect)
        self.assertTrue(self.project_area_layer.commitChanges())

        for feat in self.project_area_layer.getFeatures():
            if feat["name"] == name:
                return feat
        self.fail(f"Project area '{name}' not found after commit")

    def _add_development_site(
        self,
        name: str,
        project_area_pk: int,
        rect: QgsRectangle,
        base_height: float = 0.0,
    ) -> QgsFeature:
        self.development_site_layer.startEditing()
        self.create_development_site(
            self.development_site_layer,
            name,
            project_area_pk,
            rect,
            base_height=base_height,
        )
        self.assertTrue(self.development_site_layer.commitChanges())

        for feat in self.development_site_layer.getFeatures():
            if feat["name"] == name:
                return feat
        self.fail(f"Development site '{name}' not found after commit")

    def _create_source_layer(
        self,
        features_data: list[dict],
        crs_authid: str | None = None,
    ) -> QgsVectorLayer:
        if crs_authid is None:
            crs_authid = self.development_site_layer.crs().authid()

        layer = QgsVectorLayer(f"Polygon?crs={crs_authid}", "source_sites", "memory")
        provider = layer.dataProvider()
        provider.addAttributes(
            [
                QgsField("status", QVariant.String),
                QgsField("name", QVariant.String),
                QgsField("addr", QVariant.String),
                QgsField("owner", QVariant.String),
                QgsField("yr", QVariant.String),
            ]
        )
        layer.updateFields()

        features = []
        for item in features_data:
            feat = QgsFeature(layer.fields())
            if "geom" in item and item["geom"] is not None:
                feat.setGeometry(item["geom"])
            feat["status"] = item.get("status")
            feat["name"] = item.get("name")
            feat["addr"] = item.get("addr")
            feat["owner"] = item.get("owner")
            feat["yr"] = item.get("yr")
            features.append(feat)

        self.assertTrue(provider.addFeatures(features)[0])
        return layer

    def _run_algorithm(self, parameters: dict):
        alg = ImportDevelopmentSitesAlgorithm()
        alg.initAlgorithm()
        context = QgsProcessingContext()
        context.setProject(self.project)
        feedback = QgsProcessingFeedback()

        self.assertTrue(alg.prepareAlgorithm(parameters, context, feedback))
        alg.processAlgorithm(parameters, context, feedback)
        return alg.postProcessAlgorithm(context, feedback)

    def test_missing_layers(self):
        """
        Test prepareAlgorithm raises QgsProcessingException when required layers are missing
        """
        source = self._create_source_layer([])
        self.project.removeMapLayer(self.project_area_layer.id())

        alg = ImportDevelopmentSitesAlgorithm()
        alg.initAlgorithm()
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        with self.assertRaises(QgsProcessingException):
            alg.prepareAlgorithm(
                {
                    ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Area One",
                    ImportDevelopmentSitesAlgorithm.INPUT: source,
                },
                context,
                feedback,
            )

        self.controller.add_database_layers_to_project(self.project, self.gpkg_path)
        self.project.removeMapLayer(self.controller.get_development_sites_layer().id())

        with self.assertRaises(QgsProcessingException):
            alg.prepareAlgorithm(
                {
                    ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Area One",
                    ImportDevelopmentSitesAlgorithm.INPUT: source,
                },
                context,
                feedback,
            )

    def test_import_and_attribute_mapping(self):
        """
        Test importing valid polygons into target project area and mapping attributes
        """
        pa = self._add_project_area("Precinct A", QgsRectangle(0, 0, 200, 200))
        source = self._create_source_layer(
            [
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(10, 10, 40, 40)),
                    "status": "Approved",
                    "name": "Alpha Tower",
                    "addr": "10 Main St",
                    "owner": "Acme Corp",
                    "yr": "2026",
                },
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(60, 10, 90, 40)),
                    "status": "Proposed",
                    "name": None,
                    "addr": "20 Main St",
                    "owner": "Beta Ltd",
                    "yr": "not_an_int",
                },
                {
                    "geom": None,
                    "name": "Null Geometry Site",
                },
            ]
        )

        results = self._run_algorithm(
            {
                ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Precinct A",
                ImportDevelopmentSitesAlgorithm.INPUT: source,
                ImportDevelopmentSitesAlgorithm.SITE_STATUS_FIELD: "status",
                ImportDevelopmentSitesAlgorithm.NAME_FIELD: "name",
                ImportDevelopmentSitesAlgorithm.ADDRESS_FIELD: "addr",
                ImportDevelopmentSitesAlgorithm.SITE_OWNER_FIELD: "owner",
                ImportDevelopmentSitesAlgorithm.YEAR_FIELD: "yr",
            }
        )

        self.assertEqual(
            results,
            {ImportDevelopmentSitesAlgorithm.OUTPUT: self.development_site_layer.id()},
        )
        self.assertFalse(self.development_site_layer.isEditable())

        imported = list(self.development_site_layer.getFeatures())
        self.assertEqual(len(imported), 2)

        by_addr = {f["address"]: f for f in imported}
        alpha = by_addr["10 Main St"]
        self.assertEqual(alpha["project_area_pk"], pa["fid"])
        self.assertEqual(alpha["name"], "Alpha Tower")
        self.assertEqual(alpha["site_owner"], "Acme Corp")
        if self.development_site_layer.fields().lookupField("site_status") >= 0:
            self.assertEqual(alpha["site_status"], "Approved")
        if self.development_site_layer.fields().lookupField("year") >= 0:
            self.assertEqual(alpha["year"], 2026)

        second = by_addr["20 Main St"]
        self.assertEqual(second["project_area_pk"], pa["fid"])
        self.assertEqual(second["site_owner"], "Beta Ltd")

    def test_project_area_containment_and_tolerance(self):
        """
        Test 95% overlap threshold when ONLY_WITHIN=False and strict containment when ONLY_WITHIN=True
        """
        self._add_project_area("Precinct A", QgsRectangle(0, 0, 100, 100))

        source = self._create_source_layer(
            [
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(10, 10, 30, 30)),
                    "name": "Wholly Within",
                },
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(76, 10, 101, 30)),
                    "name": "Within Tolerance",
                },
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(80, 40, 105, 60)),
                    "name": "Exceeds Tolerance",
                },
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(150, 10, 170, 30)),
                    "name": "Outside",
                },
            ]
        )

        # With ONLY_WITHIN=False, both Wholly Within and Within Tolerance are imported
        self._run_algorithm(
            {
                ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Precinct A",
                ImportDevelopmentSitesAlgorithm.INPUT: source,
                ImportDevelopmentSitesAlgorithm.ONLY_WITHIN: False,
                ImportDevelopmentSitesAlgorithm.NAME_FIELD: "name",
            }
        )
        names = [f["name"] for f in self.development_site_layer.getFeatures()]
        self.assertCountEqual(names, ["Wholly Within", "Within Tolerance"])

        # Clear development sites and test ONLY_WITHIN=True
        self.development_site_layer.startEditing()
        self.development_site_layer.deleteFeatures(
            [f.id() for f in self.development_site_layer.getFeatures()]
        )
        self.assertTrue(self.development_site_layer.commitChanges())

        self._run_algorithm(
            {
                ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Precinct A",
                ImportDevelopmentSitesAlgorithm.INPUT: source,
                ImportDevelopmentSitesAlgorithm.ONLY_WITHIN: True,
                ImportDevelopmentSitesAlgorithm.NAME_FIELD: "name",
            }
        )
        names = [f["name"] for f in self.development_site_layer.getFeatures()]
        self.assertEqual(names, ["Wholly Within"])

    def test_extent_filter_and_clip(self):
        """
        Test EXTENT filters features and CLIP_FEATURES=True clips geometries to the extent
        """
        self._add_project_area("Precinct A", QgsRectangle(0, 0, 200, 200))
        source = self._create_source_layer(
            [
                # Straddles extent boundary x=50: x in [30, 70] (40x20 = 800)
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(30, 10, 70, 30)),
                    "name": "Straddling Site",
                },
                # Outside extent [0, 50] x [0, 100]: x in [80, 110]
                {
                    "geom": QgsGeometry.fromRect(QgsRectangle(80, 10, 110, 30)),
                    "name": "Outside Extent Site",
                },
            ]
        )
        extent = QgsRectangle(0, 0, 50, 100)

        # Without clipping: Straddling Site imported at full 800 area
        self._run_algorithm(
            {
                ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Precinct A",
                ImportDevelopmentSitesAlgorithm.INPUT: source,
                ImportDevelopmentSitesAlgorithm.EXTENT: extent,
                ImportDevelopmentSitesAlgorithm.CLIP_FEATURES: False,
                ImportDevelopmentSitesAlgorithm.NAME_FIELD: "name",
            }
        )
        features = list(self.development_site_layer.getFeatures())
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["name"], "Straddling Site")
        self.assertAlmostEqual(features[0].geometry().area(), 800.0)

        # Clear and re-run with CLIP_FEATURES=True: clipped to [30, 50] x [10, 30] (20x20 = 400)
        self.development_site_layer.startEditing()
        self.development_site_layer.deleteFeature(features[0].id())
        self.assertTrue(self.development_site_layer.commitChanges())

        self._run_algorithm(
            {
                ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Precinct A",
                ImportDevelopmentSitesAlgorithm.INPUT: source,
                ImportDevelopmentSitesAlgorithm.EXTENT: extent,
                ImportDevelopmentSitesAlgorithm.CLIP_FEATURES: True,
                ImportDevelopmentSitesAlgorithm.NAME_FIELD: "name",
            }
        )
        features = list(self.development_site_layer.getFeatures())
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["name"], "Straddling Site")
        self.assertAlmostEqual(features[0].geometry().area(), 400.0)

    def test_different_crs(self):
        """
        Test importing features from a source layer in a different CRS
        """
        self._add_project_area("Precinct A", QgsRectangle(0, 0, 100, 100))

        target_crs = self.development_site_layer.crs()
        alt_crs = (
            QgsCoordinateReferenceSystem("EPSG:3857")
            if target_crs.authid() == "EPSG:4326"
            else QgsCoordinateReferenceSystem("EPSG:4326")
        )
        transform = QgsCoordinateTransform(target_crs, alt_crs, self.project)

        src_geom = QgsGeometry.fromRect(QgsRectangle(10, 10, 40, 40))
        src_geom.transform(transform)

        source = self._create_source_layer(
            [{"geom": src_geom, "name": "Reprojected Site"}],
            crs_authid=alt_crs.authid(),
        )

        self._run_algorithm(
            {
                ImportDevelopmentSitesAlgorithm.PROJECT_AREA: "Precinct A",
                ImportDevelopmentSitesAlgorithm.INPUT: source,
                ImportDevelopmentSitesAlgorithm.NAME_FIELD: "name",
            }
        )

        features = list(self.development_site_layer.getFeatures())
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["name"], "Reprojected Site")
        bbox = features[0].geometry().boundingBox()
        self.assertAlmostEqual(bbox.xMinimum(), 10.0, places=3)
        self.assertAlmostEqual(bbox.yMinimum(), 10.0, places=3)
        self.assertAlmostEqual(bbox.xMaximum(), 40.0, places=3)
        self.assertAlmostEqual(bbox.yMaximum(), 40.0, places=3)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestImportDevelopmentSitesAlgorithm
    )
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
