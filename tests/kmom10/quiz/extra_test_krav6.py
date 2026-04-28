#!/usr/bin/env python3
"""
Tests for Krav 6 (valfritt): Slumpmässigt quiz (Random quiz).

Menu option 5 lets users pick a number of random questions drawn from
all three files combined. The result is saved with difficulty 'random'.

Fixture: all three question files contain the spec's two questions each
(6 total), so requesting 2 questions is always satisfiable.
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

FIXTURE_EASY = """\
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

FIXTURE_MEDIUM = """\
Vetenskap
Vilket grundämne har kemiskt tecken O?
Guld
Syre
Ozon
Osmium
B
2
Det finns i luften vi andas.

Matematik
Vad är kvadratroten ur 144?
10
11
12
13
C
2
Det är ett litet tal.
"""

FIXTURE_HARD = """\
Litteratur
Vem skrev Hamlet?
Dickens
Shakespeare
Cervantes
Ibsen
B
3
Han levde på 1500-talet.

Musik
Hur många toner finns det i en oktav?
6
7
8
12
C
3
Det är fler än sju.
"""


class TestKrav6Random(ExamTestCase):
    """
    Tests for the optional random quiz feature (Krav 6).
    """

    link_to_assignment = "https://bth-python.github.io/kmom/kmom10/"

    @classmethod
    def setUpClass(cls):
        os.chdir(REPO_PATH)
        os.makedirs("questions", exist_ok=True)
        cls._orig_questions = {}
        for filename, content in (
            ("easy.txt", FIXTURE_EASY),
            ("medium.txt", FIXTURE_MEDIUM),
            ("hard.txt", FIXTURE_HARD),
        ):
            path = f"questions/{filename}"
            cls._orig_questions[filename] = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    @classmethod
    def tearDownClass(cls):
        for filename in ("easy.txt", "medium.txt", "hard.txt"):
            path = f"questions/{filename}"
            orig = cls._orig_questions.get(filename)
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

    def run_program(self, inp):
        with patch("builtins.input", side_effect=inp):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                main.main()
                return fake_out.getvalue()

    @tags("krav6", "random")
    def test_a_menu_5_no_crash(self):
        """
        Testar att menyval 5 finns och inte kraschar programmet.
        Begär 2 frågor, svarar A och C, anger namn, återgår till meny.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        # "5" = random quiz, "2" = number of questions, answer both, name, return, quit
        self._multi_arguments = ["5", "2", "A", "C", "Andreas", "", "q"]
        with patch("builtins.input", side_effect=self._multi_arguments):
            with patch("sys.stdout", new=StringIO()):
                main.main()

    @tags("krav6", "random")
    def test_b_random_difficulty_saved_in_scores(self):
        """
        Testar att svårighetsgraden 'random' sparas i scores.txt
        när quizet körs via menyval 5.
        Använder följande som input:
        {arguments}
        Förväntar att 'random' finns i scores.txt.
        Fick följande:
        {student}
        """
        self.norepr = True
        scores_path = os.path.join(REPO_PATH, "scores.txt")
        if os.path.exists(scores_path):
            os.remove(scores_path)
        self._multi_arguments = ["5", "2", "A", "C", "Andreas", "", "q"]
        self.run_program(self._multi_arguments)
        self.assertTrue(os.path.exists(scores_path), "scores.txt skapades inte")
        with open(scores_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("random", content)

    @tags("krav6", "random")
    def test_c_more_questions_than_available_no_crash(self):
        """
        Testar att programmet inte kraschar om användaren begär fler frågor
        än vad som finns tillgängligt.
        Totalt 6 unika frågor (2 per fil). Begär 100 -> ska köras med 6.
        Vi svarar med alternativ B eller C för alla 6 frågor.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        # 6 answers (enough for all available questions), then name and return
        answers = ["B", "C", "B", "C", "B", "C"]
        self._multi_arguments = ["5", "100"] + answers + ["Andreas", "", "q"]
        with patch("builtins.input", side_effect=self._multi_arguments):
            with patch("sys.stdout", new=StringIO()):
                main.main()

    @tags("krav6", "random")
    def test_d_no_duplicate_questions(self):
        """
        Testar att samma fråga inte förekommer mer än en gång i ett slumpmässigt quiz.
        Begär alla 6 unika frågor och kontrollerar att varje frågetext är unik i utskriften.
        Använder följande som input:
        {arguments}
        """
        self.norepr = True
        answers = ["B", "C", "B", "C", "B", "C"]
        self._multi_arguments = ["5", "6"] + answers + ["Andreas", "", "q"]
        output = self.run_program(self._multi_arguments)
        # Each unique question text should appear exactly once
        for q_text in [
            "Vad är Sveriges huvudstad?",
            "Vilket år bildades Kungariket Sverige officiellt?",
            "Vilket grundämne har kemiskt tecken O?",
        ]:
            self.assertIn(q_text, output)
            # Verify it only appears once by checking the text after removing the first occurrence
            first_pos = output.find(q_text)
            remaining = output[first_pos + len(q_text):]
            self.assertNotIn(q_text, remaining)


if __name__ == "__main__":
    runner = TextTestRunner(resultclass=ExamTestResult, verbosity=2)
    unittest.main(testRunner=runner, exit=False)
