# -*- coding: utf-8 -*-
import os
import sys

import pandas as pd


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

        eval_result = run_sg_eval(original_text, generated_text)

        sum_scores, proba_score, sum_proba_scores = eval_result

        if (
            sum_proba_scores is not None
            and sum_proba_scores >= threshold_proba_score
            and proba_score[0] >= threshold_correctness
        ):
            generated_texts.append(generated_text.replace("\n", " "))
        else:
            logger.warning("Score below threshold. Retrying...")

    return generated_texts


def save_generated_sentences(generated_texts, output_file_path):
    """
    생성된 문장을 CSV 파일에 저장하는 함수.
    """
    new_df = pd.DataFrame([{f"sentence{i + 1}": text for i, text in enumerate(generated_texts)}])

    try:
        existing_df = pd.read_csv(output_file_path)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    except FileNotFoundError:
        updated_df = pd.DataFrame(new_df)

    updated_df.to_csv(output_file_path, index=False)
    logger.info(f"Saved generated sentences to {output_file_path}")


def main():
    generated_texts = generate_n_sentences(5, 30, 7)
    print(generated_texts)
    save_generated_sentences(generated_texts, "sentence_generated.csv")


if __name__ == "__main__":
    main()
