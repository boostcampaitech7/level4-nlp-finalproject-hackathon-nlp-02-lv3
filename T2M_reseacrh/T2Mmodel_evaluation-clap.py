import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from transformers import pipeline
import torchaudio

# 입력 프롬프트 설정
prompts = {
    "preson_teacher": "A sweeping orchestral score with gentle piano, bittersweet strings, and a subtle sense of determination, evoking both longing and the quiet resolve of a noble seeking a new future.",
    "Buja": "A bold and triumphant stadium-rock anthem with driving percussion, powerful brass, and an energetic build, capturing the electric excitement of a high-stakes World Cup marketing gamble.",
    "onlylevel": "A haunting, cinematic track with ethereal synth pads, distant choirs, and a slow-burning orchestral build, echoing the lonely drift through space and the final stand of a weary warrior.",
    "knife_fight": "A powerful, cinematic orchestral track with thunderous percussion, driving strings, and an undercurrent of ruthless intensity, capturing the lethal tension of a blood-soaked showdown on the river."
}

# 모델 크기 설정s
model_sizes = ["small", "medium", "large", "melody"]

# 출력 디렉토리 설정
output_dir = "generated_music"
assert os.path.exists(output_dir), f"Output directory '{output_dir}' does not exist. Please generate audio files first."

# 평가 기준 설정
genre_labels = ["Romance", "Fantasy", "Martial Arts", "Mystery", "Thriller", "Science", "Game", "Detective"]
emotion_labels = ["Joy", "Sadness", "Fear", "Excitement", "Calm", "Anger", "Surprise", "Longing", "Immersion"]

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
for model_size in model_sizes:
    for prompt_key in prompts.keys():
        for sample_index in range(3):
            audio_path = os.path.join(output_dir, f"MusicGen-{model_size}-{prompt_key}-{sample_index + 1}.wav")
            if os.path.exists(audio_path):
                genre_scores = evaluate_audio_clap(audio_path, genre_labels)
                genre_scores["type"] = "Genre"

                emotion_scores = evaluate_audio_clap(audio_path, emotion_labels)
                emotion_scores["type"] = "Emotion"

                results.append(pd.concat([genre_scores, emotion_scores]))
            else:
                print(f"File not found: {audio_path}")

# 결과를 데이터프레임으로 결합
data = pd.concat(results, ignore_index=True)

# 웹소설별 점수 분석 및 시각화
for prompt_key in prompts.keys():
    subset = data[data["audio_file"].str.contains(prompt_key)]

    # Genre 점수 시각화
    plt.figure(figsize=(12, 6))
    sns.barplot(data=subset[subset["type"] == "Genre"], x="label", y="score", hue="audio_file")
    plt.title(f"Genre Scores for {prompt_key}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{prompt_key}_genre_scores.png")
    plt.close()

    # Emotion 점수 시각화
    plt.figure(figsize=(12, 6))
    sns.barplot(data=subset[subset["type"] == "Emotion"], x="label", y="score", hue="audio_file")
    plt.title(f"Emotion Scores for {prompt_key}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{prompt_key}_emotion_scores.png")
    plt.close()
