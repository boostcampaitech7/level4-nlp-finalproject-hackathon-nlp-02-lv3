# -*- coding: utf-8 -*-
import os
import sys
import time

from loguru import logger
import pandas as pd
from tqdm import tqdm


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules_common.completion_executor import CompletionExecutor
from modules_common.load_config import load_config


config_api = load_config("../config/config_api.yaml")
config = load_config("../config/config_sg.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]


def process_requests(
    completion_executor,
    request_data,
    output_file_path,
    max_requests,
):
    successful_requests = 0

    with tqdm(total=max_requests, desc="Processing Requests") as pbar:
        while successful_requests < max_requests:
            response_data = completion_executor.execute(request_data)

            if response_data:
                response_data = response_data.replace("\n", " ")
                new_data = {
                    "Execution": [successful_requests + 1],
                    "Response": [response_data],
                }

                try:
                    existing_df = pd.read_csv(output_file_path)
                    new_df = pd.DataFrame(new_data)
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                except FileNotFoundError:
                    updated_df = pd.DataFrame(new_data)

                updated_df.to_csv(output_file_path, index=False)
                successful_requests += 1
                pbar.update(1)
            else:
                logger.error("Failed to retrieve valid content from response.")
                time.sleep(5)


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

    process_requests(completion_executor, request_data, "ai_safety.csv", 100)
