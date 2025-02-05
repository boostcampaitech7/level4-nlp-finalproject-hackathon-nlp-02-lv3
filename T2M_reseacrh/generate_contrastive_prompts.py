"""
이 코드는 Input text의 분위기를 LLM을 통해 추출합니다.
input text의 positive mood와 negative mood를 생성한 후 원본 csv에 컬럼을 추가하는 형식으로 저장합니다.
추후 생성된 음악의 품질 측정에 사용합니다.
"""

# -*- coding: utf-8 -*-
import os
import sys
import time  # ✅ 시간 지연을 위한 모듈 추가
import pandas as pd
from loguru import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules_common.completion_executor import CompletionExecutor
from modules_common.load_config import load_config

# ✅ API 설정 로드
config_api = load_config("../config/config_api.yaml")
config = load_config("../config/config_contrastive.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]

# ✅ 파일 경로 설정
REFINED_DATA_FOLDER = "refined_data"

INPUT_FILES = [
    "cleaned_like_input_text.csv",
    "cleaned_likepernumber_input_text.csv",
]

OUTPUT_FILES = [
    "contrasted_like_input_text.csv",
    "contrasted_likepernumber_input_text.csv",
]

# ✅ LLM 프롬프트 요청 함수 (지수적 백오프 적용)
def request_mood(original_text, mood_type, retry_count=5, delay=2):
    """LLM을 사용해 주어진 텍스트의 분위기(positive/negative)를 생성"""
    if retry_count == 0:
        logger.error(f"🚨 재생성 한도를 초과하여 기본값 반환 ({mood_type})")
        return "N/A"  # 기본값 반환

    completion_executor = CompletionExecutor(
        host=COMPLETION_HOST_URL,
        api_key=API_KEY,
        request_id=REQUEST_ID,
    )

    user_prompt_key = "user_positive" if mood_type == "positive" else "user_negative"

    preset_text = [
        {
            "role": config["contrastive_LLM"]["preset_text"]["system"]["role"],
            "content": config["contrastive_LLM"]["preset_text"]["system"]["content"],
        },
        {
            "role": config["contrastive_LLM"]["preset_text"][user_prompt_key]["role"],
            "content": config["contrastive_LLM"]["preset_text"][user_prompt_key]["content"].replace("{original_text}", original_text),
        },
    ]

    request_data = {
        "messages": preset_text,
        "topP": config["contrastive_LLM"]["request_params"]["topP"],
        "topK": config["contrastive_LLM"]["request_params"]["topK"],
        "maxTokens": config["contrastive_LLM"]["request_params"]["maxTokens"],
        "temperature": config["contrastive_LLM"]["request_params"]["temperature"],
        "stopBefore": config["contrastive_LLM"]["request_params"]["stopBefore"],
        "includeAiFilters": config["contrastive_LLM"]["request_params"]["includeAiFilters"],
        "seed": config["contrastive_LLM"]["request_params"]["seed"],
    }

    response_data = completion_executor.execute(request_data)

    # ✅ 디버깅용 API 응답 확인
    logger.debug(f"🛠️ LLM 응답 ({mood_type}): {response_data}")

    if response_data is None:
        logger.warning(f"⚠️ API 응답 없음 → 재시도 남은 횟수: {retry_count - 1} ({mood_type})")
        new_delay = min(delay * 2, 60)  # ✅ 대기 시간을 2배 증가 (최대 60초 제한)
        logger.info(f"⏳ {new_delay}초 대기 후 재시도...")
        time.sleep(new_delay)
        return request_mood(original_text, mood_type, retry_count - 1, new_delay)

    response_cleaned = response_data.strip()

    # ✅ 응답이 비었거나, 너무 짧은 경우 재생성 요청
    if response_cleaned == "" or len(response_cleaned) < 3:
        logger.warning(f"⚠️ 응답이 너무 짧음 → 재생성 요청 ({mood_type})")
        new_delay = min(delay * 2, 60)  # ✅ 대기 시간을 2배 증가 (최대 60초 제한)
        logger.info(f"⏳ {new_delay}초 대기 후 재시도...")
        time.sleep(new_delay)
        return request_mood(original_text, mood_type, retry_count - 1, new_delay)

    return response_cleaned

# ✅ CSV 처리
for input_file, output_file in zip(INPUT_FILES, OUTPUT_FILES):
    input_path = os.path.join(REFINED_DATA_FOLDER, input_file)
    output_path = os.path.join(REFINED_DATA_FOLDER, output_file)

    if not os.path.exists(input_path):
        logger.warning(f"⚠️ 파일 없음: {input_path}, 건너뜁니다.")
        continue

    logger.info(f"📂 {input_path} 처리 중...")

    df = pd.read_csv(input_path)

    # ✅ 새 컬럼 추가
    df["positive_mood"] = ""
    df["negative_mood"] = ""

    for idx, row in df.iterrows():
        original_text = row["musicgen_input_text"]
        
        # ✅ 분위기 및 반대 분위기 생성
        positive_mood = request_mood(original_text, "positive")
        negative_mood = request_mood(original_text, "negative")

        df.at[idx, "positive_mood"] = positive_mood
        df.at[idx, "negative_mood"] = negative_mood

        if (idx + 1) % 10 == 0:  # 진행 로그 (10개 단위)
            logger.info(f"🔄 {idx + 1}/{len(df)} 행 처리 완료...")

    # ✅ CSV 저장
    df.to_csv(output_path, index=False)
    logger.info(f"✅ {output_path} 저장 완료! 총 {len(df)}개 행 처리 완료.")
