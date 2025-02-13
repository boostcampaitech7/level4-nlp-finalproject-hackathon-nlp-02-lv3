# -*- coding: utf-8 -*-
import argparse
import csv
import logging
import os
import sys

import requests


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules_common.load_config import load_config


# 로그 설정
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("request_log.log", mode="w", encoding="utf-8"),  # 로그 파일 저장
    ],
)

# 설정 로드
config_api = load_config("../config/config_api.yaml")
URL = config_api["SERVER"]["URL"]
ADMIN_CODE = config_api["SERVER"]["ADMIN_CODE"]


def read_csv(file):
    """CSV 파일을 읽고 데이터를 리스트로 반환"""
    try:
        with open(file, mode="r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except csv.Error as e:
        logging.exception(f"CSV 파일 읽기 오류: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logging.error(f"CSV 파일을 찾을 수 없음: {file}")
        sys.exit(1)


def validate_data(novel_id, content):
    """데이터 유효성 검사"""
    try:
        novel_id = int(novel_id)
        assert isinstance(content, str) and content.strip(), "Content must be a non-empty string"
        return novel_id, content
    except (ValueError, AssertionError) as e:
        logging.error(f"데이터 검증 실패 - novel_id: {novel_id}, content: {content}, 오류: {e}")
        return None, None


def send_request(novel_id, content):
    """API 요청을 전송하고 응답을 반환"""
    data = {
        "admin_code": ADMIN_CODE,
        "shorts_data": {"novel_id": novel_id, "content": content},
    }

    try:
        response = requests.post(f"{URL}/admin/shorts", json=data, verify=False)
        if response.status_code == 200:
            logging.info(f"성공적으로 전송됨 - novel_id: {novel_id}")
            return True
        else:
            logging.error(f"전송 실패 - novel_id: {novel_id}, 상태 코드: {response.status_code}, 응답: {response.text}")
            return False
    except requests.RequestException as e:
        logging.exception(f"요청 오류 - novel_id: {novel_id}, 오류: {e}")
        return False


def process_csv_data(file):
    """CSV 데이터를 처리하고 API 요청을 전송"""
    data_list = read_csv(file)
    success_count = 0

    for row in data_list:
        novel_id = row.get("id")
        for i in range(1, 2):
            content = row.get(f"sentence{i}")
            if not content:
                continue

            valid_id, valid_content = validate_data(novel_id, content)
            if valid_id is None:
                continue

            if send_request(valid_id, valid_content):
                success_count += 1

    logging.info(f"총 성공 요청 수: {success_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSV 파일을 읽고, 문장을 API 서버로 전송하는 기능")
    parser.add_argument(
        "--file",
        type=str,
        default="novel_contents/final_output_contents.csv",
        help="CSV 파일의 경로를 입력하세요 (예: final_output.csv)",
    )
    args = parser.parse_args()
    process_csv_data(args.file)
