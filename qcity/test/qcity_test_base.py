import unittest

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsRectangle,
    QgsVectorLayerUtils,
    QgsGeometry,
)
from qgis.PyQt.QtCore import QCoreApplication, QEvent, QVariant

from qcity.core.project import get_project_controller, reset_project_controller


class QCityTestBase(unittest.TestCase):
    """
    QCity Test base class
    """

    def setUp(self):
        _ = get_project_controller()

    def tearDown(self):
        QgsProject.instance().clear()
        reset_project_controller()

    def delete_qobject(self, obj):
        """
        Deletes a qobject immediately
        """
        obj.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    @staticmethod
    def init_numeric_fields(layer: QgsVectorLayer, feature: QgsFeature) -> None:
        int_types = (
            QVariant.Int,
            QVariant.LongLong,
            QVariant.UInt,
            QVariant.ULongLong,
            QVariant.Double,
        )
        for idx, field in enumerate(layer.fields()):
            if field.name() != "fid" and field.type() in int_types:
                feature[idx] = 0

    def create_project_area(
        self, project_area_layer: QgsVectorLayer, name: str, rect: QgsRectangle
    ) -> QgsFeature:
        f = QgsVectorLayerUtils.createFeature(project_area_layer)
        f.setGeometry(QgsGeometry.fromRect(rect))
        self.init_numeric_fields(project_area_layer, f)
        f["name"] = name
        f["dwelling_size_1_bedroom"] = 50.0
        f["dwelling_size_2_bedroom"] = 75.0
        f["dwelling_size_3_bedroom"] = 100.0
        f["dwelling_size_4_bedroom"] = 125.0
        self.assertTrue(project_area_layer.addFeature(f))

        for feat in project_area_layer.getFeatures():
            if feat["name"] == name:
                return feat
        self.fail(f"Project area '{name}' not found after commit")

    def create_development_site(
        self,
        development_site_layer: QgsVectorLayer,
        name: str,
        project_area_pk: int,
        rect: QgsRectangle,
        base_height: float = 0.0,
    ) -> QgsFeature:
        f = QgsVectorLayerUtils.createFeature(development_site_layer)
        self.init_numeric_fields(development_site_layer, f)
        f.setGeometry(QgsGeometry.fromRect(rect))
        f["project_area_pk"] = project_area_pk
        f["name"] = name
        f["base_height"] = base_height
        f["auto_calculate_floorspace"] = True
        self.assertTrue(development_site_layer.addFeature(f))

        for feat in development_site_layer.getFeatures():
            if feat["name"] == name:
                return feat
        self.fail(f"Development site '{name}' not found after commit")

    def create_building_level(
        self,
        building_level_layer: QgsVectorLayer,
        name: str,
        development_site_pk: int,
        geom: QgsGeometry,
        level_index: int = 1,
        level_height: float = 3.5,
    ) -> QgsFeature:
        building_level_layer.startEditing()
        f = QgsVectorLayerUtils.createFeature(building_level_layer)
        self.init_numeric_fields(building_level_layer, f)
        if not geom.isNull():
            f.setGeometry(geom)
        f["development_site_pk"] = development_site_pk
        f["name"] = name
        f["level_index"] = level_index
        f["level_height"] = level_height
        f["percent_commercial_floorspace"] = 100.0
        f["percent_office_floorspace"] = 0.0
        f["percent_residential_floorspace"] = 0.0
        self.assertTrue(building_level_layer.addFeature(f))

        for feat in building_level_layer.getFeatures():
            if feat["name"] == name:
                return feat
        self.fail(f"Building level '{name}' not found after commit")
