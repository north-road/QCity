from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox

from qgis.core import QgsFeature, NULL

from ..core.settings import SETTINGS_MANAGER


class PageController(QObject):
    """
    Base QObject class for dock page controllers
    """

    def __init__(self, og_widget: 'QCityDockWidget', tab_widget: QWidget):
        super().__init__(og_widget)
        self.og_widget: 'QCityDockWidget' = og_widget
        self.tab_widget: QWidget = tab_widget
        self.skip_fields_for_widgets = []

        if self.tab_widget:
            for spin_box in self.tab_widget.findChildren(
                (QSpinBox, QDoubleSpinBox)
            ):
                spin_box.valueChanged.connect(
                    lambda value,
                    widget=spin_box: SETTINGS_MANAGER.save_widget_value_to_layer(
                        widget, value, SETTINGS_MANAGER.project_area_prefix
                    )
                )

    def set_feature(self, feature: QgsFeature):
        """
        Sets the current feature to show in the page
        """
        attributes = feature.attributeMap()
        self.set_widget_values(attributes)

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
