# -*- coding: utf-8 -*-
from loguru import logger
from modules import CompletionExecutor, extract_probabilities_and_calculate_weighted_score, handle_response, load_config


config_api = load_config("../config/config_api.yaml")
config = load_config("../config/config_sg_eval.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]

if __name__ == "__main__":
    original_text = """
    """
    generated_text = """
        """

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

    completion_executor = CompletionExecutor(
        host=COMPLETION_HOST_URL,
        api_key=API_KEY,
        request_id=REQUEST_ID,
    )

    response_data = completion_executor.execute(request_data)
    result = handle_response(response_data)

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
