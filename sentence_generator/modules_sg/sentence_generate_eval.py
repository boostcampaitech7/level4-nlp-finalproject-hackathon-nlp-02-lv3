# -*- coding: utf-8 -*-
import os
import sys
import time


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
from modules_common.completion_executor import CompletionExecutor
from modules_common.load_config import load_config
from sentence_generator.modules_sg.response_handler import handle_response
from sentence_generator.modules_sg.result_processor import process_result


config_api = load_config("../config/config_api.yaml")
config = load_config("../config/config_sg_eval.yaml")

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
            "role": config["sg_eval_LLM"]["preset_text"]["system"]["role"],
            "content": config["sg_eval_LLM"]["preset_text"]["system"]["content"],
        },
        {
            "role": config["sg_eval_LLM"]["preset_text"]["user"]["role"],
            "content": config["sg_eval_LLM"]["preset_text"]["user"]["content"]
            .replace("{original_text}", original_text)
            .replace("{generated_text}", generated_text),
        },
    ]
    request_data = {
        "messages": preset_text,
        "topP": config["sg_eval_LLM"]["request_params"]["topP"],
        "topK": config["sg_eval_LLM"]["request_params"]["topK"],
        "maxTokens": config["sg_eval_LLM"]["request_params"]["maxTokens"],
        "temperature": config["sg_eval_LLM"]["request_params"]["temperature"],
        # "repeatPenalty": config["sg_eval_LLM"]["request_params"]["repeatPenalty"],
        "stopBefore": config["sg_eval_LLM"]["request_params"]["stopBefore"],
        "includeAiFilters": config["sg_eval_LLM"]["request_params"]["includeAiFilters"],
        "seed": config["sg_eval_LLM"]["request_params"]["seed"],
    }

    response_data = None
    retry_count = 0
    max_retries = 100

    while retry_count < max_retries:
        response_data = completion_executor.execute(request_data)

        if response_data:
            logger.info("✅ 모델 응답 수신 완료")
            break

        retry_count += 1
        logger.warning(f"⚠️ 모델 응답 없음. {retry_count}번째 재시도 중...")
        time.sleep(5)

    if response_data is None:
        logger.error("❌ 최대 재시도 횟수를 초과하여 응답을 받지 못했습니다.")
        return None

    result = handle_response(response_data)

    return process_result(result)
