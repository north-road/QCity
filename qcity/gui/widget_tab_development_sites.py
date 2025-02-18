import sqlite3

from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtWidgets import QListWidgetItem, QComboBox, QWidget, QDialog, QLineEdit, QSpinBox, QDoubleSpinBox
from qgis.core import QgsVectorLayer, QgsFeatureRequest, QgsProject
from qgis.gui import QgsNewNameDialog

from qcity.core import SETTINGS_MANAGER


class WidgetUtilsDevelopmentSites(QObject):
    def __init__(self, og_widget):
        super().__init__(og_widget)
        self.og_widget = og_widget

        self.og_widget.toolButton_development_site_add.clicked.connect(
            self.action_maptool_emit
        )

        self.og_widget.toolButton_development_site_remove.clicked.connect(
            self.remove_selected_sites
        )

        self.og_widget.toolButton_development_site_rename.clicked.connect(
            self.update_site_name_gpkg
        )

        self.og_widget.lineEdit_development_site_address.textChanged.connect(
            lambda value,
            widget=self.og_widget.lineEdit_development_site_address: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.lineEdit_development_site_owner.textChanged.connect(
            lambda value,
            widget=self.og_widget.lineEdit_development_site_owner: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.lineEdit_development_site_year.textChanged.connect(
            lambda value,
            widget=self.og_widget.lineEdit_development_site_year: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.comboBox_development_site_status.currentIndexChanged.connect(
            lambda value,
            widget=self.og_widget.comboBox_development_site_status: SETTINGS_MANAGER.save_widget_value_to_settings(
                widget, value, "development_sites"
            )
        )

        self.og_widget.listWidget_development_sites.currentItemChanged.connect(
            lambda item: self.update_development_site_parameters(item)
        )

        self.og_widget.listWidget_development_sites.currentItemChanged.connect(
            lambda item: self.update_development_site_listwidget(item)
        )

    def update_development_site_listwidget(self, item: QListWidgetItem) -> None:
        """Updates the listwidget of the development sites to show only development sites within the active project area."""
        site_layer = QgsProject.instance().mapLayer(SETTINGS_MANAGER.get_development_site_layer_id())
        area_layer = QgsProject.instance().mapLayer(SETTINGS_MANAGER.get_project_area_layer_id())

        name = self.og_widget.listWidget_project_areas.currentItem().text()

        request = QgsFeatureRequest().setFilterExpression(f'"name" = \'{name}\'')
        iterator = area_layer.getFeatures(request)
        filter_feature = next(iterator)
        filter_geom_wkt = filter_feature.geometry().asWkt()

        sql_filter = f"ST_Within($geometry, ST_GeomFromText('{filter_geom_wkt}', 4326)) and \"name\" = '{item.text()}'"
        site_layer.setSubsetString(sql_filter)

    def action_maptool_emit(self) -> None:
        """Emitted when plus button is clicked."""
        SETTINGS_MANAGER.add_feature_clicked.emit(True)

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

                gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.area_prefix}"
                layer = QgsVectorLayer(gpkg_path, SETTINGS_MANAGER.area_prefix, "ogr")
                layer.startEditing()

                feature_ids = [feat.id() for feat in layer.getFeatures() if feat["name"] == table_name]

                if feature_ids:
                    for fid in feature_ids:
                        layer.deleteFeature(fid)
                layer.commitChanges()

                del layer

            self.og_widget.label_current_development_site.setText("Development Site")

            if self.og_widget.listWidget_development_sites.count() < 1:
                SETTINGS_MANAGER.set_current_development_site_parameter_table_name(None)
                for widget in self.og_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                    # self.og_widget.tabWidget_project_area_parameters.setEnabled(False)

    def update_site_name_gpkg(self) -> None:
        """
        Updates the name of the table in the geopackage.
        """
        widget = self.og_widget.listWidget_development_sites.selectedItems()[0]
        old_layer_name = widget.text()

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

        layer_name = dialog.name()

        old_item_id = self.og_widget.listWidget_development_sites.row(widget)
        self.og_widget.listWidget_development_sites.takeItem(old_item_id)
        self.og_widget.listWidget_development_sites.addItem(layer_name)

        try:
            database_path = SETTINGS_MANAGER.get_database_path()
            with sqlite3.connect(database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f'ALTER TABLE "{SETTINGS_MANAGER.development_site_prefix}{old_layer_name}" RENAME TO "{SETTINGS_MANAGER.development_site_prefix}{layer_name}"'
                )
                cursor.execute(
                    f"UPDATE gpkg_contents SET table_name = '{SETTINGS_MANAGER.development_site_prefix}{layer_name}' WHERE table_name = '{SETTINGS_MANAGER.development_site_prefix}{old_layer_name}';"
                )
                cursor.execute(
                    f"UPDATE gpkg_geometry_columns SET table_name = '{SETTINGS_MANAGER.development_site_prefix}{layer_name}' WHERE table_name = '{SETTINGS_MANAGER.development_site_prefix}{old_layer_name}'; "
                )

                parameter_name = (
                    f"{SETTINGS_MANAGER.development_site_parameter_prefix}{layer_name}"
                )
                old_parameter_name = f"{SETTINGS_MANAGER.development_site_parameter_prefix}{old_layer_name}"
                cursor.execute(
                    f"UPDATE gpkg_contents SET table_name = '{old_parameter_name}' WHERE table_name = '{parameter_name}';"
                )
                cursor.execute(
                    f"ALTER TABLE '{old_parameter_name}' RENAME TO '{parameter_name}'"
                )
                conn.commit()

        except Exception as e:
            raise e

        # Set selection to changed item
        item_to_select = self.og_widget.listWidget_development_sites.findItems(
            layer_name, Qt.MatchExactly
        )[0]
        self.og_widget.listWidget_development_sites.setCurrentItem(item_to_select)
        SETTINGS_MANAGER.set_current_development_site_parameter_table_name(
            item_to_select.text()
        )

        self.og_widget.label_current_development_site.setText(layer_name)

    def update_development_site_parameters(self, item: QListWidgetItem) -> None:
        """
        Updates the line edits and combobox of the development sites tab to the currently selected site.
        """
        if item:
            feature_name = item.text()

            SETTINGS_MANAGER.set_current_development_site_parameter_table_name(
                feature_name
            )

            gpkg_path = f"{SETTINGS_MANAGER.get_database_path()}|layername={SETTINGS_MANAGER.development_site_prefix}"

            layer = QgsVectorLayer(gpkg_path, feature_name, "ogr")
            request = QgsFeatureRequest().setFilterExpression(f'"name" = \'{feature_name}\'')
            iterator = layer.getFeatures(request)
            feature = next(iterator)

            feature_dict = feature.attributes()
            col_names = [field.name() for field in layer.fields()]
            widget_values_dict = dict(zip(col_names, feature_dict))

            for widget_name in widget_values_dict.keys():
                if widget_name in ["fid", "name"]:
                    pass
                widget = self.og_widget.findChild(QWidget, widget_name)

                if isinstance(widget, QLineEdit):
                    widget.setText(widget_values_dict[widget_name])
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(int(widget_values_dict[widget_name]))

            self.og_widget.label_current_development_site.setText(feature_name)
