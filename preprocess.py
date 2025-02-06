from loguru import logger
import pandas as pd


# CSV 파일 읽기
origin_df = pd.read_csv("./novel_content_450000_중간과정.csv")
origin_meta_df = pd.read_csv("./novel_metadata_450000_중간과정.csv")

logger.info("1st. tcontent가 없는 데이터 제거")
preprocessed_df = origin_df[origin_df["tcontent"].fillna("").str.len() > 1000]

# 상위 N개의 데이터를 담을 빈 데이터프레임 생성
quality_df = pd.DataFrame(columns=["id", "tcontent"])

logger.info("2nd. 조회수, 추천수 기준 정렬 (상위 N개)")
df_sorted = origin_meta_df.sort_values(by=["조회수", "추천수"], ascending=[False, False])

# 일단 상위 100개 가져오기
for idx, data in df_sorted.head(50).iterrows():
    # 'id'에 해당하는 'tcontent' 값을 가져옴
    content = origin_df.loc[origin_df["id"] == data["id"], "tcontent"]

    # 해당 id가 origin_df에 존재하지 않는 경우 처리
    if content.empty:
        logger.warning(f"ID {data['id']}에 해당하는 tcontent가 없습니다.")
        content_value = None  # 해당 content는 None으로 처리
    else:
        content_value = content.values[0]  # 해당 id에 맞는 tcontent 값을 가져옴

    quality_df = pd.concat(
        [quality_df, pd.DataFrame({"id": [data["id"]], "tcontent": [content_value]})], ignore_index=True
    )

logger.info(f"Quality DataFrame: \n{quality_df.head()}")
