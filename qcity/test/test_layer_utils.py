import os
import tempfile
import unittest

from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject,
    QgsRuleBasedRenderer,
    QgsVectorLayerUtils,
    QgsSymbol,
    QgsVectorLayer,
    QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer
)

from qcity.core import LayerType
from qcity.core.database import DatabaseUtils
from qcity.core.layer import LayerUtils
from qcity.core.project import PROJECT_CONTROLLER

test_data_path = os.path.join(os.path.dirname(__file__), "test_data")


class TestLayerUtils(unittest.TestCase):

    def test_change_attributes(self) -> None:
        """
        Test changing attributes in a layer
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, "test_database.gpkg")

            DatabaseUtils.create_base_tables(
                gpkg_path
            )

            p = QgsProject.instance()
            PROJECT_CONTROLLER.add_database_layers_to_project(p, gpkg_path)

            project_area_layer = PROJECT_CONTROLLER.get_project_area_layer()
            # create an initial feature
            f = QgsVectorLayerUtils.createFeature(project_area_layer)
            f['car_parking_1_bedroom'] = 1
            f['car_parking_2_bedroom'] = 2
            f['car_parking_3_bedroom'] = 3
            f['car_parking_4_bedroom'] = 4
            project_area_layer.startEditing()
            self.assertTrue(project_area_layer.addFeature(f))
            self.assertTrue(project_area_layer.commitChanges())

            f = next(project_area_layer.getFeatures())
            f_id = f.id()

            self.assertTrue(
                LayerUtils.store_value(LayerType.ProjectAreas, f_id, 'car_parking_3_bedroom', 33)
            )

            f_3 = project_area_layer.getFeature(f_id)
            self.assertEqual(f_3['car_parking_3_bedroom'], 33)

    def create_test_layer(self, layer_name="test_layer"):
        """
        Helper function to create an in-memory point vector layer.
        """
        uri = f"Point?crs=epsg:4326&field=cat:integer&field=name:string&uid={layer_name}"
        layer = QgsVectorLayer(uri, layer_name, "memory")
        self.assertTrue(layer.isValid())
        return layer

    def test_set_renderer_filter(self):
        """
        Test set_renderer_filter.
        """
        # --- Scenario 1: Input layer has QgsRuleBasedRenderer ---

        # Case 1.1: rule_count > 1 (more than one rule)
        layer1_1 = self.create_test_layer("layer1_1")
        rule1 = QgsRuleBasedRenderer.Rule(QgsSymbol.defaultSymbol(layer1_1.geometryType()), filterExp="cat = 1")
        rule2 = QgsRuleBasedRenderer.Rule(QgsSymbol.defaultSymbol(layer1_1.geometryType()), filterExp="cat = 2")
        root_rule_1_1 = QgsRuleBasedRenderer.Rule(None)
        root_rule_1_1.appendChild(rule1.clone())
        root_rule_1_1.appendChild(rule2.clone())
        renderer1_1 = QgsRuleBasedRenderer(root_rule_1_1)
        layer1_1.setRenderer(renderer1_1)

        result = LayerUtils.set_renderer_filter(layer1_1, "new_filter = 1")
        self.assertFalse(result, "Should return False when renderer has multiple rules.")
        self.assertIsInstance(layer1_1.renderer(), QgsRuleBasedRenderer, "Renderer type should not change.")
        self.assertEqual(len(layer1_1.renderer().rootRule().children()), 2, "Rule count should remain unchanged.")

        # Case 1.2: rule_count == 1 and filter_string is provided
        layer1_2 = self.create_test_layer("layer1_2")
        initial_symbol_1_2 = QgsSymbol.defaultSymbol(layer1_2.geometryType())
        initial_symbol_1_2.setColor(QColor(120, 0, 0))
        rule_1_2 = QgsRuleBasedRenderer.Rule(initial_symbol_1_2.clone(), filterExp="initial_filter = 1")
        root_rule_1_2 = QgsRuleBasedRenderer.Rule(None)
        root_rule_1_2.appendChild(rule_1_2.clone())
        renderer1_2 = QgsRuleBasedRenderer(root_rule_1_2)
        layer1_2.setRenderer(renderer1_2)
        self.assertEqual(len(layer1_2.renderer().rootRule().children()), 1)

        new_filter_1_2 = "cat > 10"
        result = LayerUtils.set_renderer_filter(layer1_2, new_filter_1_2)
        self.assertTrue(result, "Should return True for single rule update.")
        self.assertIsInstance(layer1_2.renderer(), QgsRuleBasedRenderer, "Renderer should remain RuleBased.")
        self.assertEqual(len(layer1_2.renderer().rootRule().children()), 1, "Should still have one rule.")
        updated_rule = layer1_2.renderer().rootRule().children()[0]
        self.assertEqual(updated_rule.filterExpression(), new_filter_1_2)
        self.assertEqual(updated_rule.symbol().color(), QColor(120, 0, 0))

        # Case 1.3: rule_count == 1 and filter_string is None (downgrade to SingleSymbol)
        layer1_3 = self.create_test_layer("layer1_3")
        initial_symbol_1_3 = QgsSymbol.defaultSymbol(layer1_3.geometryType())
        initial_symbol_1_3.setColor(QColor(0, 120, 0))
        rule_1_3 = QgsRuleBasedRenderer.Rule(initial_symbol_1_3.clone(), filterExp="initial_filter = 1")
        root_rule_1_3 = QgsRuleBasedRenderer.Rule(None)
        root_rule_1_3.appendChild(rule_1_3.clone())
        renderer1_3 = QgsRuleBasedRenderer(root_rule_1_3)
        layer1_3.setRenderer(renderer1_3)

        result = LayerUtils.set_renderer_filter(layer1_3, None)
        self.assertTrue(result, "Should return True for downgrade to single symbol.")
        self.assertIsInstance(layer1_3.renderer(), QgsSingleSymbolRenderer, "Renderer should be SingleSymbolRenderer.")
        self.assertEqual(layer1_3.renderer().symbol().color(), QColor(0, 120, 0))

        # Case 1.3b: rule_count == 1 and filter_string is empty "" (downgrade to SingleSymbol)
        layer1_3b = self.create_test_layer("layer1_3b")
        initial_symbol_1_3b = QgsSymbol.defaultSymbol(layer1_3b.geometryType())
        initial_symbol_1_3b.setColor(QColor(0, 0, 120))
        rule_1_3b = QgsRuleBasedRenderer.Rule(initial_symbol_1_3b.clone(), filterExp="initial_filter = 1")
        root_rule_1_3b = QgsRuleBasedRenderer.Rule(None)
        root_rule_1_3b.appendChild(rule_1_3b.clone())
        renderer1_3b = QgsRuleBasedRenderer(root_rule_1_3b)
        layer1_3b.setRenderer(renderer1_3b)

        result = LayerUtils.set_renderer_filter(layer1_3b, "")  # Empty string
        self.assertTrue(result, "Should return True for downgrade with empty filter.")
        self.assertIsInstance(layer1_3b.renderer(), QgsSingleSymbolRenderer, "Renderer should be SingleSymbolRenderer.")
        self.assertEqual(layer1_3b.renderer().symbol().color(), QColor(0, 0, 120))

        # --- Scenario 2: Input layer has QgsSingleSymbolRenderer ---

        # Case 2.1: filter_string is None (no change)
        layer2_1 = self.create_test_layer("layer2_1")
        initial_symbol_2_1 = QgsSymbol.defaultSymbol(layer2_1.geometryType())
        initial_symbol_2_1.setColor(QColor(120, 120, 0))
        renderer2_1 = QgsSingleSymbolRenderer(initial_symbol_2_1.clone())
        layer2_1.setRenderer(renderer2_1)

        result = LayerUtils.set_renderer_filter(layer2_1, None)
        self.assertTrue(result, "Should return True, no change needed.")
        self.assertIsInstance(layer2_1.renderer(), QgsSingleSymbolRenderer,
                              "Renderer should remain SingleSymbolRenderer.")
        self.assertEqual(layer2_1.renderer().symbol().color(), QColor(120, 120, 0))

        # Case 2.1b: filter_string is empty "" (no change)
        layer2_1b = self.create_test_layer("layer2_1b")
        initial_symbol_2_1b = QgsSymbol.defaultSymbol(layer2_1b.geometryType())
        initial_symbol_2_1b.setColor(QColor(0, 120, 120))
        renderer2_1b = QgsSingleSymbolRenderer(initial_symbol_2_1b.clone())
        layer2_1b.setRenderer(renderer2_1b)

        result = LayerUtils.set_renderer_filter(layer2_1b, "")
        self.assertTrue(result, "Should return True, no change needed with empty filter.")
        self.assertIsInstance(layer2_1b.renderer(), QgsSingleSymbolRenderer,
                              "Renderer should remain SingleSymbolRenderer.")
        self.assertEqual(layer2_1b.renderer().symbol().color(), QColor(0, 120, 120))

        # Case 2.2: filter_string is provided (upgrade to RuleBased)
        layer2_2 = self.create_test_layer("layer2_2")
        initial_symbol_2_2 = QgsSymbol.defaultSymbol(layer2_2.geometryType())
        initial_symbol_2_2.setColor(QColor(120, 123, 14))
        renderer2_2 = QgsSingleSymbolRenderer(initial_symbol_2_2.clone())
        layer2_2.setRenderer(renderer2_2)

        new_filter_2_2 = "cat < 5"
        result = LayerUtils.set_renderer_filter(layer2_2, new_filter_2_2)
        self.assertTrue(result, "Should return True for upgrade to RuleBased.")
        self.assertIsInstance(layer2_2.renderer(), QgsRuleBasedRenderer, "Renderer should be RuleBasedRenderer.")
        self.assertEqual(len(layer2_2.renderer().rootRule().children()), 1, "Should have one rule.")
        active_rule = layer2_2.renderer().rootRule().children()[0]
        self.assertEqual(active_rule.filterExpression(), new_filter_2_2, "Filter string should be set.")
        self.assertEqual(active_rule.symbol().color(), QColor(120, 123, 14))

        # --- Scenario 3: Input layer has other renderer type ---
        layer3_1 = self.create_test_layer("layer3_1")
        renderer3_1 = QgsCategorizedSymbolRenderer("cat")  # Example: Categorized renderer
        layer3_1.setRenderer(renderer3_1)
        self.assertIsInstance(layer3_1.renderer(), QgsCategorizedSymbolRenderer)

        result = LayerUtils.set_renderer_filter(layer3_1, "any_filter = 1")
        self.assertFalse(result, "Should return False for other (e.g., Categorized) renderer types.")
        self.assertIsInstance(layer3_1.renderer(), QgsCategorizedSymbolRenderer, "Renderer type should not change.")

        # --- Scenario 4: Edge Cases for QgsRuleBasedRenderer (0 rules) ---
        layer4_1 = self.create_test_layer("layer4_1")
        root_rule_4_1 = QgsRuleBasedRenderer.Rule(None)  # Empty root rule (0 child rules)
        renderer4_1 = QgsRuleBasedRenderer(root_rule_4_1)
        layer4_1.setRenderer(renderer4_1)
        self.assertEqual(len(layer4_1.renderer().rootRule().children()), 0)


if __name__ == "__main__":
    suite = unittest.makeSuite(TestLayerUtils)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)