"""
GUI Utils Test.
"""

import unittest
from ..gui.gui_utils import GuiUtils
from .utilities import get_qgis_app


from .qcity_test_base import QCityTestBase

QGIS_APP = get_qgis_app()


class GuiUtilsTest(QCityTestBase):
    """Test GuiUtils work."""

    def testGetIcon(self):
        """
        Tests get_icon
        """
        self.assertFalse(GuiUtils.get_icon("plugin.svg").isNull())
        self.assertTrue(GuiUtils.get_icon("not_an_icon.svg").isNull())

    def testGetUiFilePath(self):
        """
        Tests get_ui_file_path svg path
        """
        self.assertTrue(GuiUtils.get_ui_file_path("dockwidget_main.ui"))
        self.assertIn(
            "dockwidget_main.ui", GuiUtils.get_ui_file_path("dockwidget_main.ui")
        )
        self.assertFalse(GuiUtils.get_ui_file_path("not_a_form.ui"))

    def testGetIconSvg(self):
        """
        Tests get_icon svg path
        """
        self.assertTrue(GuiUtils.get_icon_svg("plugin.svg"))
        self.assertIn("plugin.svg", GuiUtils.get_icon_svg("plugin.svg"))
        self.assertFalse(GuiUtils.get_icon_svg("not_an_icon.svg"))


if __name__ == "__main__":
    suite = unittest.makeSuite(GuiUtilsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
