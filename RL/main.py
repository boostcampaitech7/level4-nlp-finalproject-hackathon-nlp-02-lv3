from config import ACCESS_KEY, CLOVA_API_KEY, SECRET_KEY
from modules import (
    CompletionExecutor,
    create_finetuning_task,
    generate_ads_comparison,
    generate_qa_data_with_comparison,
    upload_file_to_s3,
)
import pandas as pd


# 광고 문구 데이터 생성
ads_comparison = generate_ads_comparison("generated_ad_copies_with_likes.csv")

# 모델 실행 준비
completion_executor = CompletionExecutor(
    host="https://clovastudio.stream.ntruss.com",
    api_key=f"Bearer {CLOVA_API_KEY}",
    request_id="YOUR_REQUEST_ID",
)

# QA 데이터 생성
qa_data = generate_qa_data_with_comparison(ads_comparison, completion_executor)

# 저장
qa_df = pd.DataFrame(qa_data)
qa_df.to_csv("hyperclovax_ab_feedback_dataset.csv", index=False, encoding="utf-8")

# S3 업로드
upload_file_to_s3(
    "./hyperclovax_ab_feedback_dataset.csv",
    "testtesttesttestetst",
    "hyperclovax_ab_feedback_dataset.csv",
    ACCESS_KEY,
    SECRET_KEY,
)

# Fine-Tuning 요청 실행
finetuning_response = create_finetuning_task(
    task_name="My_Ad_Finetuning_Task",
    model="HCX-003",
    tuning_type="PEFT",
    task_type="GENERATION",
    train_epochs=10,
    learning_rate=1e-5,
    dataset_file="./testtesttesttestetst/hyperclovax_ab_feedback_dataset.csv",
    bucket_name="testtesttesttestetst",
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    api_key=CLOVA_API_KEY,
)

print("Fine-Tuning 응답 결과:", finetuning_response)
