from qgis.core import QgsReferencedRectangle, QgsCoordinateTransform, QgsCsException
from qgis.gui import QgsMapCanvas

class CanvasUtils:
    """
    Contains utility functions for working with map canvases
    """

    @staticmethod
    def zoom_to_extent_if_not_visible(canvas: QgsMapCanvas, extent: QgsReferencedRectangle):
        """
        Zooms the canvas to the extent of the given rectangle, but only if the full rectangle
        isn't already visible in the canvas.

        TODO: consider also zooming in if the full rectangle is visible, but only covers a very
        small region of the canvas
        """
        rect_to_canvas_ct = QgsCoordinateTransform(
            extent.crs(),
            canvas.mapSettings().destinationCrs(),
            canvas.mapSettings().transformContext()
        )
        rect_to_canvas_ct.setAllowFallbackTransforms(True)
        rect_to_canvas_ct.setBallparkTransformsAreAppropriate(True)

        try:
            rect_in_canvas_crs = rect_to_canvas_ct.transformBoundingBox(extent)
        except QgsCsException:
            return

        current_canvas_rect = canvas.extent()
        if current_canvas_rect.contains(rect_in_canvas_crs):
            # nothing to do, already visible
            return

        canvas.zoomToFeatureExtent(rect_in_canvas_crs)
        canvas.refresh()
