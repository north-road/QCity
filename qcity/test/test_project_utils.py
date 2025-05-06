import unittest
import os
import tempfile

from qgis.PyQt.QtCore import QVariant

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
)
from sphinx.project import Project

from qcity.core.project import ProjectUtils
from qcity.core.settings import SETTINGS_MANAGER

from qcity.test.utilities import get_qgis_app
from qcity.core.database import DatabaseUtils

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestProjectUtils(unittest.TestCase):

    def test_add_layers(self) -> None:
        """
        Test adding database layers to a project
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject()
            self.assertIsNone(ProjectUtils.get_project_area_layer(p))
            self.assertIsNone(ProjectUtils.get_development_sites_layer(p))
            self.assertIsNone(ProjectUtils.get_building_levels_layer(p))

            ProjectUtils.add_database_layers_to_project(p, gpkg_path)
            self.assertEqual(len(p.mapLayers()), 3)

            project_area_layer = ProjectUtils.get_project_area_layer(p)
            self.assertIsInstance(project_area_layer, QgsVectorLayer)
            self.assertTrue(project_area_layer.isValid())
            self.assertGreaterEqual(project_area_layer.fields().lookupField('dwelling_size_4_bedroom'), 0)

            development_sites_layer = ProjectUtils.get_development_sites_layer(p)
            self.assertIsInstance(development_sites_layer, QgsVectorLayer)
            self.assertGreaterEqual(development_sites_layer.fields().lookupField('site_owner'), 0)

            building_areas_layer = ProjectUtils.get_building_levels_layer(p)
            self.assertIsInstance(building_areas_layer, QgsVectorLayer)
            self.assertGreaterEqual(building_areas_layer.fields().lookupField('count_1_bedroom_dwellings'), 0)

    def test_layer_relations(self):
        """
        Test creating layer relations
        """
        p = QgsProject()
        ProjectUtils.create_layer_relations(p)
        self.assertEqual(len(p.relationManager().relations()), 0)
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            ProjectUtils.add_database_layers_to_project(p, gpkg_path)
            ProjectUtils.create_layer_relations(p)
            self.assertEqual(len(p.relationManager().relations()), 2)

            area_to_site = [p.relationManager().relation(r) for r in p.relationManager().relations() if p.relationManager().relation(r).referencedLayer() == ProjectUtils.get_project_area_layer(p)][0]
            self.assertEqual(area_to_site.referencingLayer(), ProjectUtils.get_development_sites_layer(p))
            site_to_level = [p.relationManager().relation(r) for r in p.relationManager().relations() if p.relationManager().relation(r).referencedLayer() == ProjectUtils.get_development_sites_layer(p)][0]
            self.assertEqual(site_to_level.referencingLayer(), ProjectUtils.get_building_levels_layer(p))

    def test_project_database_path(self):
        """
        Test associated database path
        """
        p = QgsProject()
        self.assertFalse(ProjectUtils.associated_database_path(p))

        ProjectUtils.set_associated_database_path(p, 'xxx')
        self.assertEqual(ProjectUtils.associated_database_path(p), 'xxx')

        p2 = QgsProject()
        self.assertEqual(ProjectUtils.associated_database_path(p), 'xxx')
        self.assertFalse(ProjectUtils.associated_database_path(p2))

