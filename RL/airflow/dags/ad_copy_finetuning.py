import logging
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.dates import days_ago
from config import ACCESS_KEY, CLOVA_API_KEY, SECRET_KEY
from modules import (
    CompletionExecutor,
    calculate_ad_scores,
    create_finetuning_task,
    generate_ads_comparison,
    generate_qa_data_with_comparison,
    upload_file_to_s3,
)
import pandas as pd


# ✅ 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, "generated_ad_copies_with_likes,views,comments.csv")


SCORES_CSV = os.path.join(BASE_DIR, "generated_ad_copies_with_scores.csv")
OUTPUT_CSV_PATH = os.path.join(BASE_DIR, "hyperclovax_ab_feedback_dataset.csv")

# ✅ 로그 설정
logging.basicConfig(level=logging.INFO)

# ✅ Airflow DAG 정의
dag = DAG(
    dag_id="ad_finetuning_pipeline",
    description="광고 문구 비교 및 Fine-Tuning DAG (조건부 실행)",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
)

# ✅ 파일 존재 여부 확인 (BashOperator)
check_file = BashOperator(
    task_id="check_csv_file",
    bash_command=f"ls -l {CSV_FILE_PATH}",
    dag=dag,
)


# ✅ 1. 점수 계산 Task
def calculate_score_task(**kwargs):
    score = calculate_ad_scores(CSV_FILE_PATH, SCORES_CSV)
    kwargs["ti"].xcom_push(key="ad_score", value=score)
    logging.info(f"📊 광고 점수 계산 완료: {score}")
    return score


calculate_score = PythonOperator(
    task_id="calculate_score",
    python_callable=calculate_score_task,
    provide_context=True,
    dag=dag,
)


# ✅ 2. 점수 조건 확인 Task (BranchPythonOperator)
def check_score_task(**kwargs):
    score = kwargs["ti"].xcom_pull(task_ids="calculate_score", key="ad_score")
    if score <= 9000:
        logging.info(f"📉 점수 {score}가 9000 이하 → 파이프라인 실행")
        return "generate_ad_comparison"
    else:
        logging.info(f"✅ 점수 {score}가 9000 초과 → 파이프라인 실행 안 함")
        return "skip_pipeline"


check_score = BranchPythonOperator(
    task_id="check_score",
    python_callable=check_score_task,
    provide_context=True,
    dag=dag,
)


# ✅ 3. 광고 문구 비교 Task
def generate_ad_comparison_task():
    logging.info(f"📌 광고 문구 비교 데이터 생성 시작, 파일 경로: {SCORES_CSV}")

    if not os.path.exists(SCORES_CSV):
        raise FileNotFoundError(f"❌ 파일이 존재하지 않습니다: {SCORES_CSV}")

    ads_comparison = generate_ads_comparison(SCORES_CSV)
    logging.info(f"✅ 광고 문구 비교 데이터 생성 완료: {len(ads_comparison)}개")

    if len(ads_comparison) == 0:
        raise ValueError("❌ 광고 문구 비교 데이터가 비어 있습니다.")

    return ads_comparison


generate_ad_comparison = PythonOperator(
    task_id="generate_ad_comparison",
    python_callable=generate_ad_comparison_task,
    dag=dag,
)


# ✅ 4. QA 데이터 생성 Task
def generate_qa_data_task(**kwargs):
    ads_comparison = kwargs["ti"].xcom_pull(task_ids="generate_ad_comparison")

    completion_executor = CompletionExecutor(
        host="https://clovastudio.stream.ntruss.com",
        api_key=f"Bearer {CLOVA_API_KEY}",
        request_id="YOUR_REQUEST_ID",
    )

    qa_data = generate_qa_data_with_comparison(ads_comparison, completion_executor)

    qa_df = pd.DataFrame(qa_data)
    qa_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
    logging.info(f"✅ QA 데이터 CSV 저장 완료: {OUTPUT_CSV_PATH}")

    return OUTPUT_CSV_PATH


generate_qa_data = PythonOperator(
    task_id="generate_qa_data",
    python_callable=generate_qa_data_task,
    provide_context=True,
    dag=dag,
)


# ✅ 5. S3 업로드 Task
def upload_to_s3_task(**kwargs):
    file_path = kwargs["ti"].xcom_pull(task_ids="generate_qa_data")

    success, message = upload_file_to_s3(
        file_path,
        "testtesttesttestetst",
        "hyperclovax_ab_feedback_dataset.csv",
        ACCESS_KEY,
        SECRET_KEY,
    )

    if not success:
        raise Exception(f"S3 업로드 실패: {message}")

    logging.info(f"✅ S3 업로드 완료: {message}")


upload_to_s3 = PythonOperator(
    task_id="upload_to_s3",
    python_callable=upload_to_s3_task,
    provide_context=True,
    dag=dag,
)


# ✅ 6. Fine-Tuning 요청 Task
def finetuning_task(**kwargs):
    dataset_file = "testtesttesttestetst/hyperclovax_ab_feedback_dataset.csv"
    finetuning_response = create_finetuning_task(
        task_name="My_Ad_Finetuning_Task",
        model="HCX-003",
        tuning_type="PEFT",
        task_type="GENERATION",
        train_epochs=10,
        learning_rate=1e-5,
        dataset_file=dataset_file,
        bucket_name="testtesttesttestetst",
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        api_key=CLOVA_API_KEY,
    )

    logging.info(f"✅ Fine-Tuning 응답 결과: {finetuning_response}")


finetuning = PythonOperator(
    task_id="finetuning",
    python_callable=finetuning_task,
    provide_context=True,
    dag=dag,
)

# ✅ 7. 파이프라인 스킵 Task
skip_pipeline = DummyOperator(
    task_id="skip_pipeline",
    dag=dag,
)

# ✅ DAG 구조 설정
check_file >> calculate_score >> check_score >> [generate_ad_comparison, skip_pipeline]
generate_ad_comparison >> generate_qa_data >> upload_to_s3 >> finetuning
