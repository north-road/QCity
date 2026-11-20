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
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterExtent,
    QgsProcessingOutputVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterField,
    QgsVectorLayerFeatureSource,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProcessing,
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeature,
    Qgis,
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


class ImportDevelopmentSitesAlgorithm(QCityAlgorithm):
    """
    Imports development sites from a vector layer
    """

    PROJECT_AREA = "PROJECT_AREA"
    INPUT = "INPUT"
    ONLY_WITHIN = "ONLY_WITHIN"
    CHECK_OVERLAPS = "CHECK_OVERLAPS"
    EXTENT = "EXTENT"
    CLIP_FEATURES = "CLIP_FEATURES"
    SITE_STATUS_FIELD = "SITE_STATUS_FIELD"
    NAME_FIELD = "NAME_FIELD"
    ADDRESS_FIELD = "ADDRESS_FIELD"
    SITE_OWNER_FIELD = "SITE_OWNER_FIELD"
    YEAR_FIELD = "YEAR_FIELD"
    OUTPUT = "OUTPUT"

    OUTSIDE_TOLERANCE = 0.05

    def __init__(self):
        super().__init__()

        self.project_area_source = None
        self.development_sites_crs = None
        self.development_sites_source = None
        self.project_area_crs = None
        self.features_to_add = None

    def name(self) -> str:
        return "importdevelopmentsites"

    def displayName(self) -> str:
        return self.tr("Import development sites")

    def shortDescription(self) -> str:
        return self.tr(
            "Creates development sites by importing features from a vector polygon layer."
        )

    def shortHelpString(self) -> str:
        return self.tr(
            "This QCity algorithm imports polygons from another layer into current QCity database development sites layer, and allows for setting attributes on import.\n\n"
            "The algorithm will import polygons with at least 95% of their area within the specified project area. Polygons that do not meet this criteria are disregarded.\n\n"
            "Duplicate polygons are deduplicated on import to avoid two development sites being located directly over each other."
        )

    def initAlgorithm(self, config=None) -> None:
        project_area_param = QCityProjectAreaParameterDefinition(
            self.PROJECT_AREA, self.tr("Target project area")
        )
        project_area_param.setHelp(
            self.tr("Development sites will be assigned to the selected project area.")
        )
        self.addParameter(project_area_param)

        input_param = QgsProcessingParameterFeatureSource(
            self.INPUT,
            self.tr("Source layer for development sites"),
            [QgsProcessing.SourceType.TypeVectorPolygon],
        )
        self.addParameter(input_param)

        only_within_param = QgsProcessingParameterBoolean(
            self.ONLY_WITHIN, self.tr("Only features wholely within project area")
        )
        only_within_param.setHelp(
            self.tr(
                "If checked, only features that fall completely within the project area will be imported"
            )
        )
        self.addParameter(only_within_param)

        check_overlaps_param = QgsProcessingParameterBoolean(
            self.CHECK_OVERLAPS,
            self.tr("Don't import features that overlap existing development sites"),
        )
        check_overlaps_param.setHelp(
            self.tr(
                "If checked, features which overlap existing development sites by more than 5% of their area will not be imported"
            )
        )
        self.addParameter(check_overlaps_param)

        extent_param = QgsProcessingParameterExtent(
            self.EXTENT, self.tr("Only import features within"), optional=True
        )
        extent_param.setHelp(self.tr("Optional extent for filtering imported features"))
        self.addParameter(extent_param)

        clip_features_param = QgsProcessingParameterBoolean(
            self.CLIP_FEATURES, self.tr("Clip imported features to extent")
        )
        clip_features_param.setHelp(
            self.tr(
                "If checked, imported features will be clipped to the specified extent"
            )
        )
        self.addParameter(clip_features_param)

        site_status_field_param = QgsProcessingParameterField(
            self.SITE_STATUS_FIELD,
            self.tr("Site status attribute"),
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.DataType.String,
            optional=True,
        )
        site_status_field_param.setHelp(
            self.tr("Attribute to import into the 'Site Status' field")
        )
        self.addParameter(site_status_field_param)

        name_field_param = QgsProcessingParameterField(
            self.NAME_FIELD,
            self.tr("Site name attribute"),
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.DataType.String,
            optional=True,
        )
        name_field_param.setHelp(
            self.tr("Attribute to import into the 'Site Name' field")
        )
        self.addParameter(name_field_param)

        site_address_field_param = QgsProcessingParameterField(
            self.ADDRESS_FIELD,
            self.tr("Site address attribute"),
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.DataType.String,
            optional=True,
        )
        site_address_field_param.setHelp(
            self.tr("Attribute to import into the 'Site Address' field")
        )
        self.addParameter(site_address_field_param)

        site_owner_field_param = QgsProcessingParameterField(
            self.SITE_OWNER_FIELD,
            self.tr("Site owner attribute"),
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.DataType.String,
            optional=True,
        )
        site_owner_field_param.setHelp(
            self.tr("Attribute to import into the 'Site Owner' field")
        )
        self.addParameter(site_owner_field_param)

        site_year_field_param = QgsProcessingParameterField(
            self.YEAR_FIELD,
            self.tr("Site year attribute"),
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.DataType.String,
            optional=True,
        )
        site_year_field_param.setHelp(
            self.tr("Attribute to import into the 'Site Year' field")
        )
        self.addParameter(site_year_field_param)

        self.addOutput(
            QgsProcessingOutputVectorLayer(self.OUTPUT, self.tr("Updated layer"))
        )

    def prepareAlgorithm(
        self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> bool:
        controller = get_project_controller()

        project_area_layer = controller.get_project_area_layer()
        if project_area_layer is None or not project_area_layer.isValid():
            raise QgsProcessingException(self.tr("QCity project area layer is invalid"))

        development_sites_layer = controller.get_development_sites_layer()
        if development_sites_layer is None or not development_sites_layer.isValid():
            raise QgsProcessingException(
                self.tr("QCity development sites layer is invalid")
            )

        project_area_name = self.parameterAsString(
            parameters, self.PROJECT_AREA, context
        )
        if not project_area_name:
            raise QgsProcessingException(self.tr("No target project area specified"))

        self.project_area_source = QgsVectorLayerFeatureSource(project_area_layer)

        self.development_sites_crs = development_sites_layer.crs()
        self.development_sites_source = QgsVectorLayerFeatureSource(
            development_sites_layer
        )

        self.project_area_crs = project_area_layer.crs()

        return True

    def processAlgorithm(
        self,
        parameters,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        input_source = self.parameterAsSource(parameters, self.INPUT, context)
        if input_source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        only_within = self.parameterAsBool(parameters, self.ONLY_WITHIN, context)
        check_overlaps = self.parameterAsBool(parameters, self.CHECK_OVERLAPS, context)
        extent = self.parameterAsExtent(
            parameters, self.EXTENT, context, self.development_sites_crs
        )
        clip_features = self.parameterAsBool(parameters, self.CLIP_FEATURES, context)
        site_status_field = self.parameterAsString(
            parameters, self.SITE_STATUS_FIELD, context
        )
        name_field = self.parameterAsString(parameters, self.NAME_FIELD, context)
        address_field = self.parameterAsString(parameters, self.ADDRESS_FIELD, context)
        site_owner_field = self.parameterAsString(
            parameters, self.SITE_OWNER_FIELD, context
        )
        year_field = self.parameterAsString(parameters, self.YEAR_FIELD, context)

        project_area_name = self.parameterAsString(
            parameters, self.PROJECT_AREA, context
        )

        name_field = DatabaseUtils.name_field_for_layer(LayerType.ProjectAreas)
        request = QgsFeatureRequest().setFilterExpression(
            QgsExpression.createFieldEqualityExpression(name_field, project_area_name)
        )
        project_area_feature = next(self.project_area_source.getFeatures(request), None)
        if project_area_feature is None or not project_area_feature.isValid():
            raise QgsProcessingException(
                self.tr("Project area '{}' could not be found").format(
                    project_area_name
                )
            )

        if (
            not project_area_feature.hasGeometry()
            or project_area_feature.geometry().isEmpty()
        ):
            raise QgsProcessingException(
                self.tr("Target project area '{}' has no geometry").format(
                    project_area_name
                )
            )

        project_area_pk = project_area_feature[
            DatabaseUtils.primary_key_for_layer(LayerType.ProjectAreas)
        ]
        project_area_geom = QgsGeometry(project_area_feature.geometry())
        if self.project_area_crs != self.development_sites_crs:
            transform = QgsCoordinateTransform(
                self.project_area_crs,
                self.development_sites_crs,
                context.transformContext(),
            )
            try:
                project_area_geom.transform(transform)
            except QgsCsException:
                raise QgsProcessingException(
                    self.tr("Could not transform project area to development site CRS")
                )

        # index existing development sites for duplicate/overlap checks
        existing_request = QgsFeatureRequest().setDestinationCrs(
            self.development_sites_crs, context.transformContext()
        )

        existing_index = QgsSpatialIndex(
            QgsSpatialIndex.Flag.FlagStoreFeatureGeometries
        )
        next_index_id = 1
        for f in self.development_sites_source.getFeatures(existing_request):
            index_feat = QgsFeature(next_index_id)
            index_feat.setGeometry(f.geometry())
            existing_index.addFeature(index_feat)
            next_index_id += 1

        project_area_engine = QgsGeometry.createGeometryEngine(
            project_area_geom.constGet()
        )
        project_area_engine.prepareGeometry()

        extent_geom = QgsGeometry.fromRect(extent) if not extent.isNull() else None

        input_request = QgsFeatureRequest().setDestinationCrs(
            self.development_sites_crs, context.transformContext()
        )
        total_features = input_source.featureCount()
        fk_field_name = DatabaseUtils.foreign_key_for_layer(LayerType.DevelopmentSites)

        features_to_add = []
        for idx, feat in enumerate(input_source.getFeatures(input_request)):
            if feedback.isCanceled():
                return {}
            if total_features > 0:
                feedback.setProgress(100 * idx / total_features)

            if not feat.hasGeometry() or feat.geometry().isEmpty():
                feedback.pushInfo(
                    self.tr("Feature {} has no geometry, skipping").format(feat.id())
                )
                continue

            geom = QgsGeometry(feat.geometry())

            # filter / clip against optional extent
            if extent_geom is not None:
                if not geom.intersects(extent_geom):
                    continue
                if clip_features:
                    geom = geom.intersection(extent_geom)
                    if geom.type() != Qgis.GeometryType.Polygon:
                        geom = geom.convertToType(Qgis.GeometryType.Polygon, True)
                    if geom.isEmpty():
                        feedback.pushInfo(
                            self.tr(
                                "Feature {} has no remaining geometry after clipping to target extent, skipping"
                            ).format(feat.id())
                        )
                        continue
            geom_area = geom.area()

            if only_within:
                if not project_area_engine.contains(geom.constGet()):
                    feedback.pushInfo(
                        self.tr(
                            "Feature {} is not wholly within the project area, skipping"
                        ).format(feat.id())
                    )
                    continue
            else:
                if not project_area_engine.intersects(geom.constGet()):
                    feedback.pushInfo(
                        self.tr(
                            "Feature {} does not intersect the project area, skipping"
                        ).format(feat.id())
                    )
                    continue

                intersection = geom.intersection(project_area_geom)
                overlap_percent = intersection.area() / geom_area
                if overlap_percent < (1 - self.OUTSIDE_TOLERANCE):
                    feedback.pushWarning(
                        self.tr(
                            "Feature {} overlaps project area by only {}%, more than {}% lies outside the project area, skipping"
                        ).format(
                            feat.id(),
                            round(overlap_percent * 100, 1),
                            self.OUTSIDE_TOLERANCE * 100,
                        )
                    )
                    continue

            # deduplicate identical polygons
            candidate_ids = existing_index.intersects(geom.boundingBox())
            geom_engine = QgsGeometry.createGeometryEngine(geom.constGet())
            geom_engine.prepareGeometry()

            skip_feature = False
            for candidate_id in candidate_ids:
                other_geom = existing_index.geometry(candidate_id)
                if geom.equals(other_geom):
                    feedback.pushInfo(
                        self.tr(
                            "Feature {} is a duplicate of an existing development site, skipping"
                        ).format(feat.id())
                    )
                    skip_feature = True
                    break

                if check_overlaps and geom_engine.intersects(other_geom.constGet()):
                    overlap_area = geom.intersection(other_geom).area()
                    if (overlap_area / geom_area) > self.OUTSIDE_TOLERANCE:
                        feedback.pushWarning(
                            self.tr(
                                "Feature {} overlaps an existing development site by {}%, skipping"
                            ).format(
                                feat.id(),
                                round((overlap_area / geom_area) * 100, 1),
                            )
                        )
                        skip_feature = True
                        break

            if skip_feature:
                continue

            # create output feature
            site_name = ""
            if name_field:
                raw_name = feat[name_field]
                if raw_name:
                    site_name = str(raw_name)
            if not site_name:
                site_name = self.tr("Site {}").format(len(features_to_add) + 1)

            initial_attributes = {
                fk_field_name: project_area_pk,
            }

            if site_status_field:
                val = feat[site_status_field]
                if val:
                    initial_attributes["site_status"] = str(val)

            if address_field:
                val = feat[address_field]
                if val:
                    initial_attributes["address"] = str(val)

            if site_owner_field:
                val = feat[site_owner_field]
                if val:
                    initial_attributes["site_owner"] = str(val)

            if year_field:
                val = feat[year_field]
                if val not in (None, ""):
                    try:
                        initial_attributes["year"] = int(val)
                    except (TypeError, ValueError):
                        feedback.pushWarning(
                            self.tr(
                                "Could not convert year value '{}' on feature {} to integer"
                            ).format(val, feat.id())
                        )

            features_to_add.append((site_name, geom, initial_attributes))

            # add to index, so we catch this feature when doing further de-duplication tests
            index_feat = QgsFeature(next_index_id)
            index_feat.setGeometry(geom)
            existing_index.addFeature(index_feat)
            next_index_id += 1

        self.features_to_add = features_to_add
        return {}

    def postProcessAlgorithm(
        self, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        controller = get_project_controller()
        development_sites_layer = controller.get_development_sites_layer()
        if development_sites_layer is None or not development_sites_layer.isValid():
            raise QgsProcessingException(
                self.tr("QCity development sites layer is invalid")
            )

        if not self.features_to_add:
            feedback.pushInfo(self.tr("No development sites were imported"))
            return {self.OUTPUT: development_sites_layer.id()}

        valid_fields = {field.name() for field in development_sites_layer.fields()}
        with wrapped_edits(development_sites_layer) as edits:
            for site_name, geom, initial_attributes in self.features_to_add:
                filtered_attributes = {
                    k: v for k, v in initial_attributes.items() if k in valid_fields
                }
                new_feature = controller.create_feature(
                    LayerType.DevelopmentSites,
                    site_name,
                    geom,
                    initial_attributes=filtered_attributes,
                )
                if not edits.addFeature(new_feature):
                    edits.error_occurred = True
                    raise QgsProcessingException(
                        self.tr("Failed to import development site '{}'").format(
                            site_name
                        )
                    )

        feedback.pushInfo(
            self.tr("Imported {} development site(s)").format(len(self.features_to_add))
        )
        return {self.OUTPUT: development_sites_layer.id()}
