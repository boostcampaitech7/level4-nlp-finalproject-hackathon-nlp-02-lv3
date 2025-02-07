import subprocess
import urllib.request
import sys
import os
import pandas as pd

# 실행할 Python 파일 및 간략한 설명
CHECK_INPUT_TEXT_QUALITY = "check_input_text_quality.py"
FILTER_INPUT_TEXT_BY_ID = "filter_input_text_by_id.py"
CLEAN_FILTERED_INPUT_TEXT = "clean_filtered_input_text.py"
GENERATE_CONTRASTIVE_PROMPTS = "generate_contrastive_prompts.py"
MUSICGEN_BASIC = "musicgen_basic.py"
UPDATE_FAILED_MOOD_DATA = "update_failed_mood_data.py"

print("🔍 T2M 연구 프로젝트 스크립트 실행을 시작합니다.\n")

print("⚠️ 이 실행을 위해서는 requirements 설치 및 config_api.yaml에 API 정보 추가가 필요합니다.")
user_input = input("계속 진행하시겠습니까? (y/n): ").strip().lower()

# 🔍 사용자의 입력값 확인
if user_input != 'y':
    print("❌ 실행이 취소되었습니다.")
    sys.exit(0)



# 1️⃣ Check Input Text Quality
print("📝 [Step 1] 입력 텍스트 품질 검사")
print("  check_input_text_quality.py  → 입력된 텍스트 데이터의 품질을 분석하고 평가하는 코드입니다.")
print("입력 데이터 : 1480의 id, input_text 컬럼을 가지는 raw_data/input_text.csv")
print("출력 데이터 : 없음")


print("📝 필요 데이터 다운로드중..")

# Google Drive에서 다운로드할 파일의 ID
FILE_ID = "1NRhquhVtdlZxjZuYmOwfvw2VuKLqkgo_"  
OUTPUT_FILE = "raw_data/input_text.csv"  # 저장할 파일명
# Google Drive 직접 다운로드 URL
GDRIVE_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
# 파일 다운로드
urllib.request.urlretrieve(GDRIVE_URL, OUTPUT_FILE)

print(f"✅ 필요 데이터 파일 다운로드 완료: {OUTPUT_FILE}")

try:
    subprocess.run(["python", CHECK_INPUT_TEXT_QUALITY], check=True)
    print("✅ 실행 완료: check_input_text_quality.py\n")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 실패: {CHECK_INPUT_TEXT_QUALITY}\n  오류 메시지: {e}\n")


# 2️⃣ Filter Input Text by ID
print("🔍 [Step 2] ID 기반 입력 텍스트 필터링")
print("    → 특정 ID를 기준으로 불필요한 텍스트를 제거합니다.")
print("  filter_input_text_by_id.py  → 전체 input_text중 품질이 좋은 데이터만 선별하여 별도로 저장하는 역할입니다.")
print("입력 데이터 : like기준으로 품질이 좋은 상위 100개의 데이터파일 novel_content_100_likes.csv")
print("입력 데이터 : likeperson기준으로 품질이 좋은 상위 100개의 데이터파일 novel_content_100_likespernumber.csv")
print("출력 데이터 : like기준으로 상위 100개의 id, input_text 컬럼을 가지는 raw_data/like_input_text.csv.csv")
print("출력 데이터 : likeperson 기준으로 상위 100개의 id, input_text 컬럼을 가지는 raw_data/likepernumber_input_text.csv")

print("📝 필요 데이터 다운로드 중..")

# 🔹 입력 데이터 1: like 기준으로 품질이 좋은 상위 100개 데이터 파일
FILE_ID_1 = "1NT_-7_CKn2IILtrwnhmNbYjDxLdRA1uL"  
OUTPUT_FILE_1 = "refined_data/novel_content_100_likes.csv"
# Google Drive 직접 다운로드 URL
GDRIVE_URL_1 = f"https://drive.google.com/uc?export=download&id={FILE_ID_1}"
# 파일 다운로드
urllib.request.urlretrieve(GDRIVE_URL_1, OUTPUT_FILE_1)
print(f"✅ 필요 데이터 파일 다운로드 완료: {OUTPUT_FILE_1}")

# 🔹 입력 데이터 2: likeperson 기준으로 품질이 좋은 상위 100개 데이터 파일
FILE_ID_2 = "1muqZGG4Ju55Cf62M39mHRo6h6i8xzPc1"
OUTPUT_FILE_2 = "refined_data/novel_content_100_likespernumber.csv"
# Google Drive 직접 다운로드 URL
GDRIVE_URL_2 = f"https://drive.google.com/uc?export=download&id={FILE_ID_2}"
# 파일 다운로드
urllib.request.urlretrieve(GDRIVE_URL_2, OUTPUT_FILE_2)
print(f"✅ 필요 데이터 파일 다운로드 완료: {OUTPUT_FILE_2}")


try:
    subprocess.run(["python", FILTER_INPUT_TEXT_BY_ID], check=True)
    print("✅ 실행 완료: filter_input_text_by_id.py\n")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 실패: {FILTER_INPUT_TEXT_BY_ID}\n  오류 메시지: {e}\n")

