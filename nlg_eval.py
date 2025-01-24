# -*- coding: utf-8 -*-
import configparser
import json
import re

from loguru import logger
import requests


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

        response_text = ""
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
                        response_text += decoded_line + "\n"
        except requests.exceptions.RequestException as e:
            logger.debug(f"Request failed: {e}")
        return response_text


def process_response(response_data):
    content_result = None
    scores = []
    total_score = 0

    lines = response_data.strip().split("\n")
    for i, line in enumerate(lines):
        if "event:result" in line:
            if i + 1 < len(lines) and lines[i + 1].startswith("data:"):
                data_line = lines[i + 1][5:]
                try:
                    result_data = json.loads(data_line)
                    content_result = result_data["message"]["content"]
                    break
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"Error processing line: {data_line}, Error: {e}")

    if content_result:
        match = re.search(r"\[([0-9,\s]+)\]", content_result)
        if match:
            scores = list(map(int, match.group(1).split(",")))
            total_score = sum(scores)
        else:
            logger.warning("No valid score list found.")
    else:
        logger.warning("No event:result data found.")
    return {
        "scores": scores,
        "total_score": total_score,
        "content": content_result,
    }


if __name__ == "__main__":
    original_text = """
    """
    generated_text = """
        """

    preset_text = [
        {
            "role": "system",
            "content": (
                "당신은 소설 원문과 생성된 문장을 비교하여 평가하는 전문가입니다. "
                "당신의 역할은 제공된 기준에 따라 생성 문장이 원문과 얼마나 잘 일치하며, "
                "내용을 매력적으로 표현했는지 평가하는 것입니다.\n\n"
                "당신의 배경은 다음과 같습니다:\n"
                "- 15년 경력의 문학 비평가로 현대 문학 작품의 주제와 상징 해석에 전문성을 보유.\n"
                "- 시나리오 작가로서 서사 구조와 창의적 표현을 평가하는 경험이 풍부.\n"
                "- 소설 덕후 출신으로 요약 및 핵심 내용 추출에 능숙.\n\n"
                "평가 기준은 다음과 같습니다:\n"
                "1. **충실성 (1-10)**: 생성 문장이 원문의 주제를 얼마나 잘 반영하는가.\n"
                "   - 생성 문장이 주제를 벗어나거나 다른 주제를 강조할 경우 점수를 낮게 부여하세요.\n"
                "   - 메시지가 흐려지거나 부정확하게 전달될 경우 점수를 낮게 부여하세요.\n"
                "   - 사건이 생략되거나 캐릭터 및 배경 설정이 변경될 경우 점수를 낮게 부여하세요.\n"
                "   - 내용이 과장되거나, 원문과 반대되는 의미를 전달할 경우 점수를 낮게 부여하세요.\n"
                "2. **세부 내용 반영도 (1-10)**: 생성 문장이 원문의 세부 내용을 얼마나 잘 반영하는가.\n"
                "   - 세부 내용이 모호하게 표현된 경우 점수를 낮게 부여하세요.\n"
                "   - 디테일이 잘못되었거나 왜곡된 경우 점수를 낮게 부여하세요.\n"
                "   - 불필요하거나 원문과 상충되는 세부 내용이 추가된 경우 점수를 낮게 부여하세요.\n"
                "3. **매력도/창의성 (1-10)**: 생성 문장이 원문보다 얼마나 매력적이고 창의적인가.\n"
                "4. **유창성/정확성 (1-10)**: 생성 문장이 문법적으로 정확하고 자연스러운가.\n"
                "5. **감정 전달력 (1-10)**: 생성 문장이 원문이 전달하려는 감정을 얼마나 효과적으로 전달했는가.\n\n"
                "평가 단계는 다음과 같습니다:\n"
                "1. **원문 분석**: 원문의 주제, 핵심 내용, 분위기, 감정을 파악합니다.\n"
                "2. **생성 문장 분석**: 생성 문장의 주제, 핵심 내용, 분위기, 감정을 파악합니다.\n"
                "3. **기준별 점수 부여**: 각 기준에 대해 점수를 1~10으로 부여합니다. "
                "모든 평가는 정직하고 객관적으로 수행해야 하며, 원문과 생성 문장 간의 유사성과 차이점을 "
                "상세히 분석하여 점수를 책정합니다.\n"
                "4. **결과 검토**: 부여한 점수를 확인하여 평가의 일관성을 검토합니다."
            ),
        },
        {
            "role": "user",
            "content": (
                "다음은 소설 원문과 생성된 문장입니다. 시스템은 이미 평가 기준을 알고 있습니다. "
                "원문과 생성 문장을 비교하여 평가를 수행하고 점수를 부여하고, 점수들을 리스트에 담아 출력합니다.\n\n"
                f"1. **원문**: {original_text}  \n"
                f"2. **생성 문장**: {generated_text}  \n\n"
                "**출력 형식**:  \n"
                "- 충실성: {점수}  \n"
                "- 세부 내용 반영도: {점수}  \n"
                "- 매력도/창의성: {점수}  \n"
                "- 유창성/정확성: {점수}  \n"
                "- 감정 전달력: {점수}  \n"
                "- 점수 리스트: "
                "[충실성 점수, 세부 내용 반영도 점수, 매력도/창의성 점수, 유창성/정확성 점수, 감정 전달력 점수]\n\n"
                "각 기준에 대해 점수를 1~10으로 부여해 주세요."
            ),
        },
    ]

    request_data = {
        "messages": preset_text,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.5,
        "stopBefore": [],
        "includeAiFilters": True,
        "seed": 2025,
    }

    config = configparser.ConfigParser()
    config.sections()
    config.read("./config/api_key.ini")

    completion_executor = CompletionExecutor(
        host=config["CLOVA"]["host"],
        api_key=config["CLOVA"]["api_key"],
        request_id=config["CLOVA"]["request_id"],
    )

    response_data = completion_executor.execute(request_data)
    result = process_response(response_data)

    if result["content"]:
        logger.info(f"Scores: {result['scores']}")
        logger.info(f"Total Score: {result['total_score']}")
        logger.info(f"Full Content:\n{result['content']}")
    else:
        logger.error("Failed to retrieve valid content from response.")
