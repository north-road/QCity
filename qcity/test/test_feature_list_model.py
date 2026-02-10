"""
GUI Utils Test.
"""

from typing import Optional
import unittest
from qgis.core import (
    QgsFeature,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsRectangle,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsProject,
)
from qgis.PyQt.QtCore import QVariant, Qt
from qcity.gui.feature_list_model import FeatureListModel, FeatureFilterProxyModel
from qcity.test.utilities import get_qgis_app
from qcity.core import DatabaseUtils, LayerType

from qcity.test.qcity_test_base import QCityTestBase

QGIS_APP = get_qgis_app()


class FeatureListModelTest(QCityTestBase):
    """Test FeatureListModel works."""

    def setUp(self):
        """
        Set up the model and dependencies before each test.
        """
        self.layer_type = LayerType.ProjectAreas
        self.model = FeatureListModel(self.layer_type)
        self.name_field = DatabaseUtils.name_field_for_layer(self.layer_type)

    def tearDown(self):
        self.model.deleteLater()

    def create_real_feature(
        self, fid: int, name_value: str, geom_wkt: Optional[str] = None
    ) -> QgsFeature:
        """
        Helper to create a QgsFeature with a specific ID and Name.
        """
        fields = QgsFields()
        fields.append(QgsField(self.name_field, QVariant.String))
        feature = QgsFeature(fields)
        feature.setId(fid)
        feature.setAttribute(self.name_field, name_value)
        if geom_wkt:
            feature.setGeometry(QgsGeometry.fromWkt(geom_wkt))
        return feature

    def test_initial_state(self):
        self.assertEqual(self.model.rowCount(), 0)
        self.assertEqual(len(self.model.items), 0)

    def test_add_feature(self):
        f1 = self.create_real_feature(1, "Feature A", "Point(1 2)")
        self.model.add_feature(f1)

        self.assertEqual(self.model.rowCount(), 1)

        index = self.model.index(0, 0)
        self.assertEqual(
            self.model.data(index, Qt.ItemDataRole.DisplayRole), "Feature A"
        )
        self.assertEqual(self.model.data(index, FeatureListModel.FEATURE_ID_ROLE), 1)
        self.assertEqual(
            self.model.data(index, FeatureListModel.FEATURE_GEOMETRY_ROLE).asWkt(),
            "Point (1 2)",
        )

        f2 = self.create_real_feature(22, "Feature B", "Point(3 4)")
        self.model.add_feature(f2)

        self.assertEqual(self.model.rowCount(), 2)

        index = self.model.index(1, 0)
        self.assertEqual(
            self.model.data(index, Qt.ItemDataRole.DisplayRole), "Feature B"
        )
        self.assertEqual(self.model.data(index, FeatureListModel.FEATURE_ID_ROLE), 22)
        self.assertEqual(
            self.model.data(index, FeatureListModel.FEATURE_GEOMETRY_ROLE).asWkt(),
            "Point (3 4)",
        )

    def test_insert_feature(self):
        f1 = self.create_real_feature(1, "A")
        f2 = self.create_real_feature(2, "B")
        f3 = self.create_real_feature(3, "C")

        self.model.add_feature(f1)
        self.model.add_feature(f3)

        # Insert B in the middle
        self.model.insert_feature(1, f2)

        index = self.model.index(0, 0)
        self.assertEqual(self.model.data(index, FeatureListModel.FEATURE_ID_ROLE), 1)
        index = self.model.index(1, 0)
        self.assertEqual(self.model.data(index, FeatureListModel.FEATURE_ID_ROLE), 2)
        index = self.model.index(2, 0)
        self.assertEqual(self.model.data(index, FeatureListModel.FEATURE_ID_ROLE), 3)

    def test_rename(self):
        """
        Test renaming a feature
        """
        f1 = self.create_real_feature(1, "Old Name")
        self.model.add_feature(f1)

        index = self.model.index(0, 0)
        self.model.rename(index, "New Name")

        self.assertEqual(
            self.model.data(index, Qt.ItemDataRole.DisplayRole), "New Name"
        )

    def test_remove_feature_by_id(self):
        f1 = self.create_real_feature(10, "A")
        f2 = self.create_real_feature(20, "B")

        self.model.add_feature(f1)
        self.model.add_feature(f2)

        self.model.remove_feature_by_id(10)

        self.assertEqual(self.model.rowCount(), 1)
        self.assertEqual(self.model.items[0].id(), 20)

    def test_move_row_up(self):
        f1 = self.create_real_feature(1, "A")
        f2 = self.create_real_feature(2, "B")
        self.model.add_feature(f1)
        self.model.add_feature(f2)

        # Move "B" (row 1) UP to row 0
        index_of_b = self.model.index(1, 0)
        self.model.move_row(index_of_b, up=True)

        self.assertEqual(self.model.items[0].id(), 2)  # B
        self.assertEqual(self.model.items[1].id(), 1)  # A

    def test_move_row_down(self):
        f1 = self.create_real_feature(1, "A")
        f2 = self.create_real_feature(2, "B")
        self.model.add_feature(f1)
        self.model.add_feature(f2)

        # Move "A" (row 0) DOWN to row 1
        index_of_a = self.model.index(0, 0)
        self.model.move_row(index_of_a, up=False)

        self.assertEqual(self.model.items[0].id(), 2)  # B
        self.assertEqual(self.model.items[1].id(), 1)  # A

    def test_index_for_feature(self):
        f0 = self.create_real_feature(50, "Not Me")
        self.model.add_feature(f0)

        f1 = self.create_real_feature(55, "Find Me")
        self.model.add_feature(f1)

        index = self.model.index_for_feature_id(55)
        self.assertTrue(index.isValid())
        self.assertEqual(index.row(), 1)

        index_obj = self.model.index_for_feature(f1)
        self.assertTrue(index_obj.isValid())
        self.assertEqual(index_obj.row(), 1)

    def test_proxy_model(self):
        proxy_model = FeatureFilterProxyModel()
        proxy_model.setSourceModel(self.model)

        f1 = self.create_real_feature(1, "Pineapple", "Point(1 3)")
        f2 = self.create_real_feature(2, "Banana", "Point(11 3)")
        f3 = self.create_real_feature(3, "Apple", "Point(1 5)")

        self.model.add_feature(f1)
        self.model.add_feature(f2)
        self.model.add_feature(f3)

        self.assertEqual(proxy_model.rowCount(), 3)
        proxy_model.set_search_string("nea")
        self.assertEqual(proxy_model.rowCount(), 1)
        self.assertEqual(proxy_model.data(proxy_model.index(0, 0)), "Pineapple")
        proxy_model.set_search_string("INE")
        self.assertEqual(proxy_model.rowCount(), 1)
        self.assertEqual(proxy_model.data(proxy_model.index(0, 0)), "Pineapple")
        proxy_model.set_search_string("app")
        self.assertEqual(proxy_model.rowCount(), 2)
        self.assertEqual(proxy_model.data(proxy_model.index(0, 0)), "Pineapple")
        self.assertEqual(proxy_model.data(proxy_model.index(1, 0)), "Apple")

        proxy_model.set_search_string(None)
        self.assertEqual(proxy_model.rowCount(), 3)

        proxy_model.set_search_bounds(QgsRectangle(0, 0, 3, 6))
        self.assertEqual(proxy_model.rowCount(), 2)
        self.assertEqual(proxy_model.data(proxy_model.index(0, 0)), "Pineapple")
        self.assertEqual(proxy_model.data(proxy_model.index(1, 0)), "Apple")

        proxy_model.set_search_bounds(QgsRectangle(10, 0, 13, 6))
        self.assertEqual(proxy_model.rowCount(), 1)
        self.assertEqual(proxy_model.data(proxy_model.index(0, 0)), "Banana")

        proxy_model.set_search_bounds(
            QgsRectangle(860322, -16729, 1700027, 685870),
            QgsCoordinateTransform(
                QgsCoordinateReferenceSystem("EPSG:4326"),
                QgsCoordinateReferenceSystem("EPSG:3857"),
                QgsProject.instance(),
            ),
        )
        self.assertEqual(proxy_model.rowCount(), 1)
        self.assertEqual(proxy_model.data(proxy_model.index(0, 0)), "Banana")

        proxy_model.set_search_bounds(None)
        self.assertEqual(proxy_model.rowCount(), 3)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(FeatureListModelTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
