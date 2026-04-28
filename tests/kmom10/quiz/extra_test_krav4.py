#!/usr/bin/env python3
"""
Tests for Krav 4 (valfritt): Quiz-sammanfattning.

The summary is shown after the final result but before the name prompt.
It shows one row per question with: truncated question text, user answer,
correct answer, and points earned/max.

Q1: "Vad är Sveriges huvudstad?" (26 chars, not truncated)
    User: A, Correct: B, Points: 0/3
Q2: "Vilket år bildades Kungariket Sverige officiellt?" (49 chars, truncated to 30 + ...)
    User: C, Correct: C, Points: 2/2
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

FIXTURE_CONTENT = """\
Geografi
Vad är Sveriges huvudstad?
Oslo
Stockholm
Köpenhamn
Helsinki
B
3
Stockholm ligger vid Mälaren och Östersjön.

Historia
Vilket år bildades Kungariket Sverige officiellt?
829
1000
972
1523
C
2
Det skedde under 900-talet.
"""


class TestKrav4Summary(ExamTestCase):
    """
    Tests for the optional quiz summary (Krav 4).
    """

    link_to_assignment = "https://bth-python.github.io/kmom/kmom10/"

    @classmethod
    def setUpClass(cls):
        os.chdir(REPO_PATH)
        os.makedirs("questions", exist_ok=True)
        easy_path = "questions/easy.txt"
        cls._orig_easy = open(easy_path, encoding="utf-8").read() if os.path.exists(easy_path) else None
        with open(easy_path, "w", encoding="utf-8") as f:
            f.write(FIXTURE_CONTENT)

    @classmethod
    def tearDownClass(cls):
        easy_path = "questions/easy.txt"
        if cls._orig_easy is not None:
            with open(easy_path, "w", encoding="utf-8") as f:
                f.write(cls._orig_easy)
        else:
            try:
                os.remove(easy_path)
            except FileNotFoundError:
                pass
        try:
            os.remove("scores.txt")
        except FileNotFoundError:
            pass

    def run_quiz(self, inp):
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                main.main()
                return fake_out.getvalue()



    @tags("krav4", "summary")
    def test_c_points_per_question_shown(self):
        """
        Testar att poäng per fråga visas i sammanfattningen.
        Fråga 1: 0/3, Fråga 2: 2/2.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        output = self.run_quiz(self._multi_arguments)
        self.assertIn("0/3", output)
        self.assertIn("2/2", output)

    @tags("krav4", "truncation")
    def test_d_long_question_truncated(self):
        """
        Testar att frågetext längre än 30 tecken trunkeras med '...'.
        'Vilket år bildades Kungariket Sverige officiellt?' är 49 tecken och ska trunkeras.
        Trunkerad text börjar med 'Vilket år bildades Kungarik'.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "..."
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("krav4", "truncation")
    def test_e_truncated_text_starts_correctly(self):
        """
        Testar att trunkerad text börjar med de första 30 tecknen av frågetexten.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        # First 30 chars of Q2 text
        self._correct = "Vilket år bildades Kungariket "
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
