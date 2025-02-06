import pandas as pd
import os

# 폴더 경로 설정
raw_data_path = "raw_data/input_text.csv"
refined_data_folder = "refined_data"

# 파일 로드
input_text_df = pd.read_csv(raw_data_path)  # input_text.csv (id, musicgen_input_text)
like_df = pd.read_csv(os.path.join(refined_data_folder, "like.csv"))  # id만 있음
likepernumber_df = pd.read_csv(os.path.join(refined_data_folder, "likepernumber.csv"))  # id만 있음

# 정제 과정: like.csv 기준 필터링
like_filtered_df = input_text_df[input_text_df["id"].isin(like_df["id"])]
like_filtered_path = os.path.join(refined_data_folder, "like_input_text.csv")
like_filtered_df.to_csv(like_filtered_path, index=False)
print(f"✅ {like_filtered_path} 저장 완료. {len(like_filtered_df)}개 데이터")

# 정제 과정: likepernumber.csv 기준 필터링
likepernumber_filtered_df = input_text_df[input_text_df["id"].isin(likepernumber_df["id"])]
likepernumber_filtered_path = os.path.join(refined_data_folder, "likepernumber_input_text.csv")
likepernumber_filtered_df.to_csv(likepernumber_filtered_path, index=False)
print(f"✅ {likepernumber_filtered_path} 저장 완료. {len(likepernumber_filtered_df)}개 데이터")
