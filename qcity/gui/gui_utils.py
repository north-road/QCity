"""
GUI Utilities
"""

import math
import os
from typing import (
    Optional,
)

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import (
    QIcon,
    QFont,
    QFontMetrics,
    QImage,
    QPixmap,
    QColor,
    QPainter,
)
from qgis.PyQt.QtSvg import QSvgRenderer
from qgis.core import Qgis

FONT_FAMILIES = ""


class GuiUtils:
    """
    Utilities for GUI plugin components
    """

    @staticmethod
    def get_icon(icon: str) -> QIcon:
        """
        Returns a plugin icon
        :param icon: icon name (svg file name)
        :return: QIcon
        """
        path = GuiUtils.get_icon_svg(icon)
        if not path:
            return QIcon()

        return QIcon(path)

    @staticmethod
    def get_icon_svg(icon: str) -> str:
        """
        Returns a plugin icon's SVG file path
        :param icon: icon name (svg file name)
        :return: icon svg path
        """
        path = os.path.join(os.path.dirname(__file__), "..", "icons", icon)
        if not os.path.exists(path):
            return ""

        return path

    @staticmethod
    def get_icon_pixmap(icon: str) -> QPixmap:
        """
        Returns a plugin icon's PNG file path
        :param icon: icon name (png file name)
        :return: icon png path
        """
        path = os.path.join(os.path.dirname(__file__), "..", "icons", icon)
        if not os.path.exists(path):
            return QPixmap()

        im = QImage(path)
        return QPixmap.fromImage(im)

    @staticmethod
    def get_svg_as_image(
        icon: str,
        width: int,
        height: int,
        background_color: Optional[QColor] = None,
        device_pixel_ratio: float = 1,
    ) -> QImage:
        """
        Returns an SVG returned as an image
        """
        path = GuiUtils.get_icon_svg(icon)
        if not os.path.exists(path):
            return QImage()

        renderer = QSvgRenderer(path)
        image = QImage(
            int(width * device_pixel_ratio),
            int(height * device_pixel_ratio),
            QImage.Format.Format_ARGB32,
        )
        image.setDevicePixelRatio(device_pixel_ratio)
        if not background_color:
            image.fill(Qt.GlobalColor.transparent)
        else:
            image.fill(background_color)

        painter = QPainter(image)
        painter.scale(1 / device_pixel_ratio, 1 / device_pixel_ratio)
        renderer.render(painter)
        painter.end()

        return image

    @staticmethod
    def get_ui_file_path(file: str) -> str:
        """
        Returns a UI file's path
        :param file: file name (uifile name)
        :return: ui file path
        """
        path = os.path.join(os.path.dirname(__file__), "..", "ui", file)
        if not os.path.exists(path):
            return ""

        return path

    @staticmethod
    def scale_icon_size(standard_size: int) -> int:
        """
        Scales an icon size accounting for device DPI
        """
        fm = QFontMetrics((QFont()))
        scale = 1.1 * standard_size / 24.0
        return int(
            math.floor(
                max(Qgis.UI_SCALE_FACTOR * fm.height() * scale, float(standard_size))
            )
        )
