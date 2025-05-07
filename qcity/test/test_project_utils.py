import unittest
import os
import tempfile

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
)

from qcity.core.project import ProjectController

from qcity.core.database import DatabaseUtils
from qcity.core import LayerType

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
            controller = ProjectController(p)
            self.assertIsNone(controller.get_project_area_layer())
            self.assertIsNone(controller.get_development_sites_layer())
            self.assertIsNone(controller.get_building_levels_layer())
            self.assertIsNone(controller.get_layer(LayerType.ProjectAreas))
            self.assertIsNone(controller.get_layer(LayerType.BuildingLevels))
            self.assertIsNone(controller.get_layer(LayerType.DevelopmentSites))

            controller.add_database_layers_to_project(p, gpkg_path)
            self.assertEqual(len(p.mapLayers()), 3)

            project_area_layer = controller.get_project_area_layer()
            self.assertIsInstance(project_area_layer, QgsVectorLayer)
            self.assertTrue(project_area_layer.isValid())
            self.assertGreaterEqual(project_area_layer.fields().lookupField('dwelling_size_4_bedroom'), 0)
            self.assertEqual(controller.get_layer( LayerType.ProjectAreas), project_area_layer)

            development_sites_layer = controller.get_development_sites_layer()
            self.assertIsInstance(development_sites_layer, QgsVectorLayer)
            self.assertGreaterEqual(development_sites_layer.fields().lookupField('site_owner'), 0)
            self.assertEqual(controller.get_layer(LayerType.DevelopmentSites), development_sites_layer)

            building_areas_layer = controller.get_building_levels_layer()
            self.assertIsInstance(building_areas_layer, QgsVectorLayer)
            self.assertGreaterEqual(building_areas_layer.fields().lookupField('count_1_bedroom_dwellings'), 0)
            self.assertEqual(controller.get_layer(LayerType.BuildingLevels), building_areas_layer)

    def test_layer_relations(self):
        """
        Test creating layer relations
        """
        p = QgsProject()
        controller = ProjectController(p)
        controller.create_layer_relations()
        self.assertEqual(len(p.relationManager().relations()), 0)
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            controller.add_database_layers_to_project(p, gpkg_path)
            controller.create_layer_relations()
            self.assertEqual(len(p.relationManager().relations()), 2)

            area_to_site = [p.relationManager().relation(r) for r in p.relationManager().relations() if p.relationManager().relation(r).referencedLayer() == controller.get_project_area_layer()][0]
            self.assertEqual(area_to_site.referencingLayer(), controller.get_development_sites_layer())
            site_to_level = [p.relationManager().relation(r) for r in p.relationManager().relations() if p.relationManager().relation(r).referencedLayer() == controller.get_development_sites_layer()][0]
            self.assertEqual(site_to_level.referencingLayer(), controller.get_building_levels_layer())

    def test_project_database_path(self):
        """
        Test associated database path
        """
        p = QgsProject()
        controller = ProjectController(p)
        self.assertFalse(controller.associated_database_path())

        controller.set_associated_database_path('xxx')
        self.assertEqual(controller.associated_database_path(), 'xxx')

        p2 = QgsProject()
        controller2 = ProjectController(p2)
        self.assertEqual(controller.associated_database_path(), 'xxx')
        self.assertFalse(controller2.associated_database_path())
