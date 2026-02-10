from typing import Optional, List

from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    QAbstractListModel,
    QModelIndex,
)
from qgis.core import QgsFeature

from ..core import LayerType, DatabaseUtils


class FeatureListModel(QAbstractListModel):
    """
    A qt list model for showing features
    """

    FEATURE_ID_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, layer_type: LayerType, parent: Optional[QObject] = None):
        super().__init__(parent)

        self.layer_type = layer_type
        self.items: List[QgsFeature] = []

    def rowCount(self, parent: Optional[QModelIndex] = QModelIndex()):
        if parent.isValid():
            return 0

        return len(self.items)

    def data(
        self,
        index: Optional[QModelIndex] = QModelIndex(),
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if not index.isValid() or index.row() < 0 or index.row() >= len(self.items):
            return None

        feature = self.items[index.row()]
        if role == self.FEATURE_ID_ROLE:
            return feature.id()
        elif role == Qt.ItemDataRole.DisplayRole:
            return feature[DatabaseUtils.name_field_for_layer(self.layer_type)]

        return None

    def clear(self):
        """
        Clears all items from the model
        """
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def index_for_feature(self, feature: QgsFeature) -> QModelIndex:
        """
        Returns the index corresponding to a given feature, or an invalid
        index if not found
        """
        return self.index_for_feature_id(feature.id())

    def index_for_feature_id(self, feature_id: int) -> QModelIndex:
        """
        Returns the index corresponding to a given feature, or an invalid
        index if not found
        """
        for row in range(0, self.rowCount()):
            if self.items[row].id() == feature_id:
                return self.index(row)

        return QModelIndex()

    def add_feature(self, feature: QgsFeature):
        """
        Adds a feature to the end of the model
        """
        self.beginInsertRows(QModelIndex(), len(self.items), len(self.items))
        self.items.append(feature)
        self.endInsertRows()

    def insert_feature(self, row: int, feature: QgsFeature):
        """
        Inserts a feature at the specified row in the model
        """
        self.beginInsertRows(QModelIndex(), row, row)
        self.items.insert(row, feature)
        self.endInsertRows()

    def rename(self, index: QModelIndex, new_name: str):
        """
        Renames the item at the given index.
        """
        if not index.isValid() or index.row() < 0 or index.row() >= len(self.items):
            return

        self.items[index.row()][DatabaseUtils.name_field_for_layer(self.layer_type)] = (
            new_name
        )
        self.dataChanged.emit(index, index)

    def remove_feature_by_id(self, feature_id: int):
        """
        Removes a feature by feature ID
        """
        index = self.index_for_feature_id(feature_id)
        if not index.isValid():
            return

        self.beginRemoveRows(QModelIndex(), index.row(), index.row())
        del self.items[index.row()]
        self.endRemoveRows()

    def move_row(self, index: QModelIndex, up: bool):
        """
        Moves a row in the model
        """
        row = index.row()
        if up:
            if row == 0:
                return

            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row - 1)
            self.items.insert(row - 1, self.items.pop(row))
            self.endMoveRows()
        else:
            if row == len(self.items) - 1:
                return

            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row + 2)
            self.items.insert(row + 1, self.items.pop(row))
            self.endMoveRows()
