# -*- coding: utf-8 -*-
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sentence_generator.modules_sg.sentence_generate import run_sg
from sentence_generator.modules_sg.sentence_generate_eval import run_sg_eval


if __name__ == "__main__":
    original_text, generated_text = run_sg()
    sum_scores, proba_score, sum_proba_scores = run_sg_eval(original_text, generated_text)
    print(sum_scores)
    print(proba_score)
    print(sum_proba_scores)
