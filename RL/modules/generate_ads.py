import pandas as pd


def generate_ads_comparison(csv_file):
    """광고 문구 데이터를 중간값 기준으로 비교 쌍을 생성하는 함수"""
    df = pd.read_csv(csv_file, encoding="utf-8")

    # 중간값(median) 계산
    threshold = df["scores"].median()

    # 점수 기준으로 두 그룹으로 나누기
    high_score_ads = df[df["scores"] >= threshold].reset_index(drop=True)
    low_score_ads = df[df["scores"] < threshold].reset_index(drop=True)

    ads_comparison = []

    # 모든 데이터를 사용하기 위해 작은 그룹 기준으로 순환
    max_len = max(len(high_score_ads), len(low_score_ads))

    for i in range(max_len):
        ad1 = high_score_ads.iloc[i % len(high_score_ads)]  # 높은 점수 그룹
        ad2 = low_score_ads.iloc[i % len(low_score_ads)]  # 낮은 점수 그룹

        ads_comparison.append(
            {
                "ad1": {"text": ad1["copy"], "scores": ad1["scores"]},
                "ad2": {"text": ad2["copy"], "scores": ad2["scores"]},
            }
        )

    return ads_comparison


# 테스트 실행 예시
csv_file = "./ad_copy_scores.csv"  # copy, scores로 이루어진 CSV 파일
