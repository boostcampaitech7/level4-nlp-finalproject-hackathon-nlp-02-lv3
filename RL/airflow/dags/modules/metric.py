import pandas as pd


def calculate_ad_scores(input_csv, output_csv):
    """광고 문구의 점수를 계산하여 새로운 CSV 파일로 저장하고 평균 점수를 반환하는 함수"""
    df = pd.read_csv(input_csv, encoding="utf-8")

    # 점수 계산: (likes) + (comments * 10)
    df["scores"] = (df["likes"]) + (df["comments"] * 10)

    # 필요한 컬럼만 남기고 새로운 CSV로 저장
    df[["copy", "scores"]].to_csv(output_csv, index=False, encoding="utf-8")

    # 평균 점수 계산
    average_score = df["scores"].mean()

    print(f"✅ 점수 계산 완료! 저장된 파일: {output_csv}")
    print(f"📊 전체 광고 문구의 평균 점수: {average_score}")

    return average_score  # 평균 점수 반환


# 실행 예시
input_csv = "./generated_ad_copies_with_likes,views,comments.csv"  # 기존 CSV
output_csv = "ad_copy_scores.csv"  # 점수가 포함된 새로운 CSV
average_score = calculate_ad_scores(input_csv, output_csv)

print(f"📢 평균 점수: {average_score}")  # 출력
