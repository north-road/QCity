from typing import Union
from qgis.core import (
    QgsProject
)
from .enums import LayerType
from .project import ProjectUtils


class LayerUtils:
    """
    Contains utility functions for working with QCity layers
    """

    @staticmethod
    def store_value(
            project: QgsProject,
            layer_type: LayerType,
            feature_id: int,
            field_name: str,
            value: Union[float, int, str]
    ) -> bool:
        """
        Stores a value in a QCity database layer
        """
        layer = ProjectUtils.get_layer(project, layer_type)
        if not layer:
            return False

        field_index = layer.fields().lookupField(field_name)

        if not layer.startEditing():
            return False
        if not layer.changeAttributeValue(feature_id, field_index, value):
            return False
        if not layer.commitChanges():
            return False

        return True
