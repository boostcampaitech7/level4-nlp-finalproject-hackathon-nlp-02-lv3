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
novels = config["novels"]
output_dir = config["output_dir"]
num_samples_per_prompt = config["num_samples_per_prompt"]
summary_dir = config["summary_dir"]
genre_labels = config["genre_labels"]
emotion_labels = config["emotion_labels"]

# 출력 디렉토리 확인
assert os.path.exists(output_dir), f"Output directory '{output_dir}' does not exist. Please generate audio files first."

# CLAP 점수 평가 함수
def evaluate_audio_clap(audio_path, candidate_labels):
    # Load audio
    waveform, sample_rate = torchaudio.load(audio_path)
    mono_audio = waveform.mean(dim=0).numpy()  # Mono 처리

    # Initialize CLAP classifier
    audio_classifier = pipeline(
        task="zero-shot-audio-classification",
        model="laion/clap-htsat-unfused"
    )

    # Run classification
    output = audio_classifier(mono_audio, candidate_labels=candidate_labels)

    # Convert to DataFrame
    scores = pd.DataFrame(output)
    scores["audio_file"] = os.path.basename(audio_path)
    return scores

# 저장된 파일에 대한 평가 결과 수집
results = []
for file_name in os.listdir(output_dir):
    if file_name.endswith(".wav"):  # WAV 파일만 처리
        audio_path = os.path.join(output_dir, file_name)
        try:
            # 장르 점수 계산
            genre_scores = evaluate_audio_clap(audio_path, genre_labels)
            genre_scores["type"] = "Genre"

            # 감정 점수 계산
            emotion_scores = evaluate_audio_clap(audio_path, emotion_labels)
            emotion_scores["type"] = "Emotion"

            # 결과 합치기
            results.append(pd.concat([genre_scores, emotion_scores]))
        except Exception as e:
            print(f"Error processing {audio_path}: {e}")

# 결과를 데이터프레임으로 결합
if results:
    data = pd.concat(results, ignore_index=True)

    # 웹소설별 점수 분석 및 시각화
    for novel_name in novels:
        subset = data[data["audio_file"].str.contains(novel_name)]

        # Genre 점수 시각화
        plt.figure(figsize=(12, 6))
        subset_genre = subset[subset["type"] == "Genre"].copy()
        subset_genre["short_label"] = subset_genre["label"].str.split(":").str[0]  # ":" 앞부분 추출

        sns.barplot(data=subset_genre, x="short_label", y="score", hue="audio_file")
        plt.title(f"Genre Scores for {novel_name}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{novel_name}_genre_scores.png")
        plt.close()

        # Emotion 점수 시각화
        plt.figure(figsize=(12, 6))
        subset_emotion = subset[subset["type"] == "Emotion"].copy()
        subset_emotion["short_label"] = subset_emotion["label"].str.split(":").str[0]  # ":" 앞부분 추출

        sns.barplot(data=subset_emotion, x="short_label", y="score", hue="audio_file")
        plt.title(f"Emotion Scores for {novel_name}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{novel_name}_emotion_scores.png")
        plt.close()
else:
    print("No results to process. Please check the generated_music directory.")
