import math

from qgis.core import Qgis, QgsRasterLayer, QgsUnitTypes


class wrapped_edits:
    """
    Context manager which wraps a set of edits to a layer,
    only committing changes if the layer wasn't originally editable
    """

    def __init__(self, layer):
        self.layer = layer
        self._was_editable = False

    def __enter__(self):
        self._was_editable = self.layer.isEditable()
        if not self._was_editable:
            self.layer.startEditing()
        return self.layer

    def __exit__(self, ex_type, ex_value, traceback):
        if ex_type is None:
            if not self._was_editable:
                assert self.layer.commitChanges()
            return True
        else:
            return False


class Utils:
    @staticmethod
    def guess_raster_vert_units(raster_layer: QgsRasterLayer) -> Qgis.DistanceUnit:
        """
        Guesses the vertical units for a raster layer
        """
        xy_units = raster_layer.crs().mapUnits()
        elev_properties = raster_layer.elevationProperties()

        if not elev_properties.isEnabled():
            if xy_units == Qgis.DistanceUnit.Degrees:
                # assume meters for a degrees based dataset
                return Qgis.DistanceUnit.Meters

            # assume same as horizontal units
            return xy_units

        z_scale = elev_properties.zScale()
        for _unit in (
            Qgis.DistanceUnit.Meters,
            Qgis.DistanceUnit.Feet,
        ):
            if math.isclose(
                QgsUnitTypes.fromUnitToUnitFactor(xy_units, _unit),
                z_scale,
                rel_tol=0.01,
            ):
                return _unit

        if xy_units == Qgis.DistanceUnit.Degrees:
            # try assuming meters for a degrees based dataset
            for _unit in (
                Qgis.DistanceUnit.Meters,
                Qgis.DistanceUnit.Feet,
            ):
                if math.isclose(
                    QgsUnitTypes.fromUnitToUnitFactor(Qgis.DistanceUnit.Meters, _unit),
                    z_scale,
                    rel_tol=0.01,
                ):
                    return _unit
            return Qgis.DistanceUnit.Meters
        return xy_units
