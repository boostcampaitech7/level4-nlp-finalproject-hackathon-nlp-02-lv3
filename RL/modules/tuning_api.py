import json
import logging

from config import ACCESS_KEY, CLOVA_API_KEY, SECRET_KEY  # API 키 추가
import requests


# 로그 설정
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] - %(message)s",
    level=logging.INFO,
)

# 네이버 클라우드 Clova Studio Fine-Tuning API 엔드포인트
TUNING_API_URL = "https://clovastudio.stream.ntruss.com/tuning/v2/tasks"


def create_finetuning_task(
    task_name,
    model="HCX-003",
    tuning_type="PEFT",
    task_type="GENERATION",
    train_epochs=10,
    learning_rate=1e-5,
    dataset_file="hyperclovax_ab_feedback_dataset.csv",
    bucket_name="testtesttesttestetst",
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    api_key=CLOVA_API_KEY,  # Clova Studio API Key 추가
):
    """
    네이버 클라우드 Clova Studio에 Fine-Tuning 요청을 보내는 함수

    Args:
        task_name (str): Fine-tuning 작업의 이름
        model (str): 사용할 모델 (기본값: "HCX-003")
        tuning_type (str): 튜닝 방식 (기본값: "PEFT")
        task_type (str): 작업 유형 (기본값: "GENERATION")
        train_epochs (int): 학습 Epoch 수
        learning_rate (float): 학습률
        dataset_file (str): 업로드한 데이터셋 파일명
        bucket_name (str): 데이터셋이 저장된 S3 버킷명
        access_key (str): NCP Access Key
        secret_key (str): NCP Secret Key
        api_key (str): Clova Studio API 키 (기본값: `config.py`에서 불러옴)

    Returns:
        dict: API 응답 데이터
    """
    headers = {
        "Authorization": f"Bearer {api_key}",  # Authorization 헤더 추가
        "Content-Type": "application/json; charset=utf-8",
    }

    payload = {
        "name": task_name,
        "model": model,
        "tuningType": tuning_type,
        "taskType": task_type,
        "trainEpochs": train_epochs,
        "learningRate": learning_rate,
        "trainingDatasetFilePath": dataset_file,
        "trainingDatasetBucket": bucket_name,
        "trainingDatasetAccessKey": access_key,
        "trainingDatasetSecretKey": secret_key,
    }

    logging.info(f"🚀 Fine-Tuning 요청 시작: {task_name}")
    logging.info(
        f"📡 API 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}"
    )

    response = requests.post(TUNING_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        logging.info("✅ Fine-Tuning 요청 성공!")
        return response.json()
    else:
        logging.error(
            f"❌ Fine-Tuning 요청 실패: {response.status_code} - {response.text}"
        )
        return {"error": response.status_code, "message": response.text}
