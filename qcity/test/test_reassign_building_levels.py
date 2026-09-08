"""
Tests for the ReassignBuildingLevelsAlgorithm processing algorithm
"""

import unittest

from qgis.core import (
    NULL,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProject,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QVariant

from qcity.processing.reassign_building_levels_algorithm import (
    ReassignBuildingLevelsAlgorithm,
)
from qcity.test.utilities import get_qgis_app

TEST_CRS = "EPSG:4326"


def _rect_geom(x_min, y_min, x_max, y_max):
    return QgsGeometry.fromWkt(
        "Polygon (({} {}, {} {}, {} {}, {} {}, {} {}))".format(
            x_min, y_min, x_max, y_min, x_max, y_max, x_min, y_max, x_min, y_min
        )
    )


def _make_polygon_layer(fields, name):
    layer = QgsVectorLayer("Polygon?crs={}".format(TEST_CRS), name, "memory")
    assert layer.isValid(), "Failed to create memory layer"
    layer.dataProvider().addAttributes(fields)
    layer.updateFields()
    QgsProject.instance().addMapLayer(layer)
    return layer


def _run_algorithm(bl_layer, ds_layer, only_selected=False):
    alg = ReassignBuildingLevelsAlgorithm()
    alg.initAlgorithm()
    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()
    params = {
        ReassignBuildingLevelsAlgorithm.INPUT: bl_layer,
        ReassignBuildingLevelsAlgorithm.DEVELOPMENT_SITES: ds_layer,
        ReassignBuildingLevelsAlgorithm.ONLY_SELECTED: only_selected,
    }
    results = alg.processAlgorithm(params, context, feedback)
    return alg, context, feedback, results


class TestReassignBuildingLevels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run before all tests"""
        get_qgis_app()

    def setUp(self):
        self.project = QgsProject.instance()
        self.project.clear()

    def tearDown(self):
        self.project.clear()

    def _make_ds_layer(self):
        """
        Two development sites:
        site A: (0,0)-(10,10), fid 1
        site B: (20,0)-(30,10), fid 2
        """
        fields = [
            QgsField("fid", QVariant.Int),
            QgsField("name", QVariant.String),
        ]
        layer = _make_polygon_layer(fields, "ds_layer")

        features = []
        for fid, name, geom in (
            (1, "A", _rect_geom(0, 0, 10, 10)),
            (2, "B", _rect_geom(20, 0, 30, 10)),
        ):
            f = QgsFeature(layer.fields())
            f.setGeometry(geom)
            f.setAttribute("fid", fid)
            f.setAttribute("name", name)
            features.append(f)

        layer.dataProvider().addFeatures(features)
        layer.updateExtents()
        return layer

    def _make_bl_layer(self):
        """
        Building levels with geometries and a development_site_pk attribute.
        Uses fid of the development sites as pk value (like QCity does).
        """
        fields = [
            QgsField("name", QVariant.String),
            QgsField("development_site_pk", QVariant.Int),
        ]
        layer = _make_polygon_layer(fields, "bl_layer")

        features = []
        # (name, geom, current fk)
        specs = [
            ("inside_a", _rect_geom(1, 1, 4, 4), None),
            ("spanning_ab", _rect_geom(8, 0, 22, 10), None),
            ("outside_all", _rect_geom(50, 50, 55, 55), None),
            ("inside_b", _rect_geom(21, 1, 24, 4), None),
            ("wrong_fk", _rect_geom(5, 5, 7, 7), 999),
        ]
        for name, geom, fk in specs:
            f = QgsFeature(layer.fields())
            f.setGeometry(geom)
            f.setAttribute("name", name)
            f.setAttribute("development_site_pk", fk)
            features.append(f)

        layer.dataProvider().addFeatures(features)
        layer.updateExtents()
        return layer

    def _ds_pk_by_name(self, ds_layer):
        return {f["name"]: f["fid"] for f in ds_layer.getFeatures()}

    def _bl_fk_by_name(self, bl_layer):
        return {
            f["name"]: f["development_site_pk"] for f in bl_layer.getFeatures()
        }

    def test_reassigns_to_most_overlapping_site(self):
        ds_layer = self._make_ds_layer()
        bl_layer = self._make_bl_layer()

        _run_algorithm(bl_layer, ds_layer)

        ds_pks = self._ds_pk_by_name(ds_layer)
        fks = self._bl_fk_by_name(bl_layer)

        # fully inside A -> A
        self.assertEqual(fks["inside_a"], ds_pks["A"])
        # spans both, larger overlap with A -> A
        self.assertEqual(fks["spanning_ab"], ds_pks["A"])
        # inside B -> B
        self.assertEqual(fks["inside_b"], ds_pks["B"])
        # wrong fk corrected to A
        self.assertEqual(fks["wrong_fk"], ds_pks["A"])

    def test_skips_features_without_overlap(self):
        ds_layer = self._make_ds_layer()
        bl_layer = self._make_bl_layer()

        _run_algorithm(bl_layer, ds_layer)

        fks = self._bl_fk_by_name(bl_layer)
        # fully outside all development sites -> untouched (NULL, not a pk)
        self.assertTrue(fks["outside_all"] == NULL)

    def test_only_selected_features(self):
        ds_layer = self._make_ds_layer()
        bl_layer = self._make_bl_layer()

        # select only "inside_b"
        for f in bl_layer.getFeatures():
            if f["name"] == "inside_b":
                bl_layer.selectByIds([f.id()])
                break

        _run_algorithm(bl_layer, ds_layer, only_selected=True)

        ds_pks = self._ds_pk_by_name(ds_layer)
        fks = self._bl_fk_by_name(bl_layer)

        self.assertEqual(fks["inside_b"], ds_pks["B"])
        # other features untouched
        self.assertTrue(fks["inside_a"] == NULL)

    def test_warns_when_building_level_largely_outside(self):
        ds_layer = self._make_ds_layer()
        bl_layer = self._make_bl_layer()

        # a building level which is only half inside site A
        f = QgsFeature(bl_layer.fields())
        f.setGeometry(_rect_geom(5, 0, 15, 4))  # half in A (0-10), half out
        f.setAttribute("name", "half_out")
        f.setAttribute("development_site_pk", None)
        bl_layer.dataProvider().addFeatures([f])

        _, _, feedback, _ = _run_algorithm(bl_layer, ds_layer)

        # warning text collected
        self.assertGreater(len(feedback.textLog()), 0)


if __name__ == "__main__":
    unittest.main()
