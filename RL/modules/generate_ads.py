import pandas as pd


def generate_ads_comparison(csv_file):
    """CSV 파일을 읽고 광고 문구 데이터를 비교 쌍으로 생성하는 함수"""
    df = pd.read_csv(csv_file, encoding="utf-8")
    ads_comparison = []

    for i in range(0, len(df), 2):
        if i + 1 < len(df):
            ad1 = {"text": df.iloc[i]["copy"], "likes": df.iloc[i]["likes"]}
            ad2 = {"text": df.iloc[i + 1]["copy"], "likes": df.iloc[i + 1]["likes"]}
            ads_comparison.append({"ad1": ad1, "ad2": ad2})

    return ads_comparison
