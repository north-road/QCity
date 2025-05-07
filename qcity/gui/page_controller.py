from typing import Optional

from qgis.PyQt.QtCore import Qt, QObject
from qgis.PyQt.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox, QListWidget, QLabel

from qgis.core import QgsFeature, NULL, QgsProject, QgsVectorLayer

from ..core import LayerUtils, SETTINGS_MANAGER, LayerType, ProjectUtils


class PageController(QObject):
    """
    Base QObject class for dock page controllers
    """

    def __init__(self,
                 layer_type: LayerType,
                 og_widget: 'QCityDockWidget',
                 tab_widget: QWidget,
                 list_widget: QListWidget,
                 current_item_label: QLabel = None):
        super().__init__(og_widget)
        self.layer_type = layer_type
        self.og_widget: 'QCityDockWidget' = og_widget
        self.tab_widget: QWidget = tab_widget
        self.list_widget: QListWidget = list_widget
        self.current_item_label = current_item_label
        self.skip_fields_for_widgets = []
        self._block_feature_updates = False

        self.current_feature_id: Optional[int] = None

        if self.tab_widget is not None:
            for spin_box in self.tab_widget.findChildren(
                (QSpinBox, QDoubleSpinBox)
            ):
                spin_box.valueChanged.connect(self.save_widget_value_to_feature)

        if self.list_widget is not None:
            self.list_widget.currentRowChanged.connect(
                self.set_current_feature_from_list
            )

    def set_current_feature_from_list(self, row):
        """
        Sets the current feature to show in the widget
        """
        current_item = self.list_widget.item(row)
        if not current_item:
            if self.current_item_label is not None:
                self.current_item_label.clear()
            return

        self.current_feature_id = current_item.data(Qt.UserRole)
        self.set_feature(
            self.get_feature_by_id(self.current_feature_id)
        )

        if self.current_item_label is not None:
            self.current_item_label.setText(current_item.text())

    def get_layer(self) -> QgsVectorLayer:
        """
        Returns the layer associated with the page
        """
        layer = ProjectUtils.get_layer(QgsProject.instance(), self.layer_type)
        return layer

    def get_feature_by_id(self, feature_id: int) -> QgsFeature:
        """
        Gets a feature from the associated layer by ID
        """
        return self.get_layer().getFeature(feature_id)

    def save_widget_value_to_feature(self, value):
        """
        Triggered when a widget value is changed by the user
        """
        if self._block_feature_updates:
            return

        if self.current_feature_id is None:
            return

        widget = self.sender()
        field_name = widget.objectName()

        LayerUtils.store_value(QgsProject.instance(),
                               self.layer_type,
                               self.current_feature_id,
                               field_name, value
                               )

    def set_feature(self, feature: QgsFeature):
        """
        Sets the current feature to show in the page
        """
        self._block_feature_updates = True
        attributes = feature.attributeMap()
        self.set_widget_values(attributes)
        self._block_feature_updates = False

    def set_widget_values(self, widget_values: dict):
        """
        Sets widget values from a dictionary
        """
        for field_name, value in widget_values.items():
            if field_name in self.skip_fields_for_widgets:
                continue

            widget_name = field_name
            widget = self.og_widget.findChild(
                (QWidget), widget_name
            )
            if isinstance(widget, QSpinBox):
                if value == NULL:
                    continue

                widget.setValue(int(value))
            elif isinstance(widget, QDoubleSpinBox):
                if value == NULL:
                    continue

                widget.setValue(float(value))
            else:
                assert False
