import math

from qgis.core import Qgis, QgsRasterLayer, QgsUnitTypes


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
