from audiocraft.models import musicgen
import torchaudio
import yaml
import os

# YAML 파일 읽기
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# 설정 값 가져오기
novels = config["novels"]
output_dir = config["output_dir"]
num_samples_per_prompt = config["num_samples_per_prompt"]
summary_dir = config["summary_dir"]
duration_sec = config["duration_sec"]  # 음악 생성 길이

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 모델 크기 설정
model_sizes = ["small", "medium", "large", "melody"]

def load_summary(novel_name, summary_dir):
    """소설 이름에 해당하는 요약 파일 읽기"""
    summary_file = os.path.join(summary_dir, f"{novel_name}.txt")
    if os.path.exists(summary_file):
        with open(summary_file, "r") as file:
            return file.read().strip()
    else:
        print(f"Summary file not found for {novel_name}")
        return None

def save_audio(model, novel_name, prompt_text, model_size, sample_index, duration):
    # 생성 파라미터 설정
    model.set_generation_params(duration=duration)

    # 텍스트 프롬프트로 음악 생성
    res = model.generate([prompt_text], progress=True)

    # 생성된 오디오 데이터를 저장
    audio_data = res[0]
    if audio_data.dim() == 1:  # 텐서가 1D라면
        audio_data = audio_data.unsqueeze(0)  # 배치 차원 추가 (채널 x 샘플)

    # 파일명 생성 및 저장
    output_file = os.path.join(output_dir, f"MusicGen-{model_size}-{novel_name}-{sample_index + 1}.wav")
    torchaudio.save(output_file, audio_data.cpu(), sample_rate=32000)
    print(f"Music saved as {output_file}")

# 모델별 음악 생성
for model_size in model_sizes:
    print(f"Loading model: {model_size}")
    model = musicgen.MusicGen.get_pretrained(model_size, device="cuda")

    for novel_name in novels:
        prompt_text = load_summary(novel_name, summary_dir)
        if prompt_text:
            for sample_index in range(num_samples_per_prompt):
                print(f"Generating: Model={model_size}, Novel={novel_name}, Sample={sample_index + 1}")
                save_audio(model, novel_name, prompt_text, model_size, sample_index, duration_sec)
