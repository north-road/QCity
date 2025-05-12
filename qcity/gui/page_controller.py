from typing import Optional

from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, QDate
from qgis.PyQt.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox, QListWidget, QLabel, QLineEdit, QComboBox, QDialog, \
    QMessageBox, QListWidgetItem
from qgis.core import QgsFeature, NULL, QgsReferencedRectangle, QgsVectorLayer
from qgis.gui import QgsNewNameDialog, QgsSpinBox, QgsDoubleSpinBox

from .canvas_utils import CanvasUtils
from ..core import LayerUtils, LayerType, PROJECT_CONTROLLER, DatabaseUtils


class PageController(QObject):
    """
    Base QObject class for dock page controllers
    """
    add_feature_clicked = pyqtSignal()

    def __init__(self,
                 layer_type: LayerType,
                 og_widget: 'QCityDockWidget',
                 tab_widget: QWidget,
                 list_widget: QListWidget,
                 current_item_label: QLabel = None):
        super().__init__(og_widget)
        self.layer_type = layer_type
        self.og_widget: 'QCityDockWidget' = og_widget
        self.tab_widget: QWidget = tab_widget
        self.list_widget: QListWidget = list_widget
        self.current_item_label = current_item_label
        self.skip_fields_for_widgets = []
        self._block_feature_updates = False

        self.current_feature_id: Optional[int] = None

        if self.tab_widget is not None:
            for spin_box in self.tab_widget.findChildren(
                    (QSpinBox, QDoubleSpinBox)
            ):
                spin_box.valueChanged.connect(self.save_widget_value_to_feature)

            for spin_box in self.tab_widget.findChildren(
                    (QgsSpinBox, QgsDoubleSpinBox)
            ):
                spin_box.setShowClearButton(False)

            for line_edit in self.tab_widget.findChildren(
                    QLineEdit
            ):
                line_edit.textChanged.connect(self.save_widget_value_to_feature)

            for combo in self.tab_widget.findChildren(
                    QComboBox
            ):
                field_config = DatabaseUtils.get_field_config(self.layer_type, combo.objectName())
                if field_config is not None and "map" in field_config:
                    for code, value in field_config["map"].items():
                        combo.addItem(value, code)

        if self.list_widget is not None:
            self.list_widget.currentRowChanged.connect(
                self.set_current_feature_from_list
            )

    def add_feature_to_list(self, feature: QgsFeature, set_current: bool = True):
        """
        Adds a new feature to the list widget
        """
        self.list_widget.setEnabled(True)

        item = QListWidgetItem(self.list_widget)
        item.setText(feature[
                         DatabaseUtils.name_field_for_layer(self.layer_type)
                     ])
        item.setData(Qt.UserRole, feature.id())

        self.list_widget.addItem(item)
        if set_current:
            row = self.list_widget.row(item)
            self.list_widget.setCurrentRow(row)

    def set_current_feature_from_list(self, row):
        """
        Sets the current feature to show in the widget
        """
        current_item = self.list_widget.item(row)
        if not current_item:
            if self.current_item_label is not None:
                self.current_item_label.clear()
            return

        self.current_feature_id = current_item.data(Qt.UserRole)
        self.set_feature(
            self.get_feature_by_id(self.current_feature_id)
        )

        if self.current_item_label is not None:
            self.current_item_label.setText(current_item.text())

    def get_layer(self) -> QgsVectorLayer:
        """
        Returns the layer associated with the page
        """
        layer = PROJECT_CONTROLLER.get_layer(self.layer_type)
        return layer

    def get_feature_by_id(self, feature_id: int) -> QgsFeature:
        """
        Gets a feature from the associated layer by ID
        """
        return self.get_layer().getFeature(feature_id)

    def delete_feature_and_child_objects(self, feature_id: int) -> bool:
        """
        Deletes a parent feature and all its child objects

        Returns True if the deletion was successful
        """
        return False

    def save_widget_value_to_feature(self, value):
        """
        Triggered when a widget value is changed by the user
        """
        if self._block_feature_updates:
            return

        if self.current_feature_id is None:
            return

        widget = self.sender()
        field_name = widget.objectName()

        LayerUtils.store_value(self.layer_type,
                               self.current_feature_id,
                               field_name, value
                               )

    def set_feature(self, feature: QgsFeature):
        """
        Sets the current feature to show in the page
        """
        self._block_feature_updates = True
        attributes = feature.attributeMap()
        self.set_widget_values(attributes)
        self._block_feature_updates = False

        self.zoom_to_feature(feature)

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
            elif isinstance(widget, QLineEdit):
                if value == NULL:
                    widget.clear()
                else:
                    widget.setText(str(value))
            elif isinstance(widget, QComboBox):
                # widget.setCurrentIndex(int(widget_values_dict[widget_name]))
                pass
            else:
                assert False

    def remove_current_selection(self) -> None:
        """
        Removes selected objects from the list widget, and deletes them
        (and all child objects) from the database.
        """
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        feature_ids = {
            item.data(Qt.UserRole): item for item in selected_items
        }
        if len(feature_ids) == 1:
            item_text = next(iter(feature_ids.values())).text()
        else:
            item_text = ', '.join(t.text() for t in feature_ids.values())
        if QMessageBox.warning(self.list_widget,
                               self.tr('Remove {}').format(self.layer_type.as_title_case(plural=False)),
                               self.tr(
                                   'Are you sure you want to remove {}? This will permanently delete the {} and all related objects from the database.').format(
                                   item_text,
                                   self.layer_type.as_sentence_case(plural=False)
                               ),
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                               QMessageBox.StandardButton.No
                               ) != QMessageBox.StandardButton.Yes:
            return

        for feature_id, item in feature_ids.items():
            if not self.delete_feature_and_child_objects(feature_id):
                return

    def remove_item_from_list(self, feature_id: int):
        """
        Removes the item with matching feature ID from the list widget
        """
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item.data(Qt.UserRole) == feature_id:
                self.list_widget.takeItem(row)
                return

    def rename_current_selection(self):
        """
        Renames the selected object
        """
        selected_item = self.list_widget.selectedItems()[0]
        feature_id = selected_item.data(Qt.UserRole)

        existing_names = PROJECT_CONTROLLER.get_unique_names(self.layer_type)

        dialog = QgsNewNameDialog(
            initial="",
            existing=existing_names,
            cs=Qt.CaseSensitivity.CaseSensitive,
            parent=self.og_widget.iface.mainWindow(),
        )

        dialog.setWindowTitle(self.tr("Rename {}").format(self.layer_type.as_title_case(plural=False)))
        dialog.setAllowEmptyName(False)
        dialog.setHintString(
            self.tr("Enter a new name for the {}").format(self.layer_type.as_sentence_case(plural=False)))

        if dialog.exec_() != QDialog.DialogCode.Accepted:
            return

        new_feat_name = dialog.name()
        selected_item.setText(new_feat_name)
        if self.current_item_label is not None:
            self.current_item_label.setText(new_feat_name)

        layer = self.get_layer()
        layer.startEditing()
        layer.changeAttributeValue(feature_id, layer.fields().lookupField(
            DatabaseUtils.name_field_for_layer(self.layer_type)), new_feat_name)
        layer.commitChanges()

    def zoom_to_feature(self, feature: QgsFeature):
        """
        Centers the canvas on a feature
        """
        feature_bbox = QgsReferencedRectangle(feature.geometry().boundingBox(), self.get_layer().crs())

        CanvasUtils.zoom_to_extent_if_not_visible(
            self.og_widget.iface.mapCanvas(),
            feature_bbox,
        )
