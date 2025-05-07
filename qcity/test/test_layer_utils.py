import unittest
import os
import tempfile

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsVectorLayerUtils
)

from qcity.core.project import PROJECT_CONTROLLER

from qcity.core.database import DatabaseUtils
from qcity.core import LayerType
from qcity.core.layer import LayerUtils

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestLayerUtils(unittest.TestCase):

    def test_change_attributes(self) -> None:
        """
        Test changing attributes in a layer
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject.instance()
            PROJECT_CONTROLLER.add_database_layers_to_project(p, gpkg_path)

            project_area_layer = PROJECT_CONTROLLER.get_project_area_layer()
            # create an initial feature
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 1
            f['car_parking_2_bedroom'] = 2
            f['car_parking_3_bedroom'] = 3
            f['car_parking_4_bedroom'] = 4
            project_area_layer.startEditing()
            self.assertTrue(project_area_layer.addFeature(f))
            self.assertTrue(project_area_layer.commitChanges())

            f = next(project_area_layer.getFeatures())
            f_id = f.id()

            self.assertTrue(
                LayerUtils.store_value(LayerType.ProjectAreas, f_id, 'car_parking_3_bedroom', 33)
            )

            f_3 = project_area_layer.getFeature(f_id)
            self.assertEqual(f_3['car_parking_3_bedroom'], 33)
