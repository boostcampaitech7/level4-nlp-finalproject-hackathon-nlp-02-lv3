import pandas as pd

# 파일 경로
input_text_path = "raw_data/input_text.csv"

# CSV 파일 로드
df = pd.read_csv(input_text_path)

# 전체 행 개수 확인
total_rows = len(df)

# ID 중복 체크
duplicate_id_count = df["id"].duplicated().sum()

# musicgen_input_text가 비어있는 행 확인
empty_musicgen_rows = df["musicgen_input_text"].isna().sum() + (df["musicgen_input_text"].astype(str).str.strip() == "").sum()

# 결과 출력
print(f"📊 데이터 품질 체크 결과")
print(f"----------------------------------------------------")
print(f"✅ 총 행 개수: {total_rows} 개")
print(f"⚠️ 중복된 ID 개수: {duplicate_id_count} 개" if duplicate_id_count > 0 else "✅ 중복된 ID 없음")
print(f"⚠️ 'musicgen_input_text'가 비어 있는 행 개수: {empty_musicgen_rows} 개" if empty_musicgen_rows > 0 else "✅ 'musicgen_input_text'가 비어 있는 행 없음")
print(f"----------------------------------------------------")
