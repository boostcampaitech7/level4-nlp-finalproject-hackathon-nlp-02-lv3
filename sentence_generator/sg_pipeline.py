# -*- coding: utf-8 -*-
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
from modules_common.completion_executor import CompletionExecutor
from modules_common.load_config import load_config
from sentence_generator.modules_sg.response_handler import handle_response
from sentence_generator.modules_sg.result_processor import process_result
from sentence_generator.modules_sg.sentence_generate import run_sg


config_api = load_config("../config/config_api.yaml")
config_eval = load_config("../config/config_sg_eval.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]


def run_sg_eval(original_text, generated_text):
    completion_executor = CompletionExecutor(
        host=COMPLETION_HOST_URL,
        api_key=API_KEY,
        request_id=REQUEST_ID,
    )
    preset_text = [
        {
            "role": config_eval["sg_eval_LLM"]["preset_text"]["system"]["role"],
            "content": config_eval["sg_eval_LLM"]["preset_text"]["system"]["content"],
        },
        {
            "role": config_eval["sg_eval_LLM"]["preset_text"]["user"]["role"],
            "content": config_eval["sg_eval_LLM"]["preset_text"]["user"]["content"]
            .replace("{original_text}", original_text)
            .replace("{generated_text}", generated_text),
        },
    ]
    request_data = {
        "messages": preset_text,
        "topP": config_eval["sg_eval_LLM"]["request_params"]["topP"],
        "topK": config_eval["sg_eval_LLM"]["request_params"]["topK"],
        "maxTokens": config_eval["sg_eval_LLM"]["request_params"]["maxTokens"],
        "temperature": config_eval["sg_eval_LLM"]["request_params"]["temperature"],
        # "repeatPenalty": config_eval["sg_eval_LLM"]["request_params"]["repeatPenalty"],
        "stopBefore": config_eval["sg_eval_LLM"]["request_params"]["stopBefore"],
        "includeAiFilters": config_eval["sg_eval_LLM"]["request_params"]["includeAiFilters"],
        "seed": config_eval["sg_eval_LLM"]["request_params"]["seed"],
    }

    response_data = completion_executor.execute(request_data)

    if response_data:
        logger.info("✅ 모델 응답 수신 완료")
    else:
        logger.warning("⚠️ 모델 응답 없음")

    result = handle_response(response_data)

    return process_result(result)


if __name__ == "__main__":
    original_text, generated_text = run_sg()
    sum_scores, sum_proba_scores = run_sg_eval(original_text, generated_text)
