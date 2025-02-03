# -*- coding: utf-8 -*-
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules_common.completion_executor import CompletionExecutor
from modules_common.load_config import load_config


config_api = load_config("../config/config_api.yaml")
config = load_config("../config/config_sg.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]


if __name__ == "__main__":
    completion_executor = CompletionExecutor(
        host=COMPLETION_HOST_URL,
        api_key=API_KEY,
        request_id=REQUEST_ID,
    )

    original_text = """
"""

    preset_text = [
        {
            "role": config["sg_LLM"]["preset_text"]["system"]["role"],
            "content": config["sg_LLM"]["preset_text"]["system"]["content"],
        },
        {
            "role": config["sg_LLM"]["preset_text"]["user"]["role"],
            "content": config["sg_LLM"]["preset_text"]["user"]["content"].replace("{original_text}", original_text),
        },
    ]

    request_data = {
        "messages": preset_text,
        "topP": config["sg_LLM"]["request_params"]["topP"],
        "topK": config["sg_LLM"]["request_params"]["topK"],
        "maxTokens": config["sg_LLM"]["request_params"]["maxTokens"],
        "temperature": config["sg_LLM"]["request_params"]["temperature"],
        # "repeatPenalty": config["sg_LLM"]["request_params"]["repeatPenalty"],
        "stopBefore": config["sg_LLM"]["request_params"]["stopBefore"],
        "includeAiFilters": config["sg_LLM"]["request_params"]["includeAiFilters"],
        "seed": config["sg_LLM"]["request_params"]["seed"],
    }

    response_data = completion_executor.execute(request_data)
    print(response_data)
