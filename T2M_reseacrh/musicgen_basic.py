from audiocraft.models import musicgen
import torchaudio
import yaml
import os
import csv
from tqdm import tqdm
import torch

# YAML 파일 읽기
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# 설정 값 가져오기
input_csv   = config["input_csv"]
output_dir  = config["output_dir"]
duration_sec= config["duration_sec"]
model_size  = config["model_size"]

# GPU device 번호를 코드 내에서 직접 설정 (예: 0번 GPU 사용)
gpu_device_index = 0  # 원하는 GPU 번호를 여기에 지정 (예: 0 또는 1)
torch.cuda.set_device(gpu_device_index)
device_for_model = "cuda"  # autocast 등 내부 모듈은 "cuda"만 허용합니다.

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 모델 로드 (지정한 GPU 사용)
print(f"Loading model: {model_size} on GPU device {gpu_device_index}")
model = musicgen.MusicGen.get_pretrained(model_size, device=device_for_model)

# CSV 파일에서 프롬프트 데이터 읽기
with open(input_csv, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))
    for row in tqdm(reader, desc="Generating music"):
        file_id     = row["id"]
        prompt_text = row["musicgen_input_text"]

        # 생성 파라미터 설정
        model.set_generation_params(duration=duration_sec)

        # 텍스트 프롬프트를 기반으로 음악 생성
        res = model.generate([prompt_text], progress=True)

        # 생성된 오디오 데이터를 저장 (1D 텐서라면 배치 차원 추가)
        audio_data = res[0]
        if audio_data.dim() == 1:
            audio_data = audio_data.unsqueeze(0)

        # 파일명은 id_1.wav 로 저장
        output_file = os.path.join(output_dir, f"{file_id}_2.wav")
        torchaudio.save(output_file, audio_data.cpu(), sample_rate=32000)
        print(f"Music saved as {output_file}")
