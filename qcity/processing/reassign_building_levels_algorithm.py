"""
Processing algorithm to reassign building levels to the development site
which they overlap the most.

Useful after copying or moving building level polygons between development
sites with standard QGIS editing tools - this algorithm updates the
development site association for the moved features.
"""

from qgis.core import (
    QgsCoordinateTransform,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterVectorLayer,
    QgsSpatialIndex,
)

from qcity.core import (
    DatabaseUtils,
    LayerType,
)
from qcity.core.utils import wrapped_edits


class ReassignBuildingLevelsAlgorithm(QgsProcessingAlgorithm):
    """
    Reassigns building levels to the development site they overlap most
    """

    INPUT = "INPUT"
    DEVELOPMENT_SITES = "DEVELOPMENT_SITES"
    ONLY_SELECTED = "ONLY_SELECTED"
    OUTPUT = "OUTPUT"

    # proportion of a building level area allowed to fall outside the
    # reassigned development site before a warning is raised, matching the
    # warning used when digitizing building levels
    OUTSIDE_TOLERANCE = 0.05

    def tr(self, string: str) -> str:
        return self.__class__.__name__ + string

    def createInstance(self):
        return ReassignBuildingLevelsAlgorithm()

    def name(self) -> str:
        return "reassignbuildinglevelstodevelopmentsites"

    def displayName(self) -> str:
        return self.tr("Reassign building levels to development sites")

    def shortHelpString(self) -> str:
        return self.tr(
            "Updates the development site association of building levels based on "
            "which development site their geometry overlaps the most. Intended for "
            "use after copying or moving building levels between development sites "
            "with QGIS editing tools."
        )

    def initAlgorithm(self, config=None) -> None:
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr("Building levels layer"),
                [QgsProcessing.TypeVectorPolygon],
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.DEVELOPMENT_SITES,
                self.tr("Development sites layer"),
                [QgsProcessing.TypeVectorPolygon],
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ONLY_SELECTED,
                self.tr("Only reassign selected building levels"),
                defaultValue=False,
            )
        )
        self.addOutput(
            QgsProcessingOutputVectorLayer(self.OUTPUT, self.tr("Updated layer"))
        )

    def processAlgorithm(
        self,
        parameters,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        building_level_layer = self.parameterAsVectorLayer(
            parameters, self.INPUT, context
        )
        if building_level_layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        development_site_layer = self.parameterAsVectorLayer(
            parameters, self.DEVELOPMENT_SITES, context
        )
        if development_site_layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.DEVELOPMENT_SITES)
            )

        only_selected = self.parameterAsBoolean(parameters, self.ONLY_SELECTED, context)

        development_site_pk_field = DatabaseUtils.primary_key_for_layer(
            LayerType.DevelopmentSites
        )
        building_level_fk_field = DatabaseUtils.foreign_key_for_layer(
            LayerType.BuildingLevels
        )

        if building_level_layer.fields().lookupField(building_level_fk_field) < 0:
            raise QgsProcessingException(
                self.tr(
                    "Building levels layer is missing the {} field".format(
                        building_level_fk_field
                    )
                )
            )
        if development_site_layer.fields().lookupField(development_site_pk_field) < 0:
            raise QgsProcessingException(
                self.tr(
                    "Development sites layer is missing the {} field".format(
                        development_site_pk_field
                    )
                )
            )

        development_site_pk_idx = development_site_layer.fields().lookupField(
            development_site_pk_field
        )

        # transform between the two layer CRS when they differ
        transform = None
        if (
            building_level_layer.crs() != development_site_layer.crs()
            and building_level_layer.crs().isValid()
            and development_site_layer.crs().isValid()
        ):
            transform = QgsCoordinateTransform(
                building_level_layer.crs(),
                development_site_layer.crs(),
                context.transformContext(),
            )

        # spatial index of development sites for fast overlap lookup
        spatial_index = QgsSpatialIndex(development_site_layer.getFeatures())

        development_site_features = {
            f.id(): f for f in development_site_layer.getFeatures()
        }

        if only_selected:
            features = building_level_layer.selectedFeatures()
            feature_count = building_level_layer.selectedFeatureCount()
        else:
            features = building_level_layer.getFeatures()
            feature_count = building_level_layer.featureCount()

        feedback.pushInfo(
            self.tr("Checking {} building levels...").format(feature_count)
        )

        total_count = 0
        reassigned_count = 0
        warning_count = 0
        updates = {}

        for feature in features:
            if feedback.isCanceled():
                break
            total_count += 1

            geometry = feature.geometry()
            if geometry is None or geometry.isEmpty():
                continue

            original_area = geometry.area()
            if original_area <= 0:
                continue

            if transform is not None:
                geometry.transform(transform)

            # find candidate development sites overlapping the bounding box
            candidate_ids = spatial_index.intersects(geometry.boundingBox())

            best_site_id = None
            best_overlap_area = 0
            for site_id in candidate_ids:
                site_feature = development_site_features[site_id]
                site_geometry = site_feature.geometry()
                if site_geometry is None:
                    continue
                intersection = geometry.intersection(site_geometry)
                overlap_area = intersection.area()
                if overlap_area > best_overlap_area:
                    best_overlap_area = overlap_area
                    best_site_id = site_id

            if best_site_id is None or best_overlap_area <= 0:
                feedback.pushWarning(
                    self.tr(
                        "Building level {} does not overlap any development "
                        "site, skipping".format(feature.id())
                    )
                )
                warning_count += 1
                continue

            overlap_percent = best_overlap_area / original_area
            site_pk_value = development_site_features[best_site_id][
                development_site_pk_idx
            ]
            current_pk = feature[building_level_fk_field]

            if overlap_percent < (1 - self.OUTSIDE_TOLERANCE):
                feedback.pushWarning(
                    self.tr(
                        "Building level {} overlaps development site {} by only "
                        "{}%, more than {}% of the building level area lies "
                        "outside the development site".format(
                            feature.id(),
                            site_pk_value,
                            round(overlap_percent * 100, 1),
                            self.OUTSIDE_TOLERANCE * 100,
                        )
                    )
                )
                warning_count += 1

            if current_pk != site_pk_value:
                updates[feature.id()] = (building_level_fk_field, site_pk_value)
                reassigned_count += 1

        # apply updates
        if updates:
            with wrapped_edits(building_level_layer) as edits:
                for fid, (field_name, value) in updates.items():
                    field_idx = building_level_layer.fields().lookupField(field_name)
                    edits.changeAttributeValue(fid, field_idx, value)

        feedback.pushInfo(
            self.tr(
                "Reassigned {} of {} building levels ({} warnings)".format(
                    reassigned_count, total_count, warning_count
                )
            )
        )

        return {self.OUTPUT: building_level_layer.id()}
