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
            self.update_site_name_gpkg
        )

        self.og_widget.address.textChanged.connect(self.save_widget_value_to_feature)
        self.og_widget.site_owner.textChanged.connect(self.save_widget_value_to_feature)

        self.og_widget.date.textChanged.connect(
            lambda value,
            widget=self.og_widget.date: SETTINGS_MANAGER.save_widget_value_to_layer(
                widget, value, SETTINGS_MANAGER.development_site_prefix
            )
        )

        self.og_widget.site_status.currentIndexChanged.connect(
            lambda value,
            widget=self.og_widget.site_status: SETTINGS_MANAGER.save_widget_value_to_layer(
                widget, value, SETTINGS_MANAGER.development_site_prefix
            )
        )

        #self.og_widget.listWidget_development_sites.currentItemChanged.connect(
        #    lambda item: self.update_development_site_parameters(item)
        #)

     #   self.og_widget.listWidget_development_sites.itemClicked.connect(
     #       lambda item: self.update_building_level_listwidget(item)
     #   )

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
        site_layer = self.get_layer()

        super().set_feature(feature)

        # PROJECT_CONTROLLER.set_current_project_area(feature.id())

        # TODO hide others from renderer only!
        # site_layer.setSubsetString(f"\"fid\" = '{feature.id()}'")

        feature_bbox = QgsReferencedRectangle(feature.geometry().boundingBox(), site_layer.crs())

        CanvasUtils.zoom_to_extent_if_not_visible(
            self.og_widget.iface.mapCanvas(),
            feature_bbox,
        )

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

    def update_building_level_listwidget(self, item: QListWidgetItem) -> None:
        """Updates the building levels listwidget to only contain sites within the current development site"""
        if not item:
            return

        level_layer = PROJECT_CONTROLLER.get_building_levels_layer()
        site_layer = PROJECT_CONTROLLER.get_development_sites_layer()

        self.og_widget.listWidget_building_levels.clear()
        site_layer.setSubsetString("")
        level_layer.setSubsetString("")

        names = list()
        pk = SETTINGS_MANAGER.get_pk(SETTINGS_MANAGER.building_level_prefix)
        for feat in level_layer.getFeatures():
            if feat.id() == pk:
                name = feat["name"]
                self.og_widget.listWidget_building_levels.addItem(name)
                names.append(name)

        site_layer.setSubsetString(f"\"name\" = '{item.text()}'")
        name_filter = ", ".join(f"'{name}'" for name in names)
        level_layer.setSubsetString(
            f"name IN ({name_filter})"
        )

    def update_site_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.og_widget.listWidget_development_sites.selectedItems()[0]
        old_feat_name = widget.text()

        existing_names = [
            self.og_widget.listWidget_development_sites.item(i).text()
            for i in range(self.og_widget.listWidget_development_sites.count())
        ]

        dialog = QgsNewNameDialog(
            initial="",
            existing=existing_names,
            cs=Qt.CaseSensitivity.CaseSensitive,
            parent=self.og_widget.iface.mainWindow(),
        )

        dialog.setWindowTitle(self.tr("Rename"))
        dialog.setAllowEmptyName(False)
        dialog.setHintString(self.tr("Enter a name for the development site"))

        if dialog.exec_() != QDialog.DialogCode.Accepted:
            return

        new_feat_name = dialog.name()

        old_item_id = self.og_widget.listWidget_development_sites.row(widget)
        self.og_widget.listWidget_development_sites.takeItem(old_item_id)
        self.og_widget.listWidget_development_sites.addItem(new_feat_name)

        layer = QgsVectorLayer(
            f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.development_site_prefix}",
            SETTINGS_MANAGER.development_site_prefix,
            "ogr",
        )
        if layer:
            layer.startEditing()
            for feature in layer.getFeatures():
                if feature["name"] == old_feat_name:
                    feature["name"] = new_feat_name
                    layer.updateFeature(feature)
            layer.commitChanges()

        # Set selection to changed item
        item_to_select = self.og_widget.listWidget_development_sites.findItems(
            new_feat_name, Qt.MatchExactly
        )[0]
        self.og_widget.listWidget_development_sites.setCurrentItem(item_to_select)
        SETTINGS_MANAGER.set_current_development_site_feature_name(
            item_to_select.text()
        )

        self.og_widget.label_current_development_site.setText(new_feat_name)

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
