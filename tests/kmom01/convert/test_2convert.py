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


class Test2Convert(ExamTestCase):
    """
    Each assignment has 1 testcase with multiple asserts.
    The different asserts https://docs.python.org/3.6/library/unittest.html#test-cases
    """

    link_to_assignment = "https://python-bth.github.io/laromaterial/uppgift/convert/"

    def get_output_from_program(self, inp):
        """
        One function for testing print input functions
        """
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                import_module(REPO_PATH, "convert")
                return fake_out.getvalue()

    @tags("example")
    def test_a_price_example(self):
        """
        Testar räkna ut pris efter rabatt med heltal som input.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._argument = "100"
        output_from_program = self.get_output_from_program([self._argument])
        self.assertIn("100 ", output_from_program)
        self.assertIn("108.0 ", output_from_program)

    @tags("positive")
    def test_b_price_positive(self):
        """
        Testar räkna ut pris efter rabatt med heltal som input.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._argument = "123"
        output_from_program = self.get_output_from_program([self._argument])
        self.assertIn("123 ", output_from_program)
        self.assertIn("135.6 ", output_from_program)

    @tags("zero")
    def test_c_price_zero(self):
        """
        Testar räkna ut pris efter rabatt med 0 som input.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._argument = "0"
        output_from_program = self.get_output_from_program([self._argument])
        self.assertIn("0 ", output_from_program)
        self.assertIn("-12.0 ", output_from_program)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
