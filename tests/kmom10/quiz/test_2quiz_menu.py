#!/usr/bin/env python3
"""
Tests for menu navigation in kmom10 quiz project.
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

main = import_module(REPO_PATH, "main")


class Test2Menu(ExamTestCase):
    """
    Tests for the main menu: quit, invalid input, menu choices display.
    """

    link_to_assignment = "https://bth-python.github.io/kmom/kmom10/"

    @classmethod
    def setUpClass(cls):
        os.chdir(REPO_PATH)

    def check_no_crash(self, inp):
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()):
                main.main()

    def check_output(self, inp):
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                main.main()
                return fake_out.getvalue()

    @tags("menu")
    def test_a_quit(self):
        """
        Testar att avsluta med menyval 'q'.
        Kollar att programmet inte kraschar.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        self._multi_arguments = ["q"]
        self.check_no_crash(self._multi_arguments)

    @tags("menu")
    def test_b_invalid_menu_no_crash(self):
        """
        Testar att ett ogiltigt menyval inte kraschar programmet.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        self._multi_arguments = ["x", "q"]
        self.check_no_crash(self._multi_arguments)


    @tags("menu", "scoreboard")
    def test_f_scoreboard_missing_file_no_crash(self):
        """
        Testar att topplistan (menyval 4) inte kraschar om scores.txt saknas.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        self._multi_arguments = ["4", "", "q"]
        # Remove scores.txt if it exists to test the missing-file path
        scores_path = os.path.join(REPO_PATH, "scores.txt")
        existed = os.path.exists(scores_path)
        if existed:
            os.rename(scores_path, scores_path + ".bak")
        try:
            self.check_no_crash(self._multi_arguments)
        finally:
            if existed:
                os.rename(scores_path + ".bak", scores_path)

    @tags("menu", "scoreboard")
    def test_g_scoreboard_returns_to_menu(self):
        """
        Testar att programmet återgår till menyn efter att topplistan visats,
        och att man kan avsluta med 'q'.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        self._multi_arguments = ["4", "", "q"]
        self.check_no_crash(self._multi_arguments)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
