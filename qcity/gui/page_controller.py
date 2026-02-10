from typing import Optional, List

from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    pyqtSignal,
    QItemSelectionModel,
)
from qgis.PyQt.QtGui import QFontMetrics
from qgis.PyQt.QtWidgets import (
    QWidget,
    QSpinBox,
    QDoubleSpinBox,
    QListView,
    QLabel,
    QLineEdit,
    QComboBox,
    QDialog,
    QMessageBox,
    QCheckBox,
)
from qgis.core import QgsFeature, NULL, QgsReferencedRectangle, QgsVectorLayer
from qgis.gui import QgsNewNameDialog, QgsSpinBox, QgsDoubleSpinBox

from .canvas_utils import CanvasUtils
from .feature_list_model import FeatureListModel, FeatureFilterProxyModel
from ..core import LayerUtils, LayerType, get_project_controller, DatabaseUtils
from ..core.utils import wrapped_edits


class PageController(QObject):
    """
    Base QObject class for dock page controllers
    """

    add_feature_clicked = pyqtSignal()

    def __init__(
        self,
        layer_type: LayerType,
        og_widget: "QCityDockWidget",
        tab_widget: QWidget,
        list_view: QListView,
        current_item_label: QLabel = None,
    ):
        super().__init__(og_widget)
        self.layer_type = layer_type
        self.og_widget: "QCityDockWidget" = og_widget
        self.tab_widget: QWidget = tab_widget

        self.list_view: QListView = list_view
        self.current_item_label = current_item_label
        self.skip_fields_for_widgets = []
        self._block_feature_updates = False

        self.list_model = FeatureListModel(self.layer_type, self)
        self.proxy_model = FeatureFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.list_model)
        if self.list_view is not None:
            self.list_view.setModel(self.proxy_model)

        self.current_feature_id: Optional[int] = None
        self.clearable_widgets: List[QWidget] = []

        if self.list_view is not None:
            fm = QFontMetrics(self.list_view.font())
            row_height = fm.height()
            self.list_view.setMinimumHeight(row_height * 10)

        if self.tab_widget is not None:
            for spin_box in self.tab_widget.findChildren((QSpinBox, QDoubleSpinBox)):
                spin_box.editingFinished.connect(self.widget_edit_finished)
                self.clearable_widgets.append(spin_box)

            for spin_box in self.tab_widget.findChildren(
                (QgsSpinBox, QgsDoubleSpinBox)
            ):
                spin_box.setShowClearButton(False)

            for line_edit in self.tab_widget.findChildren(QLineEdit):
                p = line_edit.parent()
                is_child_of_spinbox = False
                while p:
                    if isinstance(p, (QSpinBox, QDoubleSpinBox)):
                        is_child_of_spinbox = True
                        break
                    p = p.parent()
                if not is_child_of_spinbox:
                    line_edit.editingFinished.connect(self.widget_edit_finished)
                    self.clearable_widgets.append(line_edit)

            for checkbox in self.tab_widget.findChildren(QCheckBox):
                checkbox.toggled.connect(self.save_widget_value_to_feature)
                self.clearable_widgets.append(checkbox)

            for combo in self.tab_widget.findChildren(QComboBox):
                field_config = DatabaseUtils.get_field_config(
                    self.layer_type, combo.objectName()
                )
                if field_config is not None and "map" in field_config:
                    for code, value in field_config["map"].items():
                        combo.addItem(value, code)

                combo.currentIndexChanged.connect(self.save_widget_value_to_feature)
                self.clearable_widgets.append(combo)

        if self.list_view is not None:
            self.list_view.selectionModel().selectionChanged.connect(
                self.set_current_feature_from_list
            )

    def add_feature_to_list(
        self, feature: QgsFeature, set_current: bool = True, add_to_top: bool = False
    ):
        """
        Adds a new feature to the list widget
        """
        self.list_view.setEnabled(True)

        if not add_to_top or self.list_model.rowCount() == 0:
            self.list_model.add_feature(feature)
        else:
            self.list_model.insert_feature(0, feature)

        if set_current:
            model_index = self.list_model.index_for_feature(feature)
            proxy_index = self.proxy_model.mapFromSource(model_index)
            self.list_view.selectionModel().select(
                proxy_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
            )

    def set_current_feature_from_list(self):
        """
        Sets the current feature to show in the widget
        """
        selected_indices = self.list_view.selectionModel().selectedIndexes()
        if not selected_indices:
            self.clear_feature()
            return

        current_index = self.proxy_model.mapToSource(selected_indices[0])

        self.current_feature_id = self.list_model.data(
            current_index, FeatureListModel.FEATURE_ID_ROLE
        )
        self.set_feature(self.get_feature_by_id(self.current_feature_id))

        if self.current_item_label is not None:
            self.current_item_label.setText(self.list_model.data(current_index))

    def get_layer(self) -> QgsVectorLayer:
        """
        Returns the layer associated with the page
        """
        layer = get_project_controller().get_layer(self.layer_type)
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

    def widget_edit_finished(self):
        """
        Triggered when a widget editing has finished
        """
        widget = self.sender()
        if isinstance(widget, QLineEdit):
            self.save_widget_value_to_feature(widget.text())
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            value = widget.value()
            if widget.property("stored_value") is not None and value == widget.property(
                "stored_value"
            ):
                # no change
                return
            self.save_widget_value_to_feature(widget.value())
        else:
            assert False, f"Not handled widget type: {widget}"

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
        if isinstance(widget, QComboBox):
            value = widget.currentData()
        elif isinstance(widget, QCheckBox):
            value = widget.isChecked()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            value = widget.value()
            widget.setProperty("stored_value", value)

        LayerUtils.store_value(
            self.layer_type, self.current_feature_id, field_name, value
        )

    def clear_feature(self):
        """
        Clears the current feature from the page
        """
        if self.current_item_label is not None:
            self.current_item_label.clear()

        for widget in self.clearable_widgets:
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(-1)

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
            widget = self.og_widget.findChild((QWidget), widget_name)
            if isinstance(widget, QSpinBox):
                if value == NULL:
                    continue

                widget.setValue(int(value))
                widget.setProperty("stored_value", int(value))
            elif isinstance(widget, QDoubleSpinBox):
                if value == NULL:
                    continue

                widget.setValue(float(value))
                widget.setProperty("stored_value", float(value))
            elif isinstance(widget, QLineEdit):
                if value == NULL:
                    widget.clear()
                else:
                    widget.setText(str(value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QComboBox):
                match_index = widget.findData(value)
                if match_index >= 0:
                    widget.setCurrentIndex(match_index)
                else:
                    widget.setCurrentIndex(-1)
            elif isinstance(widget, QLabel):
                decimals = widget.property("decimals")
                if decimals is not None:
                    widget.setText("%.*f" % (decimals, value))
                else:
                    widget.setText(str(value))

    def remove_current_selection(self) -> None:
        """
        Removes selected objects from the list widget, and deletes them
        (and all child objects) from the database.
        """
        selected_indices = self.list_view.selectionModel().selectedIndexes()
        if not selected_indices:
            return

        feature_ids = {
            i.data(FeatureListModel.FEATURE_ID_ROLE): i.data(
                Qt.ItemDataRole.DisplayRole
            )
            for i in selected_indices
        }
        if len(feature_ids) == 1:
            item_text = next(iter(feature_ids.values()))
        else:
            item_text = ", ".join(t for t in feature_ids.values())
        if (
            QMessageBox.warning(
                self.list_view,
                self.tr("Remove {}").format(
                    self.layer_type.as_title_case(plural=False)
                ),
                self.tr(
                    "Are you sure you want to remove {}? This will permanently delete the {} and all related objects from the database."
                ).format(item_text, self.layer_type.as_sentence_case(plural=False)),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        for feature_id, item in feature_ids.items():
            if not self.delete_feature_and_child_objects(feature_id):
                return

    def remove_item_from_list(self, feature_id: int):
        """
        Removes the item with matching feature ID from the list widget
        """
        self.list_model.remove_feature_by_id(feature_id)

    def rename_current_selection(self):
        """
        Renames the selected object
        """
        selected_indices = self.list_view.selectionModel().selectedIndexes()
        if not selected_indices:
            return
        selected_index = selected_indices[0]
        feature_id = self.list_model.data(
            self.proxy_model.mapToSource(selected_index),
            FeatureListModel.FEATURE_ID_ROLE,
        )
        selected_item_text = self.list_model.data(selected_index)

        existing_names = get_project_controller().get_unique_names(self.layer_type)

        dialog = QgsNewNameDialog(
            initial=selected_item_text,
            existing=existing_names,
            cs=Qt.CaseSensitivity.CaseSensitive,
            parent=self.og_widget.iface.mainWindow(),
        )

        dialog.setWindowTitle(
            self.tr("Rename {}").format(self.layer_type.as_title_case(plural=False))
        )
        dialog.setAllowEmptyName(False)
        dialog.setOverwriteEnabled(False)
        dialog.setHintString(
            self.tr("Enter a new name for the {}").format(
                self.layer_type.as_sentence_case(plural=False)
            )
        )
        dialog.setConflictingNameWarning(
            self.tr("A {} with this name already exists").format(
                self.layer_type.as_sentence_case(plural=False)
            )
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_feat_name = dialog.name()
        self.list_model.rename(selected_index, new_feat_name)
        if self.current_item_label is not None:
            self.current_item_label.setText(new_feat_name)

        layer = self.get_layer()
        with wrapped_edits(layer) as edits:
            edits.changeAttributeValue(
                feature_id,
                layer.fields().lookupField(
                    DatabaseUtils.name_field_for_layer(self.layer_type)
                ),
                new_feat_name,
            )

    def zoom_to_feature(self, feature: QgsFeature):
        """
        Centers the canvas on a feature
        """
        feature_bbox = QgsReferencedRectangle(
            feature.geometry().boundingBox(), self.get_layer().crs()
        )

        CanvasUtils.zoom_to_extent_if_not_visible(
            self.og_widget.iface.mapCanvas(),
            feature_bbox,
        )
