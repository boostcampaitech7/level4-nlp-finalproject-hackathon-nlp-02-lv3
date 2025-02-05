import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yaml

# Wav2CLIP import
import wav2clip

###########################
# 1) YAML 설정 로드
###########################
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

output_dir = config["output_dir"]
genre_labels = config["genre_labels"]
emotion_labels = config["emotion_labels"]

# 출력 디렉토리 확인
assert os.path.exists(output_dir), f"Output directory '{output_dir}' does not exist."

###########################
# 2) Wav2CLIP 모델 준비
###########################
# get_model() 호출로 모델 객체 생성
model = wav2clip.get_model()
# forward_audio(), forward_text() 메서드 사용 가능

###########################
# 3) 평가 함수 정의
###########################
def evaluate_audio_wav2clip(audio_path, candidate_labels):
    """
    Wav2CLIP을 이용해, 주어진 audio_path와 여러 candidate_labels(문자열) 간
    코사인 유사도를 계산하여 DataFrame으로 반환한다.
    """
    # (1) 오디오 임베딩 (배치=1, 임베딩차원=512)
    audio_emb = model.forward_audio(audio_path)  # shape: (1, 512)
    audio_vec = audio_emb[0]  # (512,)

    # (2) 각 라벨에 대해 텍스트 임베딩 계산 후 유사도
    results = []
    for label in candidate_labels:
        text_emb = model.forward_text(label)  # shape: (1, 512)
        text_vec = text_emb[0]               # (512,)

        # 코사인 유사도
        similarity = np.dot(audio_vec, text_vec) / (
            np.linalg.norm(audio_vec) * np.linalg.norm(text_vec)
        )
        results.append({
            "label": label,
            "score": float(similarity)
        })

    # DataFrame 형태로 반환
    import os
    df = pd.DataFrame(results)
    df["audio_file"] = os.path.basename(audio_path)
    df["folder"] = os.path.basename(os.path.dirname(audio_path))
    return df

###########################
# 4) 폴더 내 .wav 파일 순회
###########################
all_results = []
for root, dirs, files in os.walk(output_dir):
    for file_name in files:
        if file_name.endswith(".wav"):
            audio_path = os.path.join(root, file_name)
            try:
                # (A) 장르 점수
                df_genre = evaluate_audio_wav2clip(audio_path, genre_labels)
                df_genre["type"] = "Genre"

                # (B) 감정 점수
                df_emotion = evaluate_audio_wav2clip(audio_path, emotion_labels)
                df_emotion["type"] = "Emotion"

                # 합쳐서 저장
                combined = pd.concat([df_genre, df_emotion])
                all_results.append(combined)
            except Exception as e:
                print(f"Error processing {audio_path}: {e}")

###########################
# 5) 결과 시각화
###########################
if all_results:
    data = pd.concat(all_results, ignore_index=True)

    # 폴더별로 시각화
    for folder_name in data["folder"].unique():
        subset = data[data["folder"] == folder_name]

        # (A) Genre 시각화
        subset_genre = subset[subset["type"] == "Genre"].copy()
        subset_genre["short_label"] = subset_genre["label"].str.split(":").str[0]

        plt.figure(figsize=(12, 6))
        sns.barplot(data=subset_genre, x="short_label", y="score", hue="audio_file")
        plt.title(f"Genre Scores (Wav2CLIP) for Folder: {folder_name}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        os.makedirs("score", exist_ok=True)
        plt.savefig(f"score_wav2clip/{folder_name}_genre_scores_wav2clip.png")
        plt.close()

        # (B) Emotion 시각화
        subset_emotion = subset[subset["type"] == "Emotion"].copy()
        subset_emotion["short_label"] = subset_emotion["label"].str.split(":").str[0]

        plt.figure(figsize=(12, 6))
        sns.barplot(data=subset_emotion, x="short_label", y="score", hue="audio_file")
        plt.title(f"Emotion Scores (Wav2CLIP) for Folder: {folder_name}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"score_wav2clip/{folder_name}_emotion_scores_wav2clip.png")
        plt.close()

    print("Evaluation completed. Check 'score/' folder for plots.")
else:
    print("No results to process. Please check the output_dir for .wav files.")
