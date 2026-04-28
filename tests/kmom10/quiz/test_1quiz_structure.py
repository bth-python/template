#!/usr/bin/env python3
"""
Structure tests for kmom10 quiz project.
"""

import os
import unittest
from io import StringIO
from unittest import TextTestRunner
from unittest.mock import patch

from tester import (ExamTestCase, ExamTestResult, import_module,
                    setup_and_get_repo_path, tags)

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = setup_and_get_repo_path(FILE_DIR)


class Test1Structure(ExamTestCase):
    """
    Checks that required files and functions exist.
    """

    link_to_assignment = "https://bth-python.github.io/kmom/kmom10/"

    @tags("struct")
    def test_1_file_main_py_exists(self):
        """
        Testerna hittar inte filen 'main.py'.
        """
        with patch("builtins.input", side_effect=[]):
            with patch("sys.stdout", new=StringIO()):
                try:
                    self.assertModule("main", REPO_PATH)
                except StopIteration:
                    self.assertTrue(True)

    @tags("struct")
    def test_2_main_has_main_function(self):
        """
        Testerna hittar inte funktionen 'main' i filen 'main.py'.
        """
        with patch("builtins.input", side_effect=["q"]):
            with patch("sys.stdout", new=StringIO()):
                try:
                    main = import_module(REPO_PATH, "main")
                    self.assertAttribute(main, "main")
                except StopIteration:
                    self.assertTrue(True)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
