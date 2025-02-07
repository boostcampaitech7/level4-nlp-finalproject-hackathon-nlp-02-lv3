import subprocess

# 실행할 Python 파일들을 변수로 저장
CHECK_INPUT_TEXT_QUALITY = "check_input_text_quality.py"
CLEAN_FILTERED_INPUT_TEXT = "clean_filtered_input_text.py"
FILTER_INPUT_TEXT_BY_ID = "filter_input_text_by_id.py"
GENERATE_CONTRASTIVE_PROMPTS = "generate_contrastive_prompts.py"
EVALUATE_CLAP_MOOD_SIMILARITY = "evaluate_clap_mood_similarity.py"
MUSICGEN_BASIC = "musicgen_basic.py"
UPDATE_FAILED_MOOD_DATA = "update_failed_mood_data.py"

# 실행할 파일 리스트
python_files = [
    CHECK_INPUT_TEXT_QUALITY,
    CLEAN_FILTERED_INPUT_TEXT,
    FILTER_INPUT_TEXT_BY_ID,
    GENERATE_CONTRASTIVE_PROMPTS,
    EVALUATE_CLAP_MOOD_SIMILARITY,
    MUSICGEN_BASIC,
    UPDATE_FAILED_MOOD_DATA
]

# 실행 결과 저장
results = {}

# 각 파일 실행 및 결과 확인
for file in python_files:
    print(f"🔄 실행 중: {file}")
    try:
        result = subprocess.run(["python", file], capture_output=True, text=True, check=True)
        results[file] = ("✅ 성공", result.stdout)
    except subprocess.CalledProcessError as e:
        results[file] = ("❌ 실패", e.stderr)

# 실행 결과 출력
print("\n=== 실행 결과 ===")
for file, (status, output) in results.items():
    print(f"{status} | {file}")
    if status == "❌ 실패":
        print(f"  오류 메시지: {output}")
    print("-" * 40)
