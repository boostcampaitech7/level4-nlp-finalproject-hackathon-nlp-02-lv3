from audiocraft.models import musicgen
from audiocraft.utils.notebook import display_audio
import torch
import torchaudio
import os

# 입력 프롬프트 설정
prompts = {
    "preson_teacher": "A sweeping orchestral score with gentle piano, bittersweet strings, and a subtle sense of determination, evoking both longing and the quiet resolve of a noble seeking a new future.",
    "Buja": "A bold and triumphant stadium-rock anthem with driving percussion, powerful brass, and an energetic build, capturing the electric excitement of a high-stakes World Cup marketing gamble.",
    "onlylevel": "A haunting, cinematic track with ethereal synth pads, distant choirs, and a slow-burning orchestral build, echoing the lonely drift through space and the final stand of a weary warrior.",
    "knife_fight": "A powerful, cinematic orchestral track with thunderous percussion, driving strings, and an undercurrent of ruthless intensity, capturing the lethal tension of a blood-soaked showdown on the river."
}

# 모델 크기 설정
model_sizes = ["small", "medium", "large", "melody"]

# 출력 디렉토리 설정
output_dir = "generated_music"
os.makedirs(output_dir, exist_ok=True)

# 샘플 수 설정
num_samples_per_prompt = 3

def save_audio(model, prompt_key, prompt_text, model_size, sample_index):
    # 생성 파라미터 설정
    model.set_generation_params(duration=30)

    # 텍스트 프롬프트로 음악 생성
    res = model.generate([prompt_text], progress=True)

    # 생성된 오디오 데이터를 저장
    audio_data = res[0]
    if audio_data.dim() == 1:  # 텐서가 1D라면
        audio_data = audio_data.unsqueeze(0)  # 배치 차원 추가 (채널 x 샘플)

    # 파일명 생성 및 저장
    output_file = os.path.join(output_dir, f"MusicGen-{model_size}-{prompt_key}-{sample_index + 1}.wav")
    torchaudio.save(output_file, audio_data.cpu(), sample_rate=32000)
    print(f"Music saved as {output_file}")

# 모델별 음악 생성
for model_size in model_sizes:
    print(f"Loading model: {model_size}")
    model = musicgen.MusicGen.get_pretrained(model_size, device="cuda")

    for prompt_key, prompt_text in prompts.items():
        for sample_index in range(num_samples_per_prompt):
            print(f"Generating: Model={model_size}, Prompt={prompt_key}, Sample={sample_index + 1}")
            save_audio(model, prompt_key, prompt_text, model_size, sample_index)




















# from audiocraft.models import musicgen
# from audiocraft.utils.notebook import display_audio
# import torch
# import torchaudio

# # MusicGen 모델 로드
# default_model = musicgen.MusicGen.get_pretrained('small', device='cuda')

# # 생성 파라미터 설정
# default_model.set_generation_params(duration=30)

# # 텍스트 프롬프트로 음악 생성
# res = default_model.generate([
#     "A powerful, cinematic orchestral track with thunderous percussion, driving strings, and an undercurrent of ruthless intensity, capturing the lethal tension of a blood-soaked showdown on the river."
# ], progress=True)


# # 생성된 오디오 데이터를 .wav 파일로 저장
# output_file = "test-medium.wav"

# # 차원 확인 및 수정 (2D로 변환)
# audio_data = res[0]  # 배치에서 첫 번째 생성물 선택
# if audio_data.dim() == 1:  # 텐서가 1D라면
#     audio_data = audio_data.unsqueeze(0)  # 배치 차원 추가 (채널 x 샘플)

# # 저장
# torchaudio.save(output_file, audio_data.cpu(), sample_rate=32000)

# print(f"Music saved as {output_file}")
