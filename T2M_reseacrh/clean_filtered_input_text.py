import pandas as pd
import os

# 폴더 경로 설정
refined_data_folder = "refined_data"

# 파일 로드
like_input_text_path = os.path.join(refined_data_folder, "like_input_text.csv")
likepernumber_input_text_path = os.path.join(refined_data_folder, "likepernumber_input_text.csv")

like_df = pd.read_csv(like_input_text_path)
likepernumber_df = pd.read_csv(likepernumber_input_text_path)

# 원래 데이터 개수 저장
original_like_count = len(like_df)
original_likepernumber_count = len(likepernumber_df)

# 1️⃣ 중복된 id 제거 (첫 번째 행만 유지)
like_df = like_df.drop_duplicates(subset="id", keep="first")
likepernumber_df = likepernumber_df.drop_duplicates(subset="id", keep="first")

# 중복 제거 후 개수
after_dedup_like_count = len(like_df)
after_dedup_likepernumber_count = len(likepernumber_df)

# 2️⃣ musicgen_input_text 컬럼이 비어있는 행 제거
like_df = like_df.dropna(subset=["musicgen_input_text"])
likepernumber_df = likepernumber_df.dropna(subset=["musicgen_input_text"])

# 최종 남은 개수
final_like_count = len(like_df)
final_likepernumber_count = len(likepernumber_df)

# 3️⃣ 새로운 파일로 저장
cleaned_like_path = os.path.join(refined_data_folder, "cleaned_like_input_text.csv")
cleaned_likepernumber_path = os.path.join(refined_data_folder, "cleaned_likepernumber_input_text.csv")

like_df.to_csv(cleaned_like_path, index=False)
likepernumber_df.to_csv(cleaned_likepernumber_path, index=False)

# 출력 결과
print(f"✅ {cleaned_like_path} 저장 완료.")
print(f"   - 원래 데이터: {original_like_count}개 → 중복 제거 후: {after_dedup_like_count}개 → 결측값 제거 후: {final_like_count}개")

print(f"✅ {cleaned_likepernumber_path} 저장 완료.")
print(f"   - 원래 데이터: {original_likepernumber_count}개 → 중복 제거 후: {after_dedup_likepernumber_count}개 → 결측값 제거 후: {final_likepernumber_count}개")
