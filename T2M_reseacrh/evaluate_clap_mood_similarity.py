import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from transformers import pipeline
import torchaudio
import yaml

# YAML 파일 읽기
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# 설정 값 가져오기
output_dir = config["output_dir"]  # "generated_music/likepernumber"
input_csv = config["input_csv"]  # "refined_data/contrasted_likepernumber_input_text.csv"

# 출력 디렉토리 확인
assert os.path.exists(output_dir), f"Output directory '{output_dir}' does not exist."
assert os.path.exists(input_csv), f"Input CSV '{input_csv}' does not exist."

# CLAP (LAION) 평가 함수
def evaluate_audio_clap_laion(audio_path, candidate_labels):
    """CLAP (LAION) 모델을 사용하여 오디오의 분위기 점수를 평가"""
    # Load audio
    waveform, sample_rate = torchaudio.load(audio_path)
    mono_audio = waveform.mean(dim=0).numpy()  # Mono 처리

    # Initialize CLAP (LAION) classifier (fused version)
    audio_classifier = pipeline(
        task="zero-shot-audio-classification",
        model="laion/clap-htsat-fused"
    )

    # Run classification
    output = audio_classifier(mono_audio, candidate_labels=candidate_labels)

    # Convert to DataFrame
    scores = pd.DataFrame(output)
    return scores

def evaluate_audio_mood_scores(audio_path, positive_label, negative_label):
    """
    주어진 오디오 파일에 대해 CLAP 점수를 계산하고,
    positive_mood 및 negative_mood의 점수를 반환하는 함수.

    Args:
        audio_path (str): 평가할 오디오 파일 경로
        positive_label (str): 긍정적인 분위기 라벨
        negative_label (str): 부정적인 분위기 라벨

    Returns:
        dict: {"positive_score": float, "negative_score": float}
    """
    if not os.path.exists(audio_path):
        print(f"⚠️ 파일 없음: {audio_path}, 건너뜁니다.")
        return None

    try:
        scores = evaluate_audio_clap_laion(audio_path, [positive_label, negative_label])

        # 분위기 점수를 추출
        positive_score = scores[scores["label"] == positive_label]["score"].values[0]
        negative_score = scores[scores["label"] == negative_label]["score"].values[0]

        return {"positive_score": positive_score, "negative_score": negative_score}

    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None


############################
#        실행 파트
############################
# CSV 파일 로드
df_input = pd.read_csv(input_csv)

# 결과 저장 리스트
results = []
low_positive_ids = []  # Positive 점수가 낮은 ID 목록

threshold = 0.5  # ✅ 재생성 기준으로 활용할 수 있는 최소 Positive 점수

for idx, row in df_input.iterrows():
    audio_id = row["id"]
    audio_path = os.path.join(output_dir, f"{audio_id}.wav")

    # CLAP 점수 평가
    mood_scores = evaluate_audio_mood_scores(audio_path, row["positive_mood"], row["negative_mood"])
    
    if mood_scores:
        # 결과 저장
        results.append({
            "id": audio_id,
            "mood_type": "positive_mood",
            "score": mood_scores["positive_score"]
        })
        results.append({
            "id": audio_id,
            "mood_type": "negative_mood",
            "score": mood_scores["negative_score"]
        })

        # ✅ Positive 점수가 특정 임계값(threshold) 이하일 경우 저장
        if mood_scores["positive_score"] < threshold:
            low_positive_ids.append(audio_id)

# 결과를 데이터프레임으로 결합
if results:
    df_results = pd.DataFrame(results)

    # ✅ Positive Mood의 점수가 0.5 미만인 ID 목록을 별도 저장
    if len(low_positive_ids) > 0:
        print("\n⚠️ Positive Mood 점수가 0.5 미만인 ID 목록:")
        for low_id in low_positive_ids:
            print(f"   - {low_id}")

        # ID 리스트를 파일로 저장
        os.makedirs("score_clapla", exist_ok=True)
        with open("score_clapla/low_positive_mood_ids.txt", "w") as f:
            f.write("\n".join(map(str, low_positive_ids)))
        print("✅ Low Positive Mood ID 리스트 저장됨: score_clapla/low_positive_mood_ids.txt")

    # ✅ ID별 positive_mood vs negative_mood 점수 비교 그래프
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_results, x="mood_type", y="score", hue="id", dodge=True)
    plt.title("Positive vs Negative Mood CLAP Scores by ID(like)")
    plt.xlabel("Mood Type")
    plt.ylabel("CLAP Score")
    plt.legend(title="Audio ID", bbox_to_anchor=(1.05, 1), loc='upper left')  # 범례 위치 조정
    plt.xticks(rotation=0)
    plt.tight_layout()

    # 결과 폴더 생성 및 저장
    plt.savefig("score_clapla/likepernumber_mood_comparison.png")
    plt.close()

    print("✅ CLAP 점수 분석 완료! 그래프 저장됨: score_clapla/likepernumber_mood_comparison.png")
else:
    print("❌ 처리할 결과가 없습니다. .wav 파일을 확인하세요.")
