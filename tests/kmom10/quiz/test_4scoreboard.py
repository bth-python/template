#!/usr/bin/env python3
"""
Tests for the scoreboard display (Krav 2) in kmom10 quiz project.

Instead of writing scores.txt directly, every test runs actual quizzes to
produce score entries and then verifies the scoreboard display.  This makes
the tests agnostic to the internal scores.txt format.

Fixture uses 2 questions:
  Q1: Geografi,  correct=B, 3 pts
  Q2: Historia,  correct=C, 2 pts   max = 5 pts

Possible results with this fixture:
  Both right  (B, C)         → 5/5 = 100.0 %
  Q1 right, Q2 wrong (B, B)  → 3/5 =  60.0 %
  Q1 wrong, Q2 right (A, C)  → 2/5 =  40.0 %
  Both wrong  (A, B)         → 0/5 =   0.0 %
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


class Test4Scoreboard(ExamTestCase):
    """
    Tests that the scoreboard groups by difficulty and sorts correctly.
    Quizzes are run to produce score entries; scores.txt is never written
    directly so the tests are independent of the file format.
    """

    link_to_assignment = "https://bth-python.github.io/kmom/kmom10/"

    @classmethod
    def setUpClass(cls):
        os.chdir(REPO_PATH)
        os.makedirs("questions", exist_ok=True)
        easy_path, hard_path = "questions/easy.txt", "questions/hard.txt"
        cls._orig_easy = open(easy_path, encoding="utf-8").read() if os.path.exists(easy_path) else None
        cls._orig_hard = open(hard_path, encoding="utf-8").read() if os.path.exists(hard_path) else None
        with open(easy_path, "w", encoding="utf-8") as f:
            f.write(FIXTURE_CONTENT)
        with open(hard_path, "w", encoding="utf-8") as f:
            f.write(FIXTURE_CONTENT)

    @classmethod
    def tearDownClass(cls):
        for attr, path in (("_orig_easy", "questions/easy.txt"), ("_orig_hard", "questions/hard.txt")):
            orig = getattr(cls, attr)
            if orig is not None:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(orig)
            else:
                try:
                    os.remove(path)
                except FileNotFoundError:
                    pass
        try:
            os.remove("scores.txt")
        except FileNotFoundError:
            pass

    def clear_scores(self):
        try:
            os.remove("scores.txt")
        except FileNotFoundError:
            pass

    def run_quiz(self, inp):
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                main.main()
                return fake_out.getvalue()

    def run_scoreboard(self):
        with patch("builtins.input", side_effect=["4", "", "q"]):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                main.main()
                return fake_out.getvalue()

    @tags("scoreboard")
    def test_a_shows_easy_group(self):
        """
        Testar att topplistan visar gruppen 'easy'.
        Kör ett quiz med svårighetsgrad easy, öppnar sedan topplistan.
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._correct = "easy"
        self.clear_scores()
        self.run_quiz(["1", "A", "C", "Andreas", "", "q"])
        output = self.run_scoreboard()
        self.assertIn(self._correct, output)

    @tags("scoreboard")
    def test_b_shows_hard_group(self):
        """
        Testar att topplistan visar gruppen 'hard'.
        Kör ett quiz med svårighetsgrad hard, öppnar sedan topplistan.
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._correct = "hard"
        self.clear_scores()
        self.run_quiz(["3", "A", "C", "Sara", "", "q"])
        output = self.run_scoreboard()
        self.assertIn(self._correct, output)

    @tags("scoreboard")
    def test_c_shows_all_names(self):
        """
        Testar att topplistan visar alla sparade namn.
        Kör två quizar (Andreas 40.0%, Sara 0.0%), öppnar sedan topplistan.
        Förväntar att 'Andreas' och 'Sara' finns med i utskriften.
        Fick följande:
        {student}
        """
        self.norepr = True
        self.clear_scores()
        self.run_quiz(["1", "A", "C", "Andreas", "", "q"])  # 40.0 %
        self.run_quiz(["1", "A", "B", "Sara",    "", "q"])  #  0.0 %
        output = self.run_scoreboard()
        self.assertIn("Andreas", output)
        self.assertIn("Sara", output)

    @tags("scoreboard", "sort")
    def test_d_sorted_by_percentage_descending(self):
        """
        Testar att poster inom en grupp sorteras på poängprocent i fallande ordning.
        Andreas (40.0 %) ska komma före Sara (0.0 %) i gruppen 'easy'.
        Fick följande:
        {student}
        """
        self.norepr = True
        self.clear_scores()
        self.run_quiz(["1", "A", "C", "Andreas", "", "q"])  # 40.0 %
        self.run_quiz(["1", "A", "B", "Sara",    "", "q"])  #  0.0 %
        output = self.run_scoreboard()
        andreas_pos = output.find("Andreas")
        sara_pos = output.find("Sara")
        self.assertTrue(
            andreas_pos < sara_pos,
            ["Andreas (40.0%) borde komma före Sara (0.0%) i gruppen easy",
             f"Andreas pos: {andreas_pos}, Sara pos: {sara_pos}"],
        )

    @tags("scoreboard", "sort")
    def test_e_sorted_by_time_for_equal_percentage(self):
        """
        Testar att poster med samma poängprocent sorteras på tid (snabbast först).
        Bob (~20 s) ska komma före Alice (~30 s) när båda har 40.0 %.
        time.time() mockas för att ge deterministiska tidsvärden.
        Fick följande:
        {student}
        """
        self.norepr = True
        self.clear_scores()
        # Bob answers in ~20 s total; Alice answers in ~30 s total.
        # Extra values guard against implementations that call time.time() more
        # than once per question boundary.
        bob_times = [0.0, 0.0, 10.0, 10.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
        alice_times = [0.0, 0.0, 15.0, 15.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0]
        with patch("time.time", side_effect=bob_times):
            self.run_quiz(["1", "A", "C", "Bob",   "", "q"])  # 40.0 %, ~20 s
        with patch("time.time", side_effect=alice_times):
            self.run_quiz(["1", "A", "C", "Alice", "", "q"])  # 40.0 %, ~30 s
        output = self.run_scoreboard()
        bob_pos = output.find("Bob")
        alice_pos = output.find("Alice")
        self.assertTrue(
            bob_pos < alice_pos,
            ["Bob (~20s) borde komma före Alice (~30s) när procenttalet är lika",
             f"Bob pos: {bob_pos}, Alice pos: {alice_pos}"],
        )

    @tags("scoreboard")
    def test_f_shows_percentage_values(self):
        """
        Testar att poängprocent visas i topplistan.
        Andreas → 40.0 %, Sara → 100.0 %.
        Förväntar att '40.0' och '100.0' finns med i utskriften.
        Fick följande:
        {student}
        """
        self.norepr = True
        self.clear_scores()
        self.run_quiz(["1", "A", "C", "Andreas", "", "q"])  # 40.0 %
        self.run_quiz(["1", "B", "C", "Sara",    "", "q"])  # 100.0 %
        output = self.run_scoreboard()
        self.assertIn("40.0", output)
        self.assertIn("100.0", output)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
