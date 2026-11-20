import os
import tempfile
import unittest

from qgis.PyQt.QtCore import QCoreApplication
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
)

from qcity.core import (
    DatabaseUtils,
    get_project_controller,
    reset_project_controller,
)
from qcity.core.processing.reassign_building_levels import (
    ReassignBuildingLevelsAlgorithm,
)
from qcity.test.qcity_test_base import QCityTestBase
from qcity.test.utilities import get_qgis_app


class TestReassignBuildingLevelsAlgorithm(QCityTestBase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCity_reassign_building_levels")
        QCoreApplication.setOrganizationDomain("qcity_reassign_building_levels")
        QCoreApplication.setApplicationName("qcity_reassign_building_levels")

        get_qgis_app()
        QgsSettings().clear()

    def setUp(self):
        super().setUp()
        reset_project_controller()
        self.project = QgsProject.instance()
        self.project.clear()

        self._temp_dir = tempfile.TemporaryDirectory()
        self.gpkg_path = os.path.join(self._temp_dir.name, "test_database.gpkg")
        DatabaseUtils.create_base_tables(self.gpkg_path)

        self.controller = get_project_controller()
        self.controller.add_database_layers_to_project(self.project, self.gpkg_path)

        self.project_area_layer = self.controller.get_project_area_layer()
        self.development_site_layer = self.controller.get_development_sites_layer()
        self.building_level_layer = self.controller.get_building_levels_layer()

    def tearDown(self):
        reset_project_controller()
        self.project.clear()
        self._temp_dir.cleanup()
        super().tearDown()

    def _run_algorithm(self, parameters=None):
        if parameters is None:
            parameters = {}
        alg = ReassignBuildingLevelsAlgorithm()
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
        self.project.removeMapLayer(self.building_level_layer.id())
        alg = ReassignBuildingLevelsAlgorithm()
        alg.initAlgorithm()
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        with self.assertRaises(QgsProcessingException):
            alg.prepareAlgorithm({}, context, feedback)

        self.controller.add_database_layers_to_project(self.project, self.gpkg_path)
        self.project.removeMapLayer(self.controller.get_development_sites_layer().id())

        with self.assertRaises(QgsProcessingException):
            alg.prepareAlgorithm({}, context, feedback)

    def test_invalid_project_area_name(self):
        """
        Test prepareAlgorithm raises QgsProcessingException for an unknown project area name
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()
        self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 100, 100)
        )

        alg = ReassignBuildingLevelsAlgorithm()
        alg.initAlgorithm()
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        with self.assertRaises(QgsProcessingException):
            alg.prepareAlgorithm(
                {ReassignBuildingLevelsAlgorithm.PROJECT_AREA: "Nonexistent Area"},
                context,
                feedback,
            )

    def test_only_selected_empty(self):
        """
        Test prepareAlgorithm raises QgsProcessingException when ONLY_SELECTED is True and nothing is selected
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()
        pa = self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 100, 100)
        )
        ds = self.create_development_site(
            self.development_site_layer, "Site A", pa["fid"], QgsRectangle(0, 0, 50, 50)
        )
        self.create_building_level(
            self.building_level_layer,
            "Level 1",
            ds["fid"],
            QgsGeometry.fromRect(QgsRectangle(5, 5, 25, 25)),
        )

        self.building_level_layer.removeSelection()
        alg = ReassignBuildingLevelsAlgorithm()
        alg.initAlgorithm()
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        with self.assertRaises(QgsProcessingException):
            alg.prepareAlgorithm(
                {ReassignBuildingLevelsAlgorithm.ONLY_SELECTED: True},
                context,
                feedback,
            )

    def test_reassign_to_most_overlapping_site(self):
        """
        Test building level is reassigned to the site it overlaps most, commits changes,
        and updates floorspace and floor heights on affected sites.
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()
        pa = self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 200, 200)
        )
        # Alpha Site: x in [0, 52], Beta Site: x in [52, 150]
        ds_alpha = self.create_development_site(
            self.development_site_layer,
            "Alpha Site",
            pa["fid"],
            QgsRectangle(0, 0, 52, 100),
        )
        ds_beta = self.create_development_site(
            self.development_site_layer,
            "Beta Site",
            pa["fid"],
            QgsRectangle(52, 0, 150, 100),
            base_height=2.0,
        )

        # Building level spans x in [50, 100] (50m wide):
        # 4% overlaps Alpha Site, 96% overlaps Beta Site (within 5% tolerance)
        level = self.create_building_level(
            self.building_level_layer,
            "Level 1",
            development_site_pk=ds_alpha["fid"],
            geom=QgsGeometry.fromRect(QgsRectangle(50, 10, 100, 30)),
            level_index=3,
            level_height=4.0,
        )

        results = self._run_algorithm()

        self.assertEqual(
            results,
            {ReassignBuildingLevelsAlgorithm.OUTPUT: self.building_level_layer.id()},
        )

        updated_level = self.building_level_layer.getFeature(level.id())
        self.assertEqual(updated_level["development_site_pk"], ds_beta["fid"])

    def test_already_assigned_unchanged(self):
        """
        Test building levels already linked to their best-overlapping site remain unchanged
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()

        pa = self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 100, 100)
        )
        ds = self.create_development_site(
            self.development_site_layer,
            "Site A",
            pa["fid"],
            QgsRectangle(0, 0, 100, 100),
        )
        level = self.create_building_level(
            self.building_level_layer,
            "Level 1",
            ds["fid"],
            QgsGeometry.fromRect(QgsRectangle(10, 10, 40, 40)),
        )

        self._run_algorithm()

        self.assertEqual(
            self.building_level_layer.getFeature(level.id())["development_site_pk"],
            ds["fid"],
        )

    def test_outside_tolerance_skipped(self):
        """
        Test building level with >5% area outside the best development site is not reassigned
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()

        pa = self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 200, 200)
        )
        ds_a = self.create_development_site(
            self.development_site_layer, "Site A", pa["fid"], QgsRectangle(0, 0, 50, 50)
        )
        self.create_development_site(
            self.development_site_layer,
            "Site B",
            pa["fid"],
            QgsRectangle(100, 0, 150, 50),
        )

        # 80% inside Site B (x in [110, 150]), 20% outside (x in [150, 160])
        level = self.create_building_level(
            self.building_level_layer,
            "Level 1",
            development_site_pk=ds_a["fid"],
            geom=QgsGeometry.fromRect(QgsRectangle(110, 10, 160, 30)),
        )

        self._run_algorithm()

        self.assertEqual(
            self.building_level_layer.getFeature(level.id())["development_site_pk"],
            ds_a["fid"],
        )

    def test_no_overlap_and_empty_geometry_skipped(self):
        """
        Test building levels with no overlapping development site or empty geometry are skipped
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()
        pa = self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 200, 200)
        )
        ds = self.create_development_site(
            self.development_site_layer, "Site A", pa["fid"], QgsRectangle(0, 0, 50, 50)
        )

        disjoint_level = self.create_building_level(
            self.building_level_layer,
            "Disjoint Level",
            development_site_pk=ds["fid"],
            geom=QgsGeometry.fromRect(QgsRectangle(120, 120, 140, 140)),
        )
        empty_level = self.create_building_level(
            self.building_level_layer,
            "Empty Level",
            development_site_pk=ds["fid"],
            geom=QgsGeometry(),
        )

        self._run_algorithm()

        self.assertEqual(
            self.building_level_layer.getFeature(disjoint_level.id())[
                "development_site_pk"
            ],
            ds["fid"],
        )
        self.assertEqual(
            self.building_level_layer.getFeature(empty_level.id())[
                "development_site_pk"
            ],
            ds["fid"],
        )

    def test_only_selected(self):
        """
        Test ONLY_SELECTED=True restricts reassignment to selected building levels
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()
        pa = self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 200, 200)
        )
        ds_a = self.create_development_site(
            self.development_site_layer, "Site A", pa["fid"], QgsRectangle(0, 0, 50, 50)
        )
        ds_b = self.create_development_site(
            self.development_site_layer,
            "Site B",
            pa["fid"],
            QgsRectangle(100, 0, 150, 50),
        )

        selected_level = self.create_building_level(
            self.building_level_layer,
            "Selected Level",
            development_site_pk=ds_a["fid"],
            geom=QgsGeometry.fromRect(QgsRectangle(110, 10, 130, 30)),
        )
        unselected_level = self.create_building_level(
            self.building_level_layer,
            "Unselected Level",
            development_site_pk=ds_a["fid"],
            geom=QgsGeometry.fromRect(QgsRectangle(110, 30, 130, 45)),
        )

        self.building_level_layer.selectByIds([selected_level.id()])

        self._run_algorithm({ReassignBuildingLevelsAlgorithm.ONLY_SELECTED: True})

        self.assertEqual(
            self.building_level_layer.getFeature(selected_level.id())[
                "development_site_pk"
            ],
            ds_b["fid"],
        )
        self.assertEqual(
            self.building_level_layer.getFeature(unselected_level.id())[
                "development_site_pk"
            ],
            ds_a["fid"],
        )

    def test_filter_by_project_area(self):
        """
        Test INPUT parameter restricts candidate development sites to the named project area
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()
        pa_north = self.create_project_area(
            self.project_area_layer, "North Precinct", QgsRectangle(0, 0, 100, 100)
        )
        pa_south = self.create_project_area(
            self.project_area_layer, "South Precinct", QgsRectangle(100, 0, 200, 100)
        )

        ds_north = self.create_development_site(
            self.development_site_layer,
            "North Site",
            pa_north["fid"],
            QgsRectangle(10, 10, 90, 90),
        )
        ds_south = self.create_development_site(
            self.development_site_layer,
            "South Site",
            pa_south["fid"],
            QgsRectangle(110, 10, 190, 90),
        )

        # Physically over South Site, currently linked to North Site
        level = self.create_building_level(
            self.building_level_layer,
            "Level 1",
            development_site_pk=ds_north["fid"],
            geom=QgsGeometry.fromRect(QgsRectangle(120, 20, 150, 50)),
        )

        # Filtering to North Precinct excludes South Site
        self._run_algorithm(
            {ReassignBuildingLevelsAlgorithm.PROJECT_AREA: "North Precinct"}
        )
        self.assertEqual(
            self.building_level_layer.getFeature(level.id())["development_site_pk"],
            ds_north["fid"],
        )

        # Filtering to South Precinct reassigns to South Site
        self._run_algorithm(
            {ReassignBuildingLevelsAlgorithm.PROJECT_AREA: "South Precinct"}
        )
        self.assertEqual(
            self.building_level_layer.getFeature(level.id())["development_site_pk"],
            ds_south["fid"],
        )

    def test_different_crs(self):
        """
        Test spatial overlap works when development sites and building levels use different CRSs
        """
        self.project_area_layer.startEditing()
        self.development_site_layer.startEditing()
        self.building_level_layer.startEditing()
        pa = self.create_project_area(
            self.project_area_layer, "Area One", QgsRectangle(0, 0, 200, 200)
        )

        # Replace development sites layer with a layer in a different CRS
        src_crs = self.building_level_layer.crs()
        alt_crs = (
            QgsCoordinateReferenceSystem("EPSG:3857")
            if src_crs.authid() == "EPSG:4326"
            else QgsCoordinateReferenceSystem("EPSG:4326")
        )
        transform = QgsCoordinateTransform(src_crs, alt_crs, self.project)

        fields = self.development_site_layer.fields()
        self.project.removeMapLayer(self.development_site_layer.id())

        self.development_site_layer = QgsVectorLayer(
            f"Polygon?crs={alt_crs.authid()}", "development_sites", "memory"
        )
        self.development_site_layer.setCustomProperty(
            "_qcity_role", "development_sites"
        )
        self.development_site_layer.dataProvider().addAttributes(fields.toList())
        self.development_site_layer.updateFields()
        self.project.addMapLayer(self.development_site_layer)

        self.development_site_layer.startEditing()

        rect_a = transform.transformBoundingBox(QgsRectangle(0, 0, 50, 50))
        rect_b = transform.transformBoundingBox(QgsRectangle(100, 0, 150, 50))
        ds_a = self.create_development_site(
            self.development_site_layer, "Site A", pa["fid"], rect_a
        )
        ds_b = self.create_development_site(
            self.development_site_layer, "Site B", pa["fid"], rect_b
        )

        level = self.create_building_level(
            self.building_level_layer,
            "Level 1",
            development_site_pk=ds_a["fid"],
            geom=QgsGeometry.fromRect(QgsRectangle(110, 10, 130, 30)),
        )

        self._run_algorithm()

        self.assertEqual(
            self.building_level_layer.getFeature(level.id())["development_site_pk"],
            ds_b["fid"],
        )


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestReassignBuildingLevelsAlgorithm
    )
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
