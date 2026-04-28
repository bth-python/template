#!/usr/bin/env python3
"""
Tests for quiz execution (Krav 1) in kmom10 quiz project.

Fixture file uses the two questions from the spec:
  Q1: Geografi, correct=B, 3 points
  Q2: Historia, correct=C, 2 points
  Max points = 5

Input sequences (menu 1 = easy.txt):
  Both wrong (A, B):  ["1", "A", "B", "Andreas", "", "q"]  -> 0/5 (0.0%)
  Q1 wrong, Q2 right: ["1", "A", "C", "Andreas", "", "q"]  -> 2/5 (40.0%)
  Both right (B, C):  ["1", "B", "C", "Sara",    "", "q"]  -> 5/5 (100.0%)
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


class Test3QuizRun(ExamTestCase):
    """
    Tests that a quiz runs correctly end-to-end.
    Uses a fixture easy.txt with the two questions from the spec.
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

    @tags("quiz", "display")
    def test_a_shows_category(self):
        """
        Testar att frågans kategori visas under quizet.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "Geografi"
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("quiz", "display")
    def test_b_shows_question_number(self):
        """
        Testar att frågenumret visas (t.ex. '1' av '2').
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "2"
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("quiz", "points")
    def test_d_correct_answer_gives_full_points(self):
        """
        Testar att rätt svar ger frågans fulla poäng.
        Q2 (Historia): rätt svar C, värd 2 poäng -> ska visa 2/2.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "2/2"
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("quiz", "points")
    def test_e_wrong_answer_gives_zero_points(self):
        """
        Testar att fel svar ger 0 poäng.
        Q1 (Geografi): rätt svar B, värd 3 poäng. Svar A -> ska visa 0/3.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "0/3"
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("quiz", "validation")
    def test_f_invalid_answer_reprompts(self):
        """
        Testar att ett ogiltigt svar (E) leder till ny inmatning och inte kraschar.
        Programmet ska acceptera 'B' efter att 'E' avvisats.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        self._multi_arguments = ["1", "E", "B", "C", "Andreas", "", "q"]
        with patch("builtins.input", side_effect=self._multi_arguments):
            with patch("sys.stdout", new=StringIO()):
                main.main()

    @tags("quiz", "validation")
    def test_g_case_insensitive_answer(self):
        """
        Testar att svar är case-insensitive (gemener accepteras).
        Svar 'b' och 'c' ska behandlas som 'B' och 'C'.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "b", "c", "Sara", "", "q"]
        self._correct = "5/5"
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("quiz", "summary")
    def test_h_correct_count_in_summary(self):
        """
        Testar att slututskriften visar antal rätta svar (1/2).
        Q1 fel (A), Q2 rätt (C) -> 1/2 rätta svar.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "1/2"
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("quiz", "summary")
    def test_i_percentage_in_summary(self):
        """
        Testar att slututskriften visar poängprocent.
        2 av 5 möjliga poäng -> 40.0%.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i utskrift:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        self._multi_arguments = ["1", "A", "C", "Andreas", "", "q"]
        self._correct = "40.0"
        output = self.run_quiz(self._multi_arguments)
        self.assertIn(self._correct, output)

    @tags("quiz", "summary")
    def test_j_category_summary_shown(self):
        """
        Testar att kategorisammanfattningen visas i slututskriften.
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
        self.assertIn("Geografi", output)
        self.assertIn("Historia", output)

    @tags("quiz", "summary")
    def test_k_category_correct_count(self):
        """
        Testar att kategorisammanfattningen visar rätt antal per kategori.
        Geografi: 0/1, Historia: 1/1.
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
        self.assertIn("0/1", output)
        self.assertIn("1/1", output)

    @tags("quiz", "scores")
    def test_l_scores_file_written(self):
        """
        Testar att scores.txt skapas med rätt data efter ett quiz.
        Förväntar att filen innehåller spelarens namn och svårighetsgrad.
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
        self.run_quiz(self._multi_arguments)
        self.assertTrue(os.path.exists(scores_path), "scores.txt skapades inte")
        with open(scores_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Andreas", content)
        self.assertIn("easy", content)

    @tags("quiz", "scores")
    def test_m_scores_file_contains_percentage(self):
        """
        Testar att scores.txt innehåller korrekt poängprocent (40.0).
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
        self.run_quiz(self._multi_arguments)
        with open(scores_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("40.0", content)


    @tags("quiz", "menu")
    def test_o_menu_2_medium(self):
        """
        Testar att menyval 2 startar ett quiz med medium.txt.
        Resultatet sparas med svårighetsgrad 'medium'.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i scores.txt:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        # Write the same fixture as medium.txt
        medium_path = "questions/medium.txt"
        orig_medium = open(medium_path, encoding="utf-8").read() if os.path.exists(medium_path) else None
        with open(medium_path, "w", encoding="utf-8") as f:
            f.write(FIXTURE_CONTENT)
        scores_path = os.path.join(REPO_PATH, "scores.txt")
        if os.path.exists(scores_path):
            os.remove(scores_path)
        self._multi_arguments = ["2", "A", "C", "Andreas", "", "q"]
        self.run_quiz(self._multi_arguments)
        with open(scores_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("medium", content)
        if orig_medium is not None:
            with open(medium_path, "w", encoding="utf-8") as f:
                f.write(orig_medium)
        else:
            os.remove(medium_path)

    @tags("quiz", "menu")
    def test_p_menu_3_hard(self):
        """
        Testar att menyval 3 startar ett quiz med hard.txt.
        Resultatet sparas med svårighetsgrad 'hard'.
        Använder följande som input:
        {arguments}
        Förväntar att följande finns med i scores.txt:
        {correct}
        Fick följande:
        {student}
        """
        self.norepr = True
        # Write the same fixture as hard.txt
        hard_path = "questions/hard.txt"
        orig_hard = open(hard_path, encoding="utf-8").read() if os.path.exists(hard_path) else None
        with open(hard_path, "w", encoding="utf-8") as f:
            f.write(FIXTURE_CONTENT)
        scores_path = os.path.join(REPO_PATH, "scores.txt")
        if os.path.exists(scores_path):
            os.remove(scores_path)
        self._multi_arguments = ["3", "A", "C", "Andreas", "", "q"]
        self.run_quiz(self._multi_arguments)
        with open(scores_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("hard", content)
        if orig_hard is not None:
            with open(hard_path, "w", encoding="utf-8") as f:
                f.write(orig_hard)
        else:
            os.remove(hard_path)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
