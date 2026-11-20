"""
Processing algorithm to reassign building levels to the development site
which they overlap the most.
"""

import typing

from qgis.core import (
    QgsProcessingContext,
    QgsExpression,
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
from qcity.core.utils import wrapped_edits

from .parameters import QCityProjectAreaParameterDefinition
from .qcity_algorithm import QCityAlgorithm
from qcity.gui import GuiUtils


class ReassignBuildingLevelsAlgorithm(QCityAlgorithm):
    """
    Reassigns building levels to the development site they overlap most
    """

    PROJECT_AREA = "PROJECT_AREA"
    ONLY_SELECTED = "ONLY_SELECTED"
    OUTPUT = "OUTPUT"

    OUTSIDE_TOLERANCE = 0.05

    def __init__(self):
        super().__init__()
        self.building_levels_source = None
        self.building_levels_crs = None
        self.building_level_count = None
        self.development_sites_source = None
        self.selected_level_fids = None
        self.project_area_pk = None
        self.project_area_name = None
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
        return (
            self.tr(
                "This QCity algorithm re-assigns building levels to the development sites that are positioned spatially below them."
            )
            + "\n\n"
            + self.tr(
                "This algorithm can be used together with the copy and move feature in QGIS to copy existing building levels from one QCity development site to another "
                "and re-assign the copied building levels to the new development site."
            )
            + "\n\n"
            + "<b>"
            + self.tr(
                "Initial state, with building levels contained within development site:"
            )
            + "</b>\n\n"
            + GuiUtils.get_svg_as_html("buildings_red.svg", height=140)
            + "\n\n<b>"
            + self.tr(
                "After using the 'Copy and Move' tool to copy the building levels to a new development site:"
            )
            + "</b>\n\n"
            + GuiUtils.get_svg_as_html("buildings_mixed.svg", height=140)
            + "\n\n<b>"
            + self.tr(
                "Running this algorithm changes the assigned development site for the new building levels to the new development site:"
            )
            + "</b>\n\n"
            + GuiUtils.get_svg_as_html("buildings_blue.svg", height=140)
        )

    def initAlgorithm(self, config=None) -> None:
        project_area_param = QCityProjectAreaParameterDefinition(
            self.PROJECT_AREA,
            self.tr("Only reassign to development sites in"),
            optional=True,
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

        self.project_area_name = parameters.get(self.PROJECT_AREA)
        if self.project_area_name:
            project_area_layer = controller.get_project_area_layer()
            if project_area_layer is None or not project_area_layer.isValid():
                raise QgsProcessingException(
                    self.tr("QCity project area layer is invalid")
                )

            name_field = DatabaseUtils.name_field_for_layer(LayerType.ProjectAreas)
            request = QgsFeatureRequest().setFilterExpression(
                QgsExpression.createFieldEqualityExpression(
                    name_field, self.project_area_name
                )
            )
            project_area_feature = next(project_area_layer.getFeatures(request), None)
            if project_area_feature is None or not project_area_feature.isValid():
                raise QgsProcessingException(
                    self.tr("Project area '{}' could not be found").format(
                        self.project_area_name
                    )
                )

            self.project_area_pk = project_area_feature[
                DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas)
            ]

        self.building_levels_source = QgsVectorLayerFeatureSource(building_levels_layer)
        self.building_levels_crs = building_levels_layer.crs()
        self.building_level_count = building_levels_layer.featureCount()

        self.development_sites_source = QgsVectorLayerFeatureSource(
            development_sites_layer
        )

        if self.parameterAsBool(parameters, self.ONLY_SELECTED, context):
            self.selected_level_fids = building_levels_layer.selectedFeatureIds()
            if len(self.selected_level_fids) == 0:
                raise QgsProcessingException(self.tr("No building levels are selected"))

        return True

    def processAlgorithm(
        self,
        parameters,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        dev_sites = {}
        dev_site_index = QgsSpatialIndex()

        request = QgsFeatureRequest()
        request.setDestinationCrs(self.building_levels_crs, context.transformContext())
        if self.project_area_pk is not None:
            request.setFilterExpression(
                QgsExpression.createFieldEqualityExpression(
                    DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites),
                    self.project_area_pk,
                )
            )

        for dev_site in self.development_sites_source.getFeatures(request):
            if not dev_site.hasGeometry() or dev_site.geometry().isEmpty():
                continue

            dev_sites[dev_site.id()] = dev_site
            dev_site_index.addFeature(dev_site)

        updates = {}

        building_request = QgsFeatureRequest()
        if self.selected_level_fids is not None:
            building_request.setFilterFids(self.selected_level_fids)
        for idx, building_level in enumerate(
            self.building_levels_source.getFeatures(building_request)
        ):
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
                if self.project_area_name:
                    feedback.pushWarning(
                        self.tr(
                            "Building level {} does not overlap any development "
                            "sites in {}, skipping".format(
                                building_level.id(), self.project_area_name
                            )
                        )
                    )
                else:
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

            updates[building_level.id()] = (
                current_development_site_key,
                best_development_site_key,
            )

        self.updates = updates
        return {}

    def postProcessAlgorithm(
        self, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        controller = get_project_controller()

        building_levels_layer = controller.get_building_levels_layer()
        if building_levels_layer is None or not building_levels_layer.isValid():
            raise QgsProcessingException(
                self.tr("QCity building levels layer is invalid")
            )

        if not self.updates:
            return {self.OUTPUT: building_levels_layer.id()}

        fk_field_name = DatabaseUtils.foreign_key_for_layer(LayerType.BuildingLevels)
        fk_field_idx = building_levels_layer.fields().lookupField(fk_field_name)
        if fk_field_idx < 0:
            raise QgsProcessingException(
                self.tr("Foreign key field '{}' not found").format(fk_field_name)
            )

        affected_site_pks = set()

        site_name_field = DatabaseUtils.name_field_for_layer(LayerType.DevelopmentSites)
        site_names = {}
        for pks in set(self.updates.values()):
            current_development_site_key, new_site_pk = pks
            site_feature = controller.get_feature_by_pk(
                LayerType.DevelopmentSites, new_site_pk
            )
            if site_feature is not None and site_feature.isValid():
                site_names[new_site_pk] = site_feature[site_name_field]
            else:
                site_names[new_site_pk] = str(new_site_pk)

        with wrapped_edits(building_levels_layer) as edits:
            for building_level_fid, pks in self.updates.items():
                current_development_site_key, new_site_pk = pks
                if not edits.changeAttributeValues(
                    building_level_fid,
                    {fk_field_idx: new_site_pk},
                    {fk_field_idx: current_development_site_key},
                ):
                    edits.error_occurred = True
                    raise QgsProcessingException(
                        self.tr("Failed to reassign building level {}").format(
                            building_level_fid
                        )
                    )
                affected_site_pks.add(current_development_site_key)
                affected_site_pks.add(new_site_pk)
                feedback.pushInfo(
                    self.tr("Reassigning building level {} to {}").format(
                        building_level_fid, site_names[new_site_pk]
                    )
                )

        for site_pk in affected_site_pks:
            site_feature = controller.get_feature_by_pk(
                LayerType.DevelopmentSites, site_pk
            )
            if site_feature is not None and site_feature.isValid():
                controller.auto_calculate_development_site_floorspace(site_feature.id())
                controller.update_floor_heights(site_feature.id())

        return {self.OUTPUT: building_levels_layer.id()}
