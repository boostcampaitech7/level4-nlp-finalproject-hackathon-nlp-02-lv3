import os
import sys

import pandas as pd
import streamlit as st


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import csv

from loguru import logger
from modules_common.load_config import load_config
import requests
from sentence_generator.modules.sentence_generate import run_sg
from sentence_generator.modules.sentence_generate_eval import run_sg_eval
from tqdm import tqdm


def load_original_texts(file_path):
    """
    novel_contents.csv 파일에서 tcontent,id 컬럼을 읽어와 리스트로 반환하는 함수.
    """
    try:
        df = pd.read_csv(file_path)
        if "tcontent" not in df.columns or "id" not in df.columns:
            raise ValueError("CSV 파일에 'tcontent' 또는 'id' 컬럼이 존재하지 않습니다.")
        return df["tcontent"].dropna().astype(str).tolist(), df["id"].tolist()
    except Exception as e:
        logger.error(f"Error loading original texts: {e}")
        sys.exit(1)


def generate_n_sentences(original_text, num_sentences, threshold_proba, threshold_correctness):
    """
    문장을 생성하고 평가하여 일정 점수 이상일 경우 리스트에 추가하는 함수.
    """
    generated_texts = []
    index = 0
    trial = 0
    while len(generated_texts) < num_sentences:
        generated_text = run_sg(original_text, index)
        eval_result = run_sg_eval(original_text, generated_text)
        sum_scores, proba_score, sum_proba_scores = eval_result

        if (
            sum_proba_scores is not None
            and sum_proba_scores >= threshold_proba
            and proba_score[0] >= threshold_correctness
        ):
            generated_texts.append(generated_text.replace("\n", " ").replace('"  "', " "))
            index += 1
        else:
            logger.warning("Score below threshold. Retrying...")
            trial += 1
            if trial > 4:
                index += 1
    return generated_texts


def save_generated_sentences(id, generated_texts, output_file_path):
    """
    생성된 문장을 CSV 파일에 저장하는 함수.
    """
    new_df = pd.DataFrame([{"id": id, **{f"sentence{i + 1}": text for i, text in enumerate(generated_texts)}}])
    try:
        existing_df = pd.read_csv(output_file_path)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    except FileNotFoundError:
        updated_df = pd.DataFrame(new_df)
    updated_df.to_csv(output_file_path, index=False)
    logger.info("✅ Saved generated sentences")


def send_generated_sentences(file_path):
    """CSV 데이터를 API로 전송하는 함수."""
    config_api = load_config("../config/config_api.yaml")
    URL = config_api["SERVER"]["URL"]
    ADMIN_CODE = config_api["SERVER"]["ADMIN_CODE"]

    with open(file_path, "r", encoding="utf-8") as file:
        data_list = list(csv.DictReader(file))
    success_count = 0

    st.success("🚗 API로 이동 중...")

    for row in data_list:
        novel_id = row.get("id")
        for i in range(1, 2):
            content = row.get(f"sentence{i}")
            if not content:
                continue
            data = {"admin_code": ADMIN_CODE, "shorts_data": {"novel_id": int(novel_id), "content": content}}
            response = requests.post(f"{URL}/admin/shorts", json=data, verify=False)
            if response.status_code == 200:
                success_count += 1
            else:
                logger.error(f"Failed to send - novel_id: {novel_id}, Status Code: {response.status_code}")
    logger.info(f"✅ Successfully sent {success_count} sentences.")


def main():
    st.set_page_config(page_title="📖 Novel Processing App", layout="wide")
    st.sidebar.image("../logo.png", use_container_width=True)

    st.sidebar.title("📌 Menu")
    page = st.sidebar.radio("📂 Select Page", ["📤 Upload Novel File", "✍️ Regenerate Novel Sentences"])
    if page == "📤 Upload Novel File":
        upload_page()
    elif page == "✍️ Regenerate Novel Sentences":
        regenerate_page()


def upload_page():
    st.title("📤 Upload Novel CSV File")
    uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

    # 파일이 업로드되지 않았으면 함수 종료
    if uploaded_file is None:
        st.warning("Please upload a CSV file.")
        return

    st.success("File uploaded successfully!")

    # 파일을 읽어서 처리
    original_texts, ids = load_original_texts(uploaded_file)
    if not original_texts:
        st.error("No valid text found in the uploaded file.")
        return

    if st.button("🚀 Start Process"):
        st.success("🏃‍♂️‍➡️ Processing started!")
        output_file_path = "output_novel_content.csv"
        for original_text, id_value in tqdm(
            zip(original_texts, ids), desc="Generating sentences", total=len(original_texts)
        ):
            generated_texts = generate_n_sentences(original_text, 1, 20, 6.0)
            save_generated_sentences(id_value, generated_texts, output_file_path)

        send_generated_sentences("output_novel_content.csv")
        st.success("🎉 Processing completed and results saved.🎉")


def regenerate_page():
    st.title("Regenerate Novel Sentences")
    upload_period = st.date_input("Select Novel Upload Period", [])
    threshold_score = st.number_input("Enter Threshold Score", min_value=0, max_value=100, value=50)
    if st.button("Start Process"):
        st.success(f"✅ Processing started with upload period {upload_period} and threshold score {threshold_score}!")


if __name__ == "__main__":
    main()
