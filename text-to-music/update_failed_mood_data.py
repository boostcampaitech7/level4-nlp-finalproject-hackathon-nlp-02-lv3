import os
import sys
import time

from loguru import logger
import pandas as pd


# ✅ 스크립트의 위치를 기준으로 상위 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules_common.completion_executor import CompletionExecutor
from modules_common.load_config import load_config


# ✅ API 및 설정 로드
config_api = load_config("../config/config_api.yaml")
config = load_config("../config/config_contrastive.yaml")

API_KEY = config_api["API"]["API_KEY"]
REQUEST_ID = config_api["API"]["REQUEST_ID"]
COMPLETION_HOST_URL = config_api["API"]["HOST_URL"]

# ✅ 파일 경로 설정
GENERATED_MUSIC_FOLDER = "generated_music/likepernumber"
REFINED_DATA_FOLDER = "refined_data"
INPUT_CSV = "contrasted_likepernumber_input_text.csv"


# ✅ LLM을 통해 분위기 생성하는 함수
def request_mood(original_text, mood_type, retry_count=5, delay=2):
    """LLM을 사용해 주어진 텍스트의 분위기(positive/negative)를 생성"""
    if retry_count == 0:
        logger.error(f"🚨 재생성 한도를 초과하여 기본값 반환 ({mood_type})")
        return "N/A"

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
            "content": config["contrastive_LLM"]["preset_text"][user_prompt_key]["content"].replace(
                "{original_text}", original_text
            ),
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

    logger.debug(f"🛠️ LLM 응답 ({mood_type}): {response_data}")

    if response_data is None or response_data.strip() == "":
        logger.warning(f"⚠️ API 응답 없음 → 재시도 남은 횟수: {retry_count - 1} ({mood_type})")
        new_delay = min(delay * 2, 60)
        logger.info(f"⏳ {new_delay}초 대기 후 재시도...")
        time.sleep(new_delay)
        return request_mood(original_text, mood_type, retry_count - 1, new_delay)

    return response_data.strip()


# ✅ 생성되지 않은 ID 찾기
def find_unprocessed_ids():
    """생성이 실패한 ID 목록 반환"""
    generated_files = {f.split(".")[0] for f in os.listdir(GENERATED_MUSIC_FOLDER) if f.endswith(".wav")}

    input_csv_path = os.path.join(REFINED_DATA_FOLDER, INPUT_CSV)
    if not os.path.exists(input_csv_path):
        logger.error(f"🚨 CSV 파일을 찾을 수 없음: {input_csv_path}")
        return []

    df = pd.read_csv(input_csv_path)
    csv_ids = set(df["id"].astype(str))

    unprocessed_ids = csv_ids - generated_files
    logger.info(f"🔍 {len(unprocessed_ids)}개의 미생성 ID 발견!")

    return df[df["id"].astype(str).isin(unprocessed_ids)]


# ✅ 분위기 값 업데이트 및 CSV 저장
def update_mood_data():
    """생성이 실패한 데이터의 분위기 값을 다시 생성하고 CSV 업데이트"""
    df_unprocessed = find_unprocessed_ids()

    if df_unprocessed.empty:
        logger.info("✅ 모든 데이터가 생성되었으며, 업데이트가 필요하지 않습니다.")
        return

    for idx, row in df_unprocessed.iterrows():
        original_text = row["musicgen_input_text"]

        # ✅ LLM을 통해 분위기 다시 생성
        new_positive_mood = request_mood(original_text, "positive")
        new_negative_mood = request_mood(original_text, "negative")

        df_unprocessed.at[idx, "positive_mood"] = new_positive_mood
        df_unprocessed.at[idx, "negative_mood"] = new_negative_mood

        if (idx + 1) % 10 == 0:
            logger.info(f"🔄 {idx + 1}/{len(df_unprocessed)} 행 업데이트 완료...")

    # ✅ 원본 CSV 업데이트
    input_csv_path = os.path.join(REFINED_DATA_FOLDER, INPUT_CSV)
    df_original = pd.read_csv(input_csv_path)

    for idx, row in df_unprocessed.iterrows():
        df_original.loc[df_original["id"] == row["id"], ["positive_mood", "negative_mood"]] = (
            row["positive_mood"],
            row["negative_mood"],
        )

    # ✅ CSV 저장
    df_original.to_csv(input_csv_path, index=False)
    logger.info(f"✅ 업데이트 완료! {len(df_unprocessed)}개의 분위기 값이 새로 생성됨.")


# ✅ 실행
if __name__ == "__main__":
    update_mood_data()
