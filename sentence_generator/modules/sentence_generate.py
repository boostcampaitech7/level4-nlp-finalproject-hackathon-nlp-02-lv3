# -*- coding: utf-8 -*-
import os
import sys

from loguru import logger


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from completion_executor import CompletionExecutor
from execute_with_retries import execute_with_retries
from load_config import load_config


config_api = load_config("../config/config_api.yaml")
config = load_config("../config/config_sg.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]


def run_sg(original_text, index):
    llm_config_key = f"sg_LLM{index % 3}"

    llm_config = config.get(llm_config_key, config["sg_LLM0"])
    completion_executor = CompletionExecutor(
        host=COMPLETION_HOST_URL,
        api_key=API_KEY,
        request_id=REQUEST_ID,
    )

    preset_text = [
        {
            "role": llm_config["preset_text"]["system"]["role"],
            "content": llm_config["preset_text"]["system"]["content"],
        },
        {
            "role": llm_config["preset_text"]["user"]["role"],
            "content": llm_config["preset_text"]["user"]["content"].replace("{original_text}", original_text),
        },
    ]

    request_data = {
        "messages": preset_text,
        "topP": config["request_params"]["topP"],
        "topK": config["request_params"]["topK"],
        "maxTokens": config["request_params"]["maxTokens"],
        "temperature": config["request_params"]["temperature"],
        # "repeatPenalty": config["request_params"]["repeatPenalty"],
        "stopBefore": config["request_params"]["stopBefore"],
        "includeAiFilters": config["request_params"]["includeAiFilters"],
        "seed": config["request_params"]["seed"],
    }

    response_data = execute_with_retries(completion_executor, request_data)

    if response_data is None:
        return None

    logger.info(response_data)
    return response_data
