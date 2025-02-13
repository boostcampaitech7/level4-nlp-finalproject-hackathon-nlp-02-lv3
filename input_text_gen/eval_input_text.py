import json
import time

from loguru import logger
import requests
import yaml


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


config_api = load_config("../config/config_api.yaml")
config_eval_input_text = load_config("../config/config_eval_input_text.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]


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
            self._host + "/serviceapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=True,
        ) as r:
            if r.status_code != 200:
                logger.warning(f"API 요청 실패: 상태 코드 {r.status_code}")
                return None, r.status_code
                # return None

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
                        return content, r.status_code

                except json.JSONDecodeError:  # JSON 문자열이 아닌 요소들은 무시
                    continue

        return None, 200


completion_executor = CompletionExecutor(
    host=f"{COMPLETION_HOST_URL}", api_key=f"{API_KEY}", request_id=f"{REQUEST_ID}"
)


def Eval_Input_Text(tcontent, input_text):
    logger.info("생성된 Input_text 평가 중..")
    preset_text = [
        {
            "role": config_eval_input_text["Eval_input_text_LLM"]["preset_text"]["system"]["role"],
            "content": config_eval_input_text["Eval_input_text_LLM"]["preset_text"]["system"]["content"],
        },
        {
            "role": config_eval_input_text["Eval_input_text_LLM"]["preset_text"]["user"]["role"],
            "content": f"소설 텍스트: \n{tcontent}\nInput_text:\n{input_text}",
        },
    ]

    request_data = {
        "messages": preset_text,
        "topP": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["topP"],
        "topK": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["topK"],
        "maxTokens": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["maxTokens"],
        "temperature": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["temperature"],
        "repeatPenalty": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["repeatPenalty"],
        "stopBefore": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["stopBefore"],
        "includeAiFilters": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["includeAiFilters"],
        "seed": config_eval_input_text["Eval_input_text_LLM"]["request_params"]["seed"],
    }

    retry_count = 0
    max_retries = 3
    generated_content = None
    last_status_code = None

    while retry_count < max_retries:
        try:
            generated_content, status_code = completion_executor.execute(request_data)
            last_status_code = status_code
            if generated_content:
                logger.info(f"생성된 Input_text 평가 결과:\n {generated_content}...\n")
                break
            else:
                warning_message = f"평가 실패 (상태 코드: {status_code}), 재시도 중..."
                logger.warning(f"{warning_message} ({retry_count+1}/{max_retries})\n")
                time.sleep(3)  # 약간 텀을 두고 다시 텍스트 생성을 시도해보면 생성하지 못했던것도 잘 생성하기도 함.

        except Exception as e:
            logger.error(f"텍스트 생성 중 오류 발생: {str(e)}\n")

        retry_count += 1

        if not generated_content:
            logger.error(f"Input_text 평가 실패 (최종 상태 코드: {last_status_code})")
            continue  # Translation 과정 건너뛰기용
