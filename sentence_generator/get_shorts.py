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
)

# 설정 로드
config_api = load_config("../config/config_api.yaml")
URL = config_api["SERVER"]["URL"]
ADMIN_CODE = config_api["SERVER"]["ADMIN_CODE"]


def fetch_shorts_data(limit, offset):
    """API에서 shorts 데이터를 가져옴"""
    params = {
        "limit": limit,
        "offset": offset,
    }

    try:
        response = requests.get(URL, params=params, headers={"accept": "application/json"}, verify=False)

        if response.status_code == 200:
            logging.info("Successfully retrieved shorts list.")
            return response.json()
        else:
            logging.error(
                f"Failed to retrieve shorts list. Status code: {response.status_code}, " f"Response: {response.text}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logging.exception(f"API 요청 중 오류 발생: {e}")
        return None


def save_to_csv(output_file, data):
    """가져온 데이터를 CSV 파일로 저장"""
    if not data:
        logging.error("저장할 데이터가 없습니다.")
        return

    try:
        with open(output_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(
                [
                    "no",
                    "form_type",
                    "content",
                    "music",
                    "views",
                    "likes",
                    "saves",
                    "comments",
                    "title",
                    "author",
                    "source_url",
                ]
            )

            for item in data:
                writer.writerow(
                    [
                        item.get("no"),
                        item.get("form_type"),
                        item.get("content"),
                        item.get("music"),
                        item.get("views"),
                        item.get("likes"),
                        item.get("saves"),
                        item.get("comments"),
                        item.get("title"),
                        item.get("author"),
                        item.get("source_url"),
                    ]
                )

        logging.info(f"Data successfully saved to {output_file}")
    except IOError as e:
        logging.exception(f"CSV 파일 저장 중 오류 발생: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "이 스크립트는 API에서 데이터를 가져와 CSV 파일로 저장합니다.\n"
            "\n"
            "사용 예시:\n"
            "  python script.py --limit 100 --offset 0\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="한 번에 가져올 최대 항목 수 (기본값: 100)",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="가져올 데이터의 시작 위치 (기본값: 0)",
    )
    parser.add_argument(
        "--file",
        type=argparse.FileType("r", encoding="utf-8"),
        required=True,
        help="CSV 파일의 경로를 입력하세요 (예: final_output.csv)",
    )

    args = parser.parse_args()
    shorts_data = fetch_shorts_data(args.limit, args.offset)

    if shorts_data:
        save_to_csv(args.file, shorts_data)
