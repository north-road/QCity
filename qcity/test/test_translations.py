"""
Safe Translations Test.
"""

import unittest
import os
from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class SafeTranslationsTest(unittest.TestCase):
    """Test translations work."""

    def setUp(self):
        """Runs before each test."""
        if os.getenv("LANG"):
            del os.environ["LANG"]

    def tearDown(self):
        """Runs after each test."""
        if os.getenv("LANG"):
            del os.environ["LANG"]

    def test_qgis_translations(self):
        """Test that translations work."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        file_path = os.path.join(dir_path, "i18n", "af.qm")
        self.assertTrue(
            os.path.isfile(file_path),
            "%s is not a valid translation file or it does not exist" % file_path,
        )
        translator = QTranslator()
        translator.load(file_path)
        QCoreApplication.installTranslator(translator)

        expected_message = "Goeie more"
        real_message = QCoreApplication.translate("@default", "Good morning")
        self.assertEqual(real_message, expected_message)


if __name__ == "__main__":
    suite = unittest.makeSuite(SafeTranslationsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
