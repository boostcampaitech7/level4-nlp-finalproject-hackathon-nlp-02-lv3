# -*- coding: utf-8 -*-
import json
import re

from loguru import logger
import requests
import yaml


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


config = load_config("../config/config_nlg_eval.yaml")

API_KEY = config["API"]["API_KEY"]
REQUEST_ID = config["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config["API"]["HOST_URL"]


class CompletionExecutor:
    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            "Authorization": self._api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }

        final_content = ""
        try:
            with requests.post(
                self._host + "/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=completion_request,
                stream=True,
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        # print("Received Line:", decoded_line)  # 디버깅용 출력
                        if decoded_line.startswith("data:"):
                            try:
                                data = json.loads(decoded_line[5:])
                                if "message" in data and "content" in data["message"]:
                                    final_content = data["message"]["content"]
                            except json.JSONDecodeError:
                                continue
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        return final_content


def process_response(content_result):
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


def calculate_weighted_score(probabilities):
    """
    점수 확률 분포를 받아 가중합 점수를 계산.
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


if __name__ == "__main__":
    original_text = """
    """
    generated_text = """
        """

    preset_text = [
        {
            "role": config["nlg_eval_LLM"]["preset_text"]["system"]["role"],
            "content": config["nlg_eval_LLM"]["preset_text"]["system"]["content"],
        },
        {
            "role": config["nlg_eval_LLM"]["preset_text"]["user"]["role"],
            "content": config["nlg_eval_LLM"]["preset_text"]["user"]["content"]
            .replace("{original_text}", original_text)
            .replace("{generated_text}", generated_text),
        },
    ]
    request_data = {
        "messages": preset_text,
        "topP": config["nlg_eval_LLM"]["request_params"]["topP"],
        "topK": config["nlg_eval_LLM"]["request_params"]["topK"],
        "maxTokens": config["nlg_eval_LLM"]["request_params"]["maxTokens"],
        "temperature": config["nlg_eval_LLM"]["request_params"]["temperature"],
        # "repeatPenalty": config["nlg_eval_LLM"]["request_params"]["repeatPenalty"],
        "stopBefore": config["nlg_eval_LLM"]["request_params"]["stopBefore"],
        "includeAiFilters": config["nlg_eval_LLM"]["request_params"]["includeAiFilters"],
        "seed": config["nlg_eval_LLM"]["request_params"]["seed"],
    }

    completion_executor = CompletionExecutor(
        host=COMPLETION_HOST_URL,
        api_key=API_KEY,
        request_id=REQUEST_ID,
    )

    response_data = completion_executor.execute(request_data)
    result = process_response(response_data)

    if result["content"]:
        logger.info(f"Scores: {result['scores']}")
        logger.info(f"Total Score: {result['total_score']}")
        # logger.info(f"Full Content:\n{result['content']}")

        weighted_scores = extract_probabilities_and_calculate_weighted_score(result["content"])
        # print("Weighted Scores:\n", weighted_scores)
        proba_score = []
        total_proba_score = 0
        for criterion, data in weighted_scores.items():
            # print(f"{criterion} - Weighted Score: {data['weighted_score']}")
            # print(f"  Probabilities: {data['probabilities']}")
            proba_score.append(data["weighted_score"])
        total_proba_score = sum(proba_score)
        logger.info(f"Probability Score: {proba_score}")
        logger.info(f"Total Probability Score: {total_proba_score}")

    else:
        logger.error("Failed to retrieve valid content from response.")
