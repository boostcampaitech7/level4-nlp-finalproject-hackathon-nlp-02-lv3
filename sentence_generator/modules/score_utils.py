import re

from loguru import logger


def calculate_weighted_score(probabilities):
    """
    점수 확률 분포를 받아 가중합 점수를 계산합니다.
    :param probabilities: 점수와 확률이 포함된 딕셔너리 (예: {1: 0.1, 2: 0.2, ...})
    :return: 가중합 점수 (소수점 포함)
    """
    weighted_sum = sum(int(score) * prob for score, prob in probabilities.items())
    return round(weighted_sum, 2)


def extract_probabilities_and_calculate_weighted_score(content):
    """
    결과 데이터에서 확률 분포를 추출하고 가중합 점수를 계산합니다.
    :param content: LLM 응답 데이터
    :return: 각 기준의 가중합 점수 딕셔너리
    """
    scores_data = {}

    pattern = r"- (\w+/)?(\w+)\s*:\s*(\d+)\s*- 확률분포\s*:\s*\{([^\}]+)\}"

    matches = re.finditer(pattern, content)

    for match in matches:
        category = match.group(2)
        raw_probabilities = match.group(4)

        try:
            probabilities = {
                int(k.strip()): float(v.strip()) for k, v in (item.split(":") for item in raw_probabilities.split(","))
            }
        except ValueError as e:
            logger.error(f"Error parsing probabilities: {raw_probabilities}. Error: {e}")
            continue

        # 가중합 계산
        weighted_score = calculate_weighted_score(probabilities)

        # 결과 저장
        scores_data[category] = {
            "weighted_score": weighted_score,
            "probabilities": probabilities,
        }

    return scores_data
