import pandas as pd

# 파일 경로
input_text_path = "refined_data/novel_content_100_likespernumber_input_text.csv"

# CSV 파일 로드
df = pd.read_csv(input_text_path)

# 전체 행 개수 확인
total_rows = len(df)

# 유니크한 ID 개수 확인
unique_ids = df["id"].nunique()

# 중복된 ID 개수 확인
duplicate_id_count = df["id"].duplicated().sum()

# 중복된 ID 목록과 각각 몇 번씩 중복되는지 확인
duplicate_id_summary = df["id"].value_counts()
duplicate_id_summary = duplicate_id_summary[duplicate_id_summary > 1]  # 2번 이상 중복된 것만 필터링

# musicgen_input_text가 비어있는 행 개수 확인 (NaN 또는 공백)
empty_musicgen_rows = df["musicgen_input_text"].isna().sum() + (df["musicgen_input_text"].astype(str).str.strip() == "").sum()

# 결과 출력
print(f"📊 데이터 품질 체크 결과")
print(f"----------------------------------------------------")
print(f"✅ 총 행 개수: {total_rows} 개")
print(f"✅ 유니크한 ID 개수: {unique_ids} 개")
print(f"⚠️ 중복된 ID 개수: {duplicate_id_count} 개" if duplicate_id_count > 0 else "✅ 중복된 ID 없음")
print(f"⚠️ 'musicgen_input_text'가 비어 있는 행 개수: {empty_musicgen_rows} 개" if empty_musicgen_rows > 0 else "✅ 'musicgen_input_text'가 비어 있는 행 없음")

# 중복된 ID 목록 출력 (최대 10개까지만 출력)
if not duplicate_id_summary.empty:
    print("\n⚠️ 중복된 ID 상세 정보:")
    print(duplicate_id_summary.head(10).to_string())  # 상위 10개만 출력
    if len(duplicate_id_summary) > 10:
        print(f"...총 {len(duplicate_id_summary)}개의 중복된 ID가 존재함.")

print(f"----------------------------------------------------")
