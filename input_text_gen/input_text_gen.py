# -*- coding: utf-8 -*-
import json

from loguru import logger
import pandas as pd
import requests
import yaml


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


config = load_config("../config.yaml")

API_KEY = config["API"]["API_KEY"]
REQUEST_ID = config["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config["API"]["HOST_URL"]

fiction_df = pd.read_csv(config["Origin_fiction_dir"])
fiction_content = fiction_df["tcontent"]


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

        with requests.post(
            self._host + "/testapp/v1/chat-completions/HCX-003", headers=headers, json=completion_request, stream=True
        ) as r:
            lines = [line.decode("utf-8") for line in r.iter_lines() if line]
            for line in lines[-4:]:
                try:
                    # "data:"로 시작하는 부분 제거
                    if line.startswith("data:"):
                        line = line[len("data:") :]

                    # JSON 파싱
                    data = json.loads(line)

                    # JSON에서 "content" 추출
                    content = data.get("message", {}).get("content", None)
                    if content:
                        return content

                except json.JSONDecodeError:  # JSON 문자열이 아닌 요소들은 무시
                    continue


if __name__ == "__main__":
    completion_executor = CompletionExecutor(
        host=f"{COMPLETION_HOST_URL}", api_key=f"{API_KEY}", request_id=f"{REQUEST_ID}"
    )
    content_list = []

    # for fiction in fiction_content:
    for i in range(3):
        logger.info(f"{i+1}/{len(fiction_content)} Input_text 생성 중..")
        preset_text = [
            {
                "role": config["Input_text_gen_LLM"]["preset_text"]["system"]["role"],
                # content : content(KR), content(US) > 한국어 프롬프트로 전달, 영어 프롬프트로 전달
                "content": config["Input_text_gen_LLM"]["preset_text"]["system"]["content_KR"],
            },
            {"role": config["Input_text_gen_LLM"]["preset_text"]["user"]["role"], "content": f"{fiction_content[i]}"},
        ]

        request_data = {
            "messages": preset_text,
            "topP": config["Input_text_gen_LLM"]["request_params"]["topP"],
            "topK": config["Input_text_gen_LLM"]["request_params"]["topK"],
            "maxTokens": config["Input_text_gen_LLM"]["request_params"]["maxTokens"],
            "temperature": config["Input_text_gen_LLM"]["request_params"]["temperature"],
            "repeatPenalty": config["Input_text_gen_LLM"]["request_params"]["repeatPenalty"],
            "stopBefore": config["Input_text_gen_LLM"]["request_params"]["stopBefore"],
            "includeAiFilters": config["Input_text_gen_LLM"]["request_params"]["includeAiFilters"],
            "seed": config["Input_text_gen_LLM"]["request_params"]["seed"],
        }

        try:
            generated_content = completion_executor.execute(request_data)
            if generated_content:
                logger.info(f"텍스트 생성 성공:\n {generated_content[:50]}...\n")
            else:
                logger.warning(f"[{i+1}] 생성된 텍스트가 비어있음\n")
            content_list.append(generated_content)
        # content_list.append(completion_executor.execute(request_data))
        except Exception as e:
            logger.error(f"[{i+1}] 텍스트 생성 중 오류 발생: {str(e)}\n")
            content_list.append(None)

    logger.info("모든 Input_text 생성 완료.")
    fiction_prompt_df = pd.DataFrame({"musicgen_input_text": content_list})
    new_fiction_df = pd.concat([fiction_df, fiction_prompt_df], axis=1)
    new_fiction_df.to_csv(config["New_fiction_dir"], index=False)
