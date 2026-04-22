#!/usr/bin/env python3
"""
Contains testcases for the individual examination.
"""

import os
import sys
import unittest
from io import StringIO
from unittest import TextTestRunner
from unittest.mock import patch

from tester import (ExamTestCase, ExamTestResult, find_path_to_assignment,
                    import_module, setup_and_get_repo_path, tags)

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = setup_and_get_repo_path(FILE_DIR)

# Path to file and basename of the file to import
# convert = import_module(REPO_PATH, "convert") # Has inputs, use in check_print


class Test3ConvertErrors(ExamTestCase):
    """
    Each assignment has 1 testcase with multiple asserts.
    The different asserts https://docs.python.org/3.6/library/unittest.html#test-cases
    """



    def get_output_from_program(self, inp):
        """
        One function for testing print input functions
        """
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                try:
                    import_module(REPO_PATH, "convert")
                except SystemExit:
                    pass
                return fake_out.getvalue()

    @tags("error")
    def test_a_value_not_int(self):
        """
        Testar skicka in sträng värde som input. Kollar att felhantering sker.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._argument = "inte int"
        output_from_program = self.get_output_from_program([self._argument])
        self.assertIn("Invalid value", output_from_program)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
