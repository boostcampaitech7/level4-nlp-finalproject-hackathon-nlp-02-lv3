import logging

import pandas as pd


# 로그 설정
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] - %(message)s",
    level=logging.INFO,  # 기본 로그 레벨 설정 (DEBUG로 변경 가능)
    handlers=[
        logging.StreamHandler(),  # 터미널 출력
        logging.FileHandler("qa_generation.log", mode="w", encoding="utf-8"),  # 파일 저장
    ],
)


def get_feedback_from_model(completion_executor, ad1_text, ad2_text, ad1_likes, ad2_likes):
    """모델 피드백을 요청하여 광고 문구 비교"""
    logging.info(f"🔍 모델 피드백 요청: ad1='{ad1_text}', ad2='{ad2_text}'")

    preset_text = [
        {
            "role": "system",
            "content": f"아래는 같은 소설에 대한 두 가지 홍보 문구입니다.\n"
            f'1번 문구: "{ad1_text}"\n'
            f'2번 문구: "{ad2_text}"\n'
            f"두 문구 중 사용자의 평가 점수가 높은 문장이 좋은 문장입니다.\n"
            f"두 문장 중에 어떤 문장이 좋은지 말하고, 그 이유를 함께 말하세요.",
        },
        {
            "role": "user",
            "content": f'"ad1": {{"text": "{ad1_text}", "likes": {ad1_likes}}}, '
            f'"ad2": {{"text": "{ad2_text}", "likes": {ad2_likes}}}',
        },
    ]

    request_data = {
        "messages": preset_text,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.5,
        "repeatPenalty": 5.0,
        "stopBefore": [],
        "includeAiFilters": True,
        "seed": 0,
    }

    response = completion_executor.execute(request_data)

    if response:
        logging.info(f"✅ 모델 응답: {response}")
    else:
        logging.warning(f"⚠️ 모델 응답 없음: ad1='{ad1_text}', ad2='{ad2_text}'")
        response = "모델 응답을 받을 수 없습니다."

    return response


def generate_qa_data_with_comparison(ads_comparison, completion_executor):
    """QA 데이터셋 생성"""
    qa_dataset = []
    logging.info(f"📌 {len(ads_comparison)}개의 광고 문구 비교 시작...")

    for c_id, comparison in enumerate(ads_comparison):
        ad1 = comparison["ad1"]
        ad2 = comparison["ad2"]

        question = (
            f"다음은 같은 소설에 대한 두 가지 홍보 문구입니다.\n"
            f"1번: \"{ad1['text']}\" (좋아요 {ad1['likes']}개)\n"
            f"2번: \"{ad2['text']}\" (좋아요 {ad2['likes']}개)\n"
            f"어떤 문구가 사용자에게 더 효과적인 홍보 효과를 보였을까요?"
        )
        logging.info(f"📌 {c_id + 1}/{len(ads_comparison)} 비교 질문 생성 완료\n {question}")

        # 모델 피드백 요청
        feedback = get_feedback_from_model(completion_executor, ad1["text"], ad2["text"], ad1["likes"], ad2["likes"])

        # 피드백을 기반으로 답변 생성
        if ad2["likes"] > ad1["likes"]:
            answer = f"2번 문구가 더 효과적이었습니다. 이유: {feedback}"
        else:
            answer = f"1번 문구가 더 효과적이었습니다. 이유: {feedback}"

        logging.info(f"✅ {c_id + 1}/{len(ads_comparison)} 비교 완료 - 정답 생성")

        qa_dataset.append({"C_ID": c_id, "T_ID": 0, "Text": question, "Completion": answer})

    logging.info("🎯 QA 데이터셋 생성 완료!")

    # CSV 저장 확인
    df = pd.DataFrame(qa_dataset)
    df.to_csv("hyperclovax_ab_feedback_dataset.csv", index=False, encoding="utf-8")
    logging.info("✅ 데이터셋 CSV 저장 완료: hyperclovax_ab_feedback_dataset.csv")

    return qa_dataset
