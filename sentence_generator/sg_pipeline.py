# -*- coding: utf-8 -*-
import os
import sys
import time


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from loguru import logger
from sentence_generator.modules_sg.sentence_generate import run_sg
from sentence_generator.modules_sg.sentence_generate_eval import run_sg_eval


def generate_n_sentences(n, threshold_proba_score, threshold_correctness):
    """
    문장을 생성하고 평가하여 일정 점수 이상일 경우 리스트에 추가하는 함수.
    """
    generated_texts = []
    while len(generated_texts) < n:
        original_text, generated_text = run_sg()
        if not generated_text:
            time.sleep(5)
            continue

        sum_scores, proba_score, sum_proba_scores = run_sg_eval(original_text, generated_text)
        if (
            sum_proba_scores is not None
            and sum_proba_scores >= threshold_proba_score
            and proba_score[0] >= threshold_correctness
        ):
            generated_texts.append(generated_text.replace("\n", " "))
        else:
            logger.warning("Score below threshold. Retrying...")
            time.sleep(5)

    return generated_texts


if __name__ == "__main__":
    generated_texts = generate_n_sentences(1, 30, 7)
    print(generated_texts)
