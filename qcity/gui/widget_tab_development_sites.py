from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtWidgets import (
    QListWidgetItem,
    QComboBox,
    QWidget,
    QDialog,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
)
from qgis.core import QgsVectorLayer, QgsMapLayerType, QgsFeature, QgsReferencedRectangle
from qgis.gui import QgsNewNameDialog

from qcity.core import SETTINGS_MANAGER, LayerType, PROJECT_CONTROLLER, DatabaseUtils
from .page_controller import PageController
from .canvas_utils import CanvasUtils


class DevelopmentSitesPageController(PageController):
    """
    Page controller for the development sites page
    """
    def __init__(self, og_widget, tab_widget, list_widget, current_item_label):
        super().__init__(LayerType.DevelopmentSites, og_widget, tab_widget, list_widget, current_item_label)
        self.skip_fields_for_widgets = ['fid', 'name', 'project_area_pk']

        PROJECT_CONTROLLER.project_area_changed.connect(self.on_project_area_changed)

        self.og_widget.toolButton_development_site_add.clicked.connect(
            self.add_feature_clicked
        )

        self.og_widget.toolButton_development_site_remove.clicked.connect(
            self.remove_selected_sites
        )

        self.og_widget.toolButton_development_site_rename.clicked.connect(
            self.rename_current_selection
        )

        self.og_widget.address.textChanged.connect(self.save_widget_value_to_feature)
        self.og_widget.site_owner.textChanged.connect(self.save_widget_value_to_feature)
        self.og_widget.date.textChanged.connect(self.save_widget_value_to_feature)

        self.og_widget.site_elevation.valueChanged.connect(
            lambda value: SETTINGS_MANAGER.save_widget_value_to_layer(
                self.og_widget.site_elevation,
                value,
                SETTINGS_MANAGER.development_site_prefix,
            )
        )

        self.og_widget.comboBox_auto_elevation.setAllowEmptyLayer(True)
        self.og_widget.comboBox_auto_elevation.setFilters(QgsMapLayerType.RasterLayer)
        self.og_widget.checkBox_auto_elevation.toggled.connect(
            self.get_elevation_from_dem
        )
        self.og_widget.checkBox_auto_elevation.toggled.connect(
            lambda: SETTINGS_MANAGER.save_checkbox_state(
                self.og_widget.checkBox_auto_elevation,
                self.og_widget.listWidget_development_sites.currentItem(),
            )
        )
    #    self.og_widget.listWidget_development_sites.currentItemChanged.connect(
     #       lambda item: SETTINGS_MANAGER.restore_checkbox_state(
      #          self.og_widget.checkBox_auto_elevation, item
     #       )
     #   )

    def on_project_area_changed(self, project_area_fid: int):
        """
        Called when the current project area FID is changed
        """
        site_layer = self.get_layer()
        self.list_widget.clear()
        foreign_key = DatabaseUtils.foreign_key_for_layer(self.layer_type)
        site_layer.setSubsetString(f'{foreign_key} = {project_area_fid}')

        for feat in site_layer.getFeatures():
            item = QListWidgetItem(self.list_widget)
            item.setText(feat["name"])
            item.setData(Qt.UserRole, feat.id())
            self.list_widget.addItem(item)

    def set_feature(self, feature: QgsFeature):
        super().set_feature(feature)

        PROJECT_CONTROLLER.set_current_development_site(feature.id())

        # TODO hide others from renderer only!
        # site_layer.setSubsetString(f"\"fid\" = '{feature.id()}'")

    def remove_selected_sites(self) -> None:
        """Removes selected area from Qlistwidget, map and geopackage."""
        tbr_areas = self.og_widget.listWidget_development_sites.selectedItems()

        if tbr_areas:
            rows = {
                self.og_widget.listWidget_development_sites.row(item): item.text()
                for item in tbr_areas
            }

            for key, table_name in rows.items():
                self.og_widget.listWidget_development_sites.takeItem(key)

                layers = self.og_widget.project.mapLayersByName(table_name)
                if layers:
                    self.og_widget.project.removeMapLayer(layers[0].id())

                gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.project_area_prefix}"
                layer = QgsVectorLayer(
                    gpkg_path, SETTINGS_MANAGER.project_area_prefix, "ogr"
                )
                layer.startEditing()

                feature_ids = [
                    feat.id()
                    for feat in layer.getFeatures()
                    if feat["name"] == table_name
                ]

                if feature_ids:
                    for fid in feature_ids:
                        layer.deleteFeature(fid)
                layer.commitChanges()

                del layer

            self.og_widget.label_current_development_site.setText("Development Site")

            if self.og_widget.listWidget_development_sites.count() < 1:
                SETTINGS_MANAGER.set_current_development_site_feature_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                    # self.og_widget.tabWidget_project_area_parameters.setEnabled(False)

    def get_elevation_from_dem(self, checked) -> None:
        """Gets the elevation for a centroid in a polygon feature and sets it as an attribute."""
        if checked:
            try:
                gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.development_site_prefix}"
                layer = QgsVectorLayer(gpkg_path, "", "ogr")
                name = self.og_widget.listWidget_development_sites.currentItem()

                dem_layer = self.og_widget.comboBox_auto_elevation.currentLayer()
                provider = dem_layer.dataProvider()

                feature = self.og_widget.get_feature_of_layer_by_name(layer, name)
                geom = feature.geometry()
                centroid = geom.centroid().asPoint()
                sample_value = int(provider.sample(centroid, 1)[0])
                feature["elevation"] = sample_value
                self.og_widget.spinBox_dev_site_elevation.setValue(sample_value)
                self.og_widget.spinBox_dev_site_elevation.setEnabled(False)
                layer.updateFeature(feature)
            except AttributeError:
                return
            except Exception as e:
                # TODO: Catch various exceptions here
                raise e
        else:
            self.og_widget.spinBox_dev_site_elevation.setValue(0)
            self.og_widget.spinBox_dev_site_elevation.setEnabled(True)
