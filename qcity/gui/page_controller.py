from qgis.PyQt.QtCore import QObject


class PageController(QObject):
    """
    Base QObject class for dock page controllers
    """

    def __init__(self, og_widget: 'QCityDockWidget'):
        super().__init__(og_widget)
        self.og_widget: 'QCityDockWidget' = og_widget