# 3️⃣ Clean Filtered Input Text

print("🧹 [Step 3] 필터링된 입력 텍스트 정리")
print("  clean_filtered_input_text.py  → 정제된 데이터를 저장하고 불필요한 기호나 공백을 제거합니다.")
print("입력 데이터 : like기준으로 상위 100개의 id, input_text 컬럼을 가지는 raw_data/like_input_text.csv.csv")
print("입력 데이터 : likeperson 기준으로 상위 100개의 id, input_text 컬럼을 가지는 raw_data/likepernumber_input_text.csv")
print("생성 데이터 : 해당 데이터의 중복데이터를 정리한 cleaned_like_input_text.csv")
print("생성 데이터 : 해당 데이터의 중복데이터를 정리한 cleaned_likepernumber_input_text.csv")
try:
    subprocess.run(["python", CLEAN_FILTERED_INPUT_TEXT], check=True)
    print("✅ 실행 완료: clean_filtered_input_text.py\n")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 실패: {CLEAN_FILTERED_INPUT_TEXT}\n  오류 메시지: {e}\n")

# 4️⃣ Generate Contrastive Prompts (대조문장 생성)
print("🔄 [Step 4] 대조 문장 생성")
print("  generate_contrastive_prompts.py  → 원본 문장과 반대되는 의미의 문장을 생성하여 비교 분석합니다.")
print("위의 데이터는 100개가 아니기 때문에 정확히 100개씩 작업된 데이터를 다시 불러옵니다. 그리고 테스트편의성을 위해 상위 3개의 행만 테스트합니다.")
print("생성 데이터 : 음악생성을 위한 contrasted_likepernumber_input_text.csv")

FILE_ID_1 = "1epPvcJJtC67yMlEWsBfQYRibkdMOoV2-"
OUTPUT_FILE_1 = "refined_data/novel_content_100_likes_input_text.csv"
GDRIVE_URL_1 = f"https://drive.google.com/uc?export=download&id={FILE_ID_1}"
FILE_ID_2 = "1r8O6fSPj2Ia-0xPypUUVJf6MZvgyPCxH"
OUTPUT_FILE_2 = "refined_data/novel_content_100_likespernumber_input_text.csv"
GDRIVE_URL_2 = f"https://drive.google.com/uc?export=download&id={FILE_ID_2}"
urllib.request.urlretrieve(GDRIVE_URL_2, OUTPUT_FILE_2)
print(f"✅ 필요 데이터 파일 다운로드 완료: {OUTPUT_FILE_2}\n")
urllib.request.urlretrieve(GDRIVE_URL_1, OUTPUT_FILE_1)
print(f"✅ 필요 데이터 파일 다운로드 완료: {OUTPUT_FILE_1}\n")
# 📥 CSV 파일 불러오기
df = pd.read_csv(OUTPUT_FILE_2)
# 🔍 상위 3개 행만 유지
df_top3 = df.head(3)
# 💾 동일한 파일명으로 다시 저장 (기존 데이터 덮어쓰기)
df_top3.to_csv(OUTPUT_FILE_2, index=False)

try:
    subprocess.run(["python", GENERATE_CONTRASTIVE_PROMPTS], check=True)
    print("✅ 실행 완료: generate_contrastive_prompts.py\n")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 실패: {GENERATE_CONTRASTIVE_PROMPTS}\n  오류 메시지: {e}\n")

# 5️⃣ MusicGen 기본 실행
print("🎵 [Step 5] MusicGen 모델 실행")
print(" musicgen_basic.py  → 텍스트를 기반으로 음악을 생성하는 핵심 T2M 모델 실행")
try:
    subprocess.run(["python", MUSICGEN_BASIC], check=True)
    print("✅ 실행 완료: musicgen_basic.py\n")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 실패: {MUSICGEN_BASIC}\n  오류 메시지: {e}\n")

# 6️⃣ Update Failed Mood Data
print("🛠️ [Step 6] 실패한 감정 데이터 업데이트")
print("  update_failed_mood_data.py  → CLAP 평가에서 낮은 점수를 얻어 생성되지 않은 wav 데이터를 찾고, 해당 id의 positive mood와 negative mood를 재생성합니다.")
print("확인을 위해 임시로 만들어진 wav파일을 하나 삭제 후 코드를 실행합니다. 그리고 다시 음악을 생성합니다")

file_path = "generated_music/likepernumber/450006.wav"
if os.path.exists(file_path):
    os.remove(file_path)
try:
    subprocess.run(["python", UPDATE_FAILED_MOOD_DATA], check=True)
    print("✅ 실행 완료: update_failed_mood_data.py\n")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 실패: {UPDATE_FAILED_MOOD_DATA}\n  오류 메시지: {e}\n")

print(" musicgen_basic.py  → 텍스트를 기반으로 음악을 생성하는 핵심 T2M 모델 재 실행")
try:
    subprocess.run(["python", MUSICGEN_BASIC], check=True)
    print("✅ 실행 완료: musicgen_basic.py\n")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 실패: {MUSICGEN_BASIC}\n  오류 메시지: {e}\n")


print("\n✅ 모든 스크립트 실행이 완료되었습니다.")
