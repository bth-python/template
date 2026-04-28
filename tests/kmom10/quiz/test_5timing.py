#!/usr/bin/env python3
"""
Tests for timing (Krav 3) in kmom10 quiz project.

time.time() is mocked to return deterministic values so tests check
the computed numbers in the output rather than relying on real elapsed time.

Mock sequence for a 2-question quiz:
  call 0: quiz start      -> 0.0   (total timer start)
  call 1: q1 display      -> 0.0   (q1 timer start)
  call 2: q1 answer given -> 4.32  (q1 timer end)  -> per-question time = 4.32
  call 3: q2 display      -> 4.32  (q2 timer start)
  call 4: q2 answer given -> 10.47 (q2 timer end)  -> per-question time = 6.15
                                                       total time = 10.47
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

# time.time() values: start, q1-start, q1-end, q2-start, q2-end
# (the exact number of calls depends on implementation; provide extra values)
TIME_VALUES = [0.0, 0.0, 4.32, 4.32, 10.47, 10.47, 10.47, 10.47]


class Test5Timing(ExamTestCase):
    """
    Tests that timing values appear in output (Krav 3).
    time.time() is mocked so computed durations are deterministic.
    """

    link_to_assignment = "https://bth-python.github.io/kmom/kmom10/"

    @classmethod
    def setUpClass(cls):
        os.chdir(REPO_PATH)
        os.makedirs("questions", exist_ok=True)
        with open("questions/easy.txt", "w", encoding="utf-8") as f:
            f.write(FIXTURE_CONTENT)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove("questions/easy.txt")
        except FileNotFoundError:
            pass
        try:
            os.remove("scores.txt")
        except FileNotFoundError:
            pass

    def run_quiz_timed(self, inp):
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                with patch("time.time", side_effect=TIME_VALUES):
                    main.main()
                    return fake_out.getvalue()

    @tags("timing")
    def test_a_per_question_time_shown(self):
        """
        Testar att tidmätning per fråga visas i utskriften.
        Med mockade tidsvärden ska '4.32' visas efter fråga 1.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "4.32"
        output = self.run_quiz_timed(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("timing")
    def test_b_total_time_shown_in_summary(self):
        """
        Testar att total tid visas i slututskriften.
        Med mockade tidsvärden ska '10.47' finnas i slututskriften.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "10.47"
        output = self.run_quiz_timed(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("timing")
    def test_c_total_time_in_scores_file(self):
        """
        Testar att total tid sparas i scores.txt.
        Med mockade tidsvärden ska '10.47' finnas i scores.txt.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i scores.txt:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        scores_path = os.path.join(REPO_PATH, "scores.txt")
        if os.path.exists(scores_path):
            os.remove(scores_path)
        self.run_quiz_timed(self._multi_arguments)
        with open(scores_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("10.47", content)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
