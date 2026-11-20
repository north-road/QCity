"""
Processing algorithm to reassign building levels to the development site
which they overlap the most.
"""

import typing

from qgis.core import (
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputVectorLayer,
    QgsProcessingParameterBoolean,
    QgsVectorLayerFeatureSource,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsGeometry,
)

from qcity.core import (
    DatabaseUtils,
    LayerType,
)
from qcity.core import (
    get_project_controller,
)
from .parameters import QCityProjectAreaParameterDefinition
from .qcity_algorithm import QCityAlgorithm


class ReassignBuildingLevelsAlgorithm(QCityAlgorithm):
    """
    Reassigns building levels to the development site they overlap most
    """

    INPUT = "INPUT"
    ONLY_SELECTED = "ONLY_SELECTED"
    OUTPUT = "OUTPUT"

    OUTSIDE_TOLERANCE = 0.05

    def __init__(self):
        super().__init__()
        self.building_levels_source = None
        self.building_levels_crs = None
        self.building_level_count = None
        self.development_sites_source = None
        self.updates = None

    def name(self) -> str:
        return "reassignbuildinglevels"

    def displayName(self) -> str:
        return self.tr("Reassign building levels")

    def shortDescription(self) -> str:
        return self.tr(
            "Reassigns building levels to the development sites that are positioned below them."
        )

    def shortHelpString(self) -> str:
        return self.tr("")

    def initAlgorithm(self, config=None) -> None:
        project_area_param = QCityProjectAreaParameterDefinition(
            self.INPUT, self.tr("Only reassign to development sites in"), optional=True
        )
        project_area_param.setHelp(
            self.tr(
                "If set, building levels will only be assigned to development sites that are within the selected project area."
            )
        )

        self.addParameter(project_area_param)

        selected_only_param = QgsProcessingParameterBoolean(
            self.ONLY_SELECTED,
            self.tr("Only reassign selected building levels"),
            defaultValue=False,
        )
        selected_only_param.setHelp(
            self.tr("If checked, only the selected building levels will be reassigned.")
        )
        self.addParameter(selected_only_param)
        self.addOutput(
            QgsProcessingOutputVectorLayer(self.OUTPUT, self.tr("Updated layer"))
        )

    def prepareAlgorithm(
        self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> bool:
        controller = get_project_controller()
        building_levels_layer = controller.get_building_levels_layer()
        if building_levels_layer is None or not building_levels_layer.isValid():
            raise QgsProcessingException(
                self.tr("QCity building levels layer is invalid")
            )
        development_sites_layer = controller.get_development_sites_layer()
        if development_sites_layer is None or not development_sites_layer.isValid():
            raise QgsProcessingException(
                self.tr("QCity development sites layer is invalid")
            )

        self.building_levels_source = QgsVectorLayerFeatureSource(building_levels_layer)
        self.building_levels_crs = building_levels_layer.crs()
        self.building_level_count = building_levels_layer.featureCount()

        self.development_sites_source = QgsVectorLayerFeatureSource(
            development_sites_layer
        )

        return True

    def processAlgorithm(
        self,
        parameters,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        controller = get_project_controller()

        dev_sites = {}
        dev_site_index = QgsSpatialIndex()

        request = QgsFeatureRequest()
        request.setDestinationCrs(self.building_levels_crs, context.transformContext())

        for dev_site in self.development_sites_source.getFeatures(request):
            if not dev_site.hasGeometry() or dev_site.geometry().isEmpty():
                continue

            dev_sites[dev_site.id()] = dev_site
            dev_site_index.addFeature(dev_site)

        updates = {}
        for idx, building_level in enumerate(self.building_levels_source.getFeatures()):
            if feedback.isCanceled():
                break
            feedback.setProgress(100 * idx / self.building_level_count)

            if not building_level.hasGeometry() or building_level.geometry().isEmpty():
                feedback.pushInfo(
                    self.tr("Building level {} has no geometry, skipping").format(
                        building_level.id()
                    )
                )
                continue

            building_level_geom = building_level.geometry()
            candidate_ids = dev_site_index.intersects(building_level_geom.boundingBox())

            dev_site_engine = QgsGeometry.createGeometryEngine(
                building_level_geom.constGet()
            )
            dev_site_engine.prepareGeometry()
            original_area = building_level_geom.area()

            best_site = None
            best_overlap_area = 0
            for site_id in candidate_ids:
                site_feature = dev_sites[site_id]
                site_geometry = site_feature.geometry()
                if not dev_site_engine.intersects(site_geometry.constGet()):
                    continue

                intersection = building_level_geom.intersection(site_geometry)
                overlap_area = intersection.area()
                if overlap_area > best_overlap_area:
                    best_overlap_area = overlap_area
                    best_site = site_feature

            if best_site is None or best_overlap_area <= 0:
                feedback.pushWarning(
                    self.tr(
                        "Building level {} does not overlap any development "
                        "sites, skipping".format(building_level.id())
                    )
                )
                continue

            current_development_site_key = building_level[
                DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels)
            ]

            best_development_site_key = best_site[
                DatabaseUtils.primary_key_for_layer(LayerType.DevelopmentSites)
            ]

            if current_development_site_key == best_development_site_key:
                continue

            overlap_percent = best_overlap_area / original_area
            if overlap_percent < (1 - self.OUTSIDE_TOLERANCE):
                feedback.pushWarning(
                    self.tr(
                        "Building level {} overlaps development site by only "
                        "{}%, more than {}% of the building level area lies "
                        "outside the development site".format(
                            building_level.id(),
                            round(overlap_percent * 100, 1),
                            self.OUTSIDE_TOLERANCE * 100,
                        )
                    )
                )
                continue

            updates[building_level.id()] = best_development_site_key

        self.updates = updates
        return {}

    def postProcessAlgorithm(
        self, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        print(self.updates)
        return {}
