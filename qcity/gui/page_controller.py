from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox

from qgis.core import QgsFeature, NULL


class PageController(QObject):
    """
    Base QObject class for dock page controllers
    """

    def __init__(self, og_widget: 'QCityDockWidget'):
        super().__init__(og_widget)
        self.og_widget: 'QCityDockWidget' = og_widget
        self.skip_fields_for_widgets = []

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
