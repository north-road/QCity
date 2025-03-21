from qgis.PyQt.QtCore import QVariant


def get_qgis_type(key):
    return (
        QVariant.Double
        if "doubleSpinBox" in key
        else QVariant.Int
        if "spinBox" in key or "comboBox" in key
        else QVariant.String
        if "lineEdit" in key
        else QVariant.String
    )