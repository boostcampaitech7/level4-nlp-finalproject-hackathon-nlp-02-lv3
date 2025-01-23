from diffusers import AudioLDM2Pipeline
import torch
import scipy
import os
import yaml

# YAML 파일 읽기
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# 설정 값 가져오기
novels = config["novels"]
output_dir = config["output_dir"]
summary_dir = config["summary_dir"]
num_samples_per_prompt = config["num_samples_per_prompt"]
duration_sec = config["duration_sec"]

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# GPU 설정
gpu_id = 1  # 사용할 GPU ID를 지정
torch.cuda.set_device(gpu_id)  # 선택한 GPU를 설정

# AudioLDM 모델 로드
repo_id = "cvssp/audioldm2"
pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch.float16)
pipe = pipe.to(f"cuda:{gpu_id}")  # 선택한 GPU로 이동

def load_summary(novel_name, summary_dir):
    """소설 이름에 해당하는 요약 파일 읽기"""
    summary_file = os.path.join(summary_dir, f"{novel_name}.txt")
    if os.path.exists(summary_file):
        with open(summary_file, "r") as file:
            return file.read().strip()
    else:
        print(f"Summary file not found for {novel_name}")
        return None

def generate_and_save_audio(novel_name, prompt_text, sample_index, duration):
    """오디오 생성 및 저장"""
    print(f"Generating: Novel={novel_name}, Sample={sample_index + 1}")
    audio = pipe(prompt_text, num_inference_steps=200, audio_length_in_s=duration).audios[0]

    # 파일명 생성 및 저장
    output_file = os.path.join(output_dir, f"AudioLDM2-{novel_name}-{sample_index + 1}.wav")
    scipy.io.wavfile.write(output_file, rate=32000, data=audio)
    print(f"Audio saved as {output_file}")

# 각 소설에 대해 오디오 생성
for novel_name in novels:
    prompt_text = load_summary(novel_name, summary_dir)
    if prompt_text:
        for sample_index in range(num_samples_per_prompt):
            generate_and_save_audio(novel_name, prompt_text, sample_index, duration_sec)
