from typing import Optional, Union

from qgis.core import (
    QgsVectorLayer,
    QgsRuleBasedRenderer,
    QgsSingleSymbolRenderer,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCsException,
)
from .enums import LayerType
from .project import PROJECT_CONTROLLER
from .utils import wrapped_edits


class LayerUtils:
    """
    Contains utility functions for working with QCity layers
    """

    @staticmethod
    def store_value(
        layer_type: LayerType,
        feature_id: int,
        field_name: str,
        value: Union[float, int, str],
    ) -> bool:
        """
        Stores a value in a QCity database layer
        """
        layer = PROJECT_CONTROLLER.get_layer(layer_type)
        if not layer:
            return False

        field_index = layer.fields().lookupField(field_name)
        if field_index < 0:
            return False

        with wrapped_edits(layer) as edits:
            if not edits.changeAttributeValue(feature_id, field_index, value):
                return False

        return True

    @staticmethod
    def set_renderer_filter(
        layer: QgsVectorLayer, filter_string: Optional[str]
    ) -> bool:
        """
        Morphs a layer's renderer to respect the specified filter string
        """
        current_renderer = layer.renderer()
        if isinstance(current_renderer, QgsRuleBasedRenderer):
            # current renderer is rule based. Either update the rule filter,
            # or downgrade to single symbol renderer
            rule_count = len(current_renderer.rootRule().children())
            if rule_count > 1:
                return False

            if filter_string:
                new_renderer = current_renderer.clone()
                new_renderer.rootRule().children()[0].setFilterExpression(filter_string)
                layer.setRenderer(new_renderer)
            else:
                # remove rule based renderer
                only_rule = current_renderer.rootRule().children()[0]
                symbol = only_rule.symbol().clone()
                layer.setRenderer(QgsSingleSymbolRenderer(symbol))
            layer.triggerRepaint()
            return True
        elif isinstance(current_renderer, QgsSingleSymbolRenderer):
            if not filter_string:
                # nothing to do
                return True

            # current renderer is NOT rule based, upgrade to rule based
            root_rule = QgsRuleBasedRenderer.Rule(None)
            new_rule = QgsRuleBasedRenderer.Rule(
                current_renderer.symbol().clone(), filterExp=filter_string
            )
            root_rule.appendChild(new_rule)
            rule_based = QgsRuleBasedRenderer(root_rule)
            layer.setRenderer(rule_based)
            layer.triggerRepaint()
            return True

        return False

    @staticmethod
    def test_geometry_within(
        layer: QgsVectorLayer,
        feature_id: int,
        geometry: QgsGeometry,
        geometry_crs: QgsCoordinateReferenceSystem,
        tolerance_percent: Optional[float] = None,
    ) -> bool:
        """
        Tests whether a geometry is completely contained within a feature from a layer.

        tolerance_percent can be used to specify a tolerance (eg 0.05 = 5%) of the geometry
        which is allowed to fall outside the feature.
        """
        feature_geometry = layer.getFeature(feature_id).geometry()

        ct = QgsCoordinateTransform(geometry_crs, layer.crs(), layer.transformContext())
        reference_geometry = QgsGeometry(geometry)
        try:
            reference_geometry.transform(ct)
        except QgsCsException:
            return False

        if tolerance_percent is None:
            return feature_geometry.contains(reference_geometry)

        intersection = feature_geometry.intersection(reference_geometry)
        area_geometry = reference_geometry.area()
        intersection_area = intersection.area()
        return intersection_area >= (area_geometry * (1 - tolerance_percent))
