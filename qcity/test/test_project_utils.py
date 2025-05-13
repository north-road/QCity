import unittest
import os
import tempfile

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtTest import QSignalSpy

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsVectorLayerUtils,
    QgsSettings
)

from qcity.core.project import ProjectController

from qcity.core import DatabaseUtils, LayerUtils, LayerType

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")

from .utilities import get_qgis_app


class TestProjectUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        super().setUpClass()
        QCoreApplication.setOrganizationName("QCiy_project_utils")
        QCoreApplication.setOrganizationDomain("qcity_project_utils")
        QCoreApplication.setApplicationName("qcity_project_utils")

        _, CANVAS, cls.iface, cls.PARENT = get_qgis_app()
        QgsSettings().clear()

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
            self.assertGreaterEqual(building_areas_layer.fields().lookupField('percent_1_bedroom_floorspace'), 0)
            self.assertEqual(controller.get_layer(LayerType.BuildingLevels), building_areas_layer)
            controller.cleanup()
            p.clear()

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
            controller.cleanup()
            p.clear()

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
        controller.cleanup()
        controller2.cleanup()
        p.clear()
        p2.clear()

    def test_delete_project_area(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject.instance()
            controller = ProjectController(p)
            controller.add_database_layers_to_project(p, gpkg_path)

            project_area_added_spy = QSignalSpy(controller.project_area_added)
            development_site_added_spy = QSignalSpy(controller.development_site_added)
            building_level_added_spy = QSignalSpy(controller.building_level_added)
            project_area_deleted_spy = QSignalSpy(controller.project_area_deleted)
            development_site_deleted_spy = QSignalSpy(controller.development_site_deleted)
            building_level_deleted_spy = QSignalSpy(controller.building_level_deleted)

            project_area_layer = controller.get_project_area_layer()
            project_area_layer.startEditing()
            # create some initial features
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 1
            f['car_parking_2_bedroom'] = 2
            f['car_parking_3_bedroom'] = 3
            f['car_parking_4_bedroom'] = 4
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 11
            f['car_parking_2_bedroom'] = 12
            f['car_parking_3_bedroom'] = 13
            f['car_parking_4_bedroom'] = 14
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 21
            f['car_parking_2_bedroom'] = 22
            f['car_parking_3_bedroom'] = 23
            f['car_parking_4_bedroom'] = 24
            self.assertTrue(project_area_layer.addFeature(f))
            # no signals for uncommitted features
            self.assertEqual(len(project_area_added_spy), 0)
            self.assertEqual(len(development_site_added_spy), 0)
            self.assertEqual(len(building_level_added_spy), 0)

            self.assertTrue(project_area_layer.commitChanges())
            self.assertEqual(len(project_area_added_spy), 3)
            self.assertEqual(len(development_site_added_spy), 0)
            self.assertEqual(len(building_level_added_spy), 0)
            self.assertEqual(len(project_area_deleted_spy), 0)
            self.assertEqual(len(development_site_deleted_spy), 0)
            self.assertEqual(len(building_level_deleted_spy), 0)

            f1 = None
            f2 = None
            f3 = None
            for f in project_area_layer.getFeatures():
                if f['car_parking_1_bedroom'] == 1:
                    f1 = f
                elif f['car_parking_1_bedroom'] == 11:
                    f2 = f
                elif f['car_parking_1_bedroom'] == 21:
                    f3 = f

            f1_pk = f1['fid']
            f2_pk = f2['fid']

            development_site_layer = controller.get_development_sites_layer()
            development_site_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a1'
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a2'
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f2_pk
            f['address'] = 'b1'
            self.assertTrue(development_site_layer.addFeature(f))

            # no signals for uncommitted features
            self.assertEqual(len(project_area_added_spy), 3)
            self.assertEqual(len(development_site_added_spy), 0)
            self.assertEqual(len(building_level_added_spy), 0)

            self.assertTrue(development_site_layer.commitChanges())
            self.assertEqual(len(project_area_added_spy), 3)
            self.assertEqual(len(development_site_added_spy), 3)
            self.assertEqual(len(building_level_added_spy), 0)

            ds1 = None
            ds2 = None
            ds3 = None
            for f in development_site_layer.getFeatures():
                if f['address'] == 'a1':
                    ds1 = f
                elif f['address'] == 'a2':
                    ds2 = f
                elif f['address'] == 'b1':
                    ds3 = f

            ds1_pk = ds1['fid']
            ds3_pk = ds3['fid']

            # make some building levels

            building_level_layer = controller.get_building_levels_layer()
            building_level_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 44
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 45
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds3_pk
            f['percent_office_floorspace'] = 46
            self.assertTrue(building_level_layer.addFeature(f))
            # no signals for uncommitted features
            self.assertEqual(len(project_area_added_spy), 3)
            self.assertEqual(len(development_site_added_spy), 3)
            self.assertEqual(len(building_level_added_spy), 0)
            self.assertTrue(building_level_layer.commitChanges())
            self.assertEqual(len(project_area_added_spy), 3)
            self.assertEqual(len(development_site_added_spy), 3)
            self.assertEqual(len(building_level_added_spy), 3)

            bl1 = None
            bl2 = None
            bl3 = None
            for f in building_level_layer.getFeatures():
                if f['percent_office_floorspace'] == 44:
                    bl1 = f
                elif f['percent_office_floorspace'] == 45:
                    bl2 = f
                elif f['percent_office_floorspace'] == 46:
                    bl3 = f

            # delete project area which doesn't exist
            self.assertFalse(
                controller.delete_project_area(1111)
            )
            # nothing should have changed
            self.assertEqual(len(list(project_area_layer.getFeatures())), 3)
            self.assertFalse(project_area_layer.isEditable())
            self.assertEqual(len(list(development_site_layer.getFeatures())), 3)
            self.assertFalse(development_site_layer.isEditable())
            self.assertEqual(len(list(building_level_layer.getFeatures())), 3)
            self.assertFalse(building_level_layer.isEditable())
            self.assertEqual(len(project_area_deleted_spy), 0)
            self.assertEqual(len(development_site_deleted_spy), 0)
            self.assertEqual(len(building_level_deleted_spy), 0)

            # delete a valid project area
            self.assertTrue(controller.delete_project_area(f1.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f2.id(), f3.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertCountEqual([f.id() for f in development_site_layer.getFeatures()],
                                  [ds3.id()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertCountEqual([f.id() for f in building_level_layer.getFeatures()],
                                  [bl3.id()])
            self.assertFalse(building_level_layer.isEditable())
            self.assertEqual(len(project_area_deleted_spy), 1)
            self.assertEqual(len(development_site_deleted_spy), 2)
            self.assertEqual(len(building_level_deleted_spy), 2)

            # nothing attached
            self.assertTrue(controller.delete_project_area(f3.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f2.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertCountEqual([f.id() for f in development_site_layer.getFeatures()],
                                  [ds3.id()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertCountEqual([f.id() for f in building_level_layer.getFeatures()],
                                  [bl3.id()])
            self.assertFalse(building_level_layer.isEditable())
            self.assertEqual(len(project_area_deleted_spy), 2)
            self.assertEqual(len(development_site_deleted_spy), 2)
            self.assertEqual(len(building_level_deleted_spy), 2)

            self.assertTrue(controller.delete_project_area(f2.id()))
            self.assertFalse([f.id() for f in project_area_layer.getFeatures()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertFalse([f.id() for f in development_site_layer.getFeatures()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertFalse([f.id() for f in building_level_layer.getFeatures()])
            self.assertFalse(building_level_layer.isEditable())
            self.assertEqual(len(project_area_deleted_spy), 3)
            self.assertEqual(len(development_site_deleted_spy), 3)
            self.assertEqual(len(building_level_deleted_spy), 3)
            controller.cleanup()
            p.clear()

    def test_delete_development_site(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject.instance()
            controller = ProjectController(p)
            controller.add_database_layers_to_project(p, gpkg_path)

            project_area_layer = controller.get_project_area_layer()
            project_area_layer.startEditing()
            # create some initial features
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 1
            f['car_parking_2_bedroom'] = 2
            f['car_parking_3_bedroom'] = 3
            f['car_parking_4_bedroom'] = 4
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 11
            f['car_parking_2_bedroom'] = 12
            f['car_parking_3_bedroom'] = 13
            f['car_parking_4_bedroom'] = 14
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 21
            f['car_parking_2_bedroom'] = 22
            f['car_parking_3_bedroom'] = 23
            f['car_parking_4_bedroom'] = 24
            self.assertTrue(project_area_layer.addFeature(f))

            self.assertTrue(project_area_layer.commitChanges())

            f1 = None
            f2 = None
            f3 = None
            for f in project_area_layer.getFeatures():
                if f['car_parking_1_bedroom'] == 1:
                    f1 = f
                elif f['car_parking_1_bedroom'] == 11:
                    f2 = f
                elif f['car_parking_1_bedroom'] == 21:
                    f3 = f

            f1_pk = f1['fid']
            f2_pk = f2['fid']

            development_site_layer = controller.get_development_sites_layer()
            development_site_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a1'
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a2'
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f2_pk
            f['address'] = 'b1'
            self.assertTrue(development_site_layer.addFeature(f))
            self.assertTrue(development_site_layer.commitChanges())

            ds1 = None
            ds2 = None
            ds3 = None
            for f in development_site_layer.getFeatures():
                if f['address'] == 'a1':
                    ds1 = f
                elif f['address'] == 'a2':
                    ds2 = f
                elif f['address'] == 'b1':
                    ds3 = f

            ds1_pk = ds1['fid']
            ds3_pk = ds3['fid']

            # make some building levels

            building_level_layer = controller.get_building_levels_layer()
            building_level_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 44
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 45
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds3_pk
            f['percent_office_floorspace'] = 46
            self.assertTrue(building_level_layer.addFeature(f))
            self.assertTrue(building_level_layer.commitChanges())

            bl1 = None
            bl2 = None
            bl3 = None
            for f in building_level_layer.getFeatures():
                if f['percent_office_floorspace'] == 44:
                    bl1 = f
                elif f['percent_office_floorspace'] == 45:
                    bl2 = f
                elif f['percent_office_floorspace'] == 46:
                    bl3 = f

            # delete development site which doesn't exist
            self.assertFalse(
                controller.delete_development_site(1111)
            )
            # nothing should have changed
            self.assertEqual(len(list(project_area_layer.getFeatures())), 3)
            self.assertFalse(project_area_layer.isEditable())
            self.assertEqual(len(list(development_site_layer.getFeatures())), 3)
            self.assertFalse(development_site_layer.isEditable())
            self.assertEqual(len(list(building_level_layer.getFeatures())), 3)
            self.assertFalse(building_level_layer.isEditable())

            # delete a valid development site
            self.assertTrue(controller.delete_development_site(ds1.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f1.id(), f2.id(), f3.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertCountEqual([f.id() for f in development_site_layer.getFeatures()],
                                  [ds2.id(), ds3.id()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertCountEqual([f.id() for f in building_level_layer.getFeatures()],
                                  [bl3.id()])
            self.assertFalse(building_level_layer.isEditable())

            # nothing attached
            self.assertTrue(controller.delete_development_site(ds2.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f1.id(), f2.id(), f3.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertCountEqual([f.id() for f in development_site_layer.getFeatures()],
                                  [ds3.id()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertCountEqual([f.id() for f in building_level_layer.getFeatures()],
                                  [bl3.id()])
            self.assertFalse(building_level_layer.isEditable())

            self.assertTrue(controller.delete_development_site(ds3.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f1.id(), f2.id(), f3.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertFalse([f.id() for f in development_site_layer.getFeatures()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertFalse([f.id() for f in building_level_layer.getFeatures()])
            self.assertFalse(building_level_layer.isEditable())
            controller.cleanup()
            p.clear()

    def test_delete_building_level(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject.instance()
            controller = ProjectController(p)
            controller.add_database_layers_to_project(p, gpkg_path)

            project_area_layer = controller.get_project_area_layer()
            project_area_layer.startEditing()
            # create some initial features
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 1
            f['car_parking_2_bedroom'] = 2
            f['car_parking_3_bedroom'] = 3
            f['car_parking_4_bedroom'] = 4
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 11
            f['car_parking_2_bedroom'] = 12
            f['car_parking_3_bedroom'] = 13
            f['car_parking_4_bedroom'] = 14
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 21
            f['car_parking_2_bedroom'] = 22
            f['car_parking_3_bedroom'] = 23
            f['car_parking_4_bedroom'] = 24
            self.assertTrue(project_area_layer.addFeature(f))

            self.assertTrue(project_area_layer.commitChanges())

            f1 = None
            f2 = None
            f3 = None
            for f in project_area_layer.getFeatures():
                if f['car_parking_1_bedroom'] == 1:
                    f1 = f
                elif f['car_parking_1_bedroom'] == 11:
                    f2 = f
                elif f['car_parking_1_bedroom'] == 21:
                    f3 = f

            f1_pk = f1['fid']
            f2_pk = f2['fid']

            development_site_layer = controller.get_development_sites_layer()
            development_site_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a1'
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a2'
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f2_pk
            f['address'] = 'b1'
            self.assertTrue(development_site_layer.addFeature(f))
            self.assertTrue(development_site_layer.commitChanges())

            ds1 = None
            ds2 = None
            ds3 = None
            for f in development_site_layer.getFeatures():
                if f['address'] == 'a1':
                    ds1 = f
                elif f['address'] == 'a2':
                    ds2 = f
                elif f['address'] == 'b1':
                    ds3 = f

            ds1_pk = ds1['fid']
            ds3_pk = ds3['fid']

            # make some building levels

            building_level_layer = controller.get_building_levels_layer()
            building_level_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 44
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 45
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds3_pk
            f['percent_office_floorspace'] = 46
            self.assertTrue(building_level_layer.addFeature(f))
            self.assertTrue(building_level_layer.commitChanges())

            bl1 = None
            bl2 = None
            bl3 = None
            for f in building_level_layer.getFeatures():
                if f['percent_office_floorspace'] == 44:
                    bl1 = f
                elif f['percent_office_floorspace'] == 45:
                    bl2 = f
                elif f['percent_office_floorspace'] == 46:
                    bl3 = f

            # delete building level which doesn't exist
            self.assertFalse(
                controller.delete_building_level(1111)
            )
            # nothing should have changed
            self.assertEqual(len(list(project_area_layer.getFeatures())), 3)
            self.assertFalse(project_area_layer.isEditable())
            self.assertEqual(len(list(development_site_layer.getFeatures())), 3)
            self.assertFalse(development_site_layer.isEditable())
            self.assertEqual(len(list(building_level_layer.getFeatures())), 3)
            self.assertFalse(building_level_layer.isEditable())

            # delete a valid building level
            self.assertTrue(controller.delete_building_level(bl3.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f1.id(), f2.id(), f3.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertCountEqual([f.id() for f in development_site_layer.getFeatures()],
                                  [ds1.id(), ds2.id(), ds3.id()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertCountEqual([f.id() for f in building_level_layer.getFeatures()],
                                  [bl1.id(), bl2.id()])
            self.assertFalse(building_level_layer.isEditable())

            self.assertTrue(controller.delete_building_level(bl2.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f1.id(), f2.id(), f3.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertCountEqual([f.id() for f in development_site_layer.getFeatures()],
                                  [ds1.id(), ds2.id(), ds3.id()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertEqual([f.id() for f in building_level_layer.getFeatures()],
                                  [bl1.id()])
            self.assertFalse(building_level_layer.isEditable())

            self.assertTrue(controller.delete_building_level(bl1.id()))
            self.assertCountEqual([f.id() for f in project_area_layer.getFeatures()],
                                  [f1.id(), f2.id(), f3.id()])
            self.assertFalse(project_area_layer.isEditable())
            self.assertCountEqual([f.id() for f in development_site_layer.getFeatures()],
                                  [ds1.id(), ds2.id(), ds3.id()])
            self.assertFalse(development_site_layer.isEditable())
            self.assertFalse([f.id() for f in building_level_layer.getFeatures()])
            self.assertFalse(building_level_layer.isEditable())
            controller.cleanup()
            p.clear()

    def test_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject.instance()
            controller = ProjectController(p)
            controller.add_database_layers_to_project(p, gpkg_path)

            project_area_layer = controller.get_project_area_layer()
            project_area_layer.startEditing()
            # create some initial features
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['name'] = 'Feature 1 Name'
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['name'] = "feature 2"
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['name'] = "a3"
            self.assertTrue(project_area_layer.addFeature(f))
            self.assertTrue(project_area_layer.commitChanges())

            development_site_layer = controller.get_development_sites_layer()
            development_site_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['name'] = "dev site 1"
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['name'] = "Development site 2"
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['name'] = "Aaa 3"
            self.assertTrue(development_site_layer.addFeature(f))
            self.assertTrue(development_site_layer.commitChanges())

            # make some building levels
            building_level_layer = controller.get_building_levels_layer()
            building_level_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['name'] = "Floor 3"
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['name'] = "Floor 4"
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['name'] = "floor 1"
            self.assertTrue(building_level_layer.addFeature(f))
            self.assertTrue(building_level_layer.commitChanges())

            self.assertEqual(
                controller.get_unique_names(LayerType.ProjectAreas),
                ['a3', 'Feature 1 Name', 'feature 2']
            )

            self.assertEqual(
                controller.get_unique_names(LayerType.DevelopmentSites),
                ['Aaa 3', 'dev site 1', 'Development site 2']
            )
            self.assertEqual(
                controller.get_unique_names(LayerType.BuildingLevels),
                ['floor 1', 'Floor 3', 'Floor 4']
            )
            controller.cleanup()
            p.clear()

    def test_attribute_change_signals(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject.instance()
            controller = ProjectController(p)
            controller.add_database_layers_to_project(p, gpkg_path)

            project_area_attribute_changed_spy = QSignalSpy(controller.project_area_attribute_changed)
            development_site_attribute_changed_spy = QSignalSpy(controller.development_site_attribute_changed)
            building_level_attribute_changed_spy = QSignalSpy(controller.building_level_attribute_changed)

            project_area_layer = controller.get_project_area_layer()
            project_area_layer.startEditing()
            # create some initial features
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 1
            f['car_parking_2_bedroom'] = 2
            f['car_parking_3_bedroom'] = 3
            f['car_parking_4_bedroom'] = 4
            self.assertTrue(project_area_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 11
            f['car_parking_2_bedroom'] = 12
            f['car_parking_3_bedroom'] = 13
            f['car_parking_4_bedroom'] = 14
            self.assertTrue(project_area_layer.addFeature(f))
            self.assertTrue(project_area_layer.commitChanges())

            f1 = None
            f2 = None
            for f in project_area_layer.getFeatures():
                if f['car_parking_1_bedroom'] == 1:
                    f1 = f
                elif f['car_parking_1_bedroom'] == 11:
                    f2 = f

            f1_pk = f1['fid']
            f2_pk = f2['fid']

            development_site_layer = controller.get_development_sites_layer()
            development_site_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a1'
            self.assertTrue(development_site_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(development_site_layer)
            f['project_area_pk'] = f1_pk
            f['address'] = 'a2'
            self.assertTrue(development_site_layer.addFeature(f))
            self.assertTrue(development_site_layer.commitChanges())

            ds1 = None
            ds2 = None
            for f in development_site_layer.getFeatures():
                if f['address'] == 'a1':
                    ds1 = f
                elif f['address'] == 'a2':
                    ds2 = f

            ds1_pk = ds1['fid']
            ds2_pk = ds2['fid']

            # make some building levels

            building_level_layer = controller.get_building_levels_layer()
            building_level_layer.startEditing()
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 44
            self.assertTrue(building_level_layer.addFeature(f))
            f = QgsVectorLayerUtils.createFeature(building_level_layer)
            f['development_site_pk'] = ds1_pk
            f['percent_office_floorspace'] = 45
            self.assertTrue(building_level_layer.addFeature(f))
            self.assertTrue(building_level_layer.commitChanges())

            bl1 = None
            bl2 = None
            for f in building_level_layer.getFeatures():
                if f['percent_office_floorspace'] == 44:
                    bl1 = f
                elif f['percent_office_floorspace'] == 45:
                    bl2 = f

            self.assertEqual(len(project_area_attribute_changed_spy), 0)
            self.assertEqual(len(development_site_attribute_changed_spy), 0)
            self.assertEqual(len(building_level_attribute_changed_spy), 0)

            development_site_layer.startEditing()
            development_site_layer.changeAttributeValue(ds1_pk, 1, 11)
            self.assertEqual(len(project_area_attribute_changed_spy), 0)
            self.assertEqual(len(development_site_attribute_changed_spy), 1)
            self.assertEqual(len(building_level_attribute_changed_spy), 0)
            self.assertEqual(development_site_attribute_changed_spy[-1], [ds1_pk, 'name', 11])
            development_site_layer.changeAttributeValue(ds2_pk, 2, 12)
            self.assertEqual(len(project_area_attribute_changed_spy), 0)
            self.assertEqual(len(development_site_attribute_changed_spy), 2)
            self.assertEqual(len(building_level_attribute_changed_spy), 0)
            self.assertEqual(development_site_attribute_changed_spy[-1], [ds2_pk, 'project_area_pk', 12])

            project_area_layer.startEditing()
            project_area_layer.changeAttributeValue(f1_pk, 2, 14)
            self.assertEqual(len(project_area_attribute_changed_spy), 1)
            self.assertEqual(project_area_attribute_changed_spy[-1], [f1_pk, 'dwelling_size_1_bedroom', 14])
            self.assertEqual(len(development_site_attribute_changed_spy), 2)
            self.assertEqual(len(building_level_attribute_changed_spy), 0)
            project_area_layer.changeAttributeValue(f2_pk, 3, 15)
            self.assertEqual(len(project_area_attribute_changed_spy), 2)
            self.assertEqual(project_area_attribute_changed_spy[-1], [f2_pk, 'dwelling_size_2_bedroom', 15])
            self.assertEqual(len(development_site_attribute_changed_spy), 2)
            self.assertEqual(len(building_level_attribute_changed_spy), 0)

            building_level_layer.startEditing()
            building_level_layer.changeAttributeValue(bl1['fid'], 2, 24)
            self.assertEqual(len(project_area_attribute_changed_spy), 2)
            self.assertEqual(len(development_site_attribute_changed_spy), 2)
            self.assertEqual(len(building_level_attribute_changed_spy), 1)
            self.assertEqual(building_level_attribute_changed_spy[-1], [bl1['fid'], 'development_site_pk', 24])
            building_level_layer.changeAttributeValue(bl2['fid'], 3, 25)
            self.assertEqual(len(project_area_attribute_changed_spy), 2)
            self.assertEqual(len(development_site_attribute_changed_spy), 2)
            self.assertEqual(len(building_level_attribute_changed_spy), 2)
            self.assertEqual(building_level_attribute_changed_spy[-1], [bl2['fid'], 'level_height', 25])

            controller.cleanup()
            p.clear()
