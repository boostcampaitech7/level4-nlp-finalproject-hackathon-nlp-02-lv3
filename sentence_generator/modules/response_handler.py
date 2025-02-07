# -*- coding: utf-8 -*-
import re

from loguru import logger


def handle_response(content_result):
    """
    모델 응답 데이터를 처리하여 점수와 총점을 추출합니다.
    :param content_result: LLM 응답 데이터
    :return: 점수 리스트, 총점, 원본 컨텐츠 딕셔너리
    """
    if not content_result:
        logger.warning("No valid content received.")
        return {"scores": [], "total_score": 0, "content": None}

    scores = []
    total_score = 0

    match = re.search(r"\[([0-9,\s]+)\]", content_result)
    if match:
        scores = list(map(int, match.group(1).split(",")))
        total_score = sum(scores)
    else:
        logger.warning("No valid score list found.")

    return {"scores": scores, "total_score": total_score, "content": content_result}
