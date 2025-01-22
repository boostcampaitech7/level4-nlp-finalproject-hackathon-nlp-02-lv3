from diffusers import AudioLDM2Pipeline
import torch
import scipy
import os

# 출력 디렉토리 설정
output_dir = "audioldm_generated_music"
os.makedirs(output_dir, exist_ok=True)

# 입력 프롬프트 설정
prompts = {
    "preson_teacher": "A sweeping orchestral score with gentle piano, bittersweet strings, and a subtle sense of determination, evoking both longing and the quiet resolve of a noble seeking a new future.",
    "Buja": "A bold and triumphant stadium-rock anthem with driving percussion, powerful brass, and an energetic build, capturing the electric excitement of a high-stakes World Cup marketing gamble.",
    "onlylevel": "A haunting, cinematic track with ethereal synth pads, distant choirs, and a slow-burning orchestral build, echoing the lonely drift through space and the final stand of a weary warrior.",
    "knife_fight": "A powerful, cinematic orchestral track with thunderous percussion, driving strings, and an undercurrent of ruthless intensity, capturing the lethal tension of a blood-soaked showdown on the river."
}

# GPU 설정
gpu_id = 1  # 사용할 GPU ID를 지정
torch.cuda.set_device(gpu_id)  # 선택한 GPU를 설정

# AudioLDM 모델 로드
repo_id = "cvssp/audioldm2"
pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch.float16)
pipe = pipe.to(f"cuda:{gpu_id}")  # 선택한 GPU로 이동

# 샘플 수 설정
num_samples_per_prompt = 3

def generate_and_save_audio(prompt_key, prompt_text, sample_index):
    print(f"Generating: Prompt={prompt_key}, Sample={sample_index + 1}")
    audio = pipe(prompt_text, num_inference_steps=200, audio_length_in_s=60.0).audios[0]

    # 파일명 생성 및 저장
    output_file = os.path.join(output_dir, f"AudioLDM-{prompt_key}-{sample_index + 1}.wav")
    scipy.io.wavfile.write(output_file, rate=32000, data=audio)
    print(f"Audio saved as {output_file}")

# 각 프롬프트에 대해 오디오 생성
for prompt_key, prompt_text in prompts.items():
    for sample_index in range(num_samples_per_prompt):
        generate_and_save_audio(prompt_key, prompt_text, sample_index)



# from diffusers import AudioLDM2Pipeline
# import torch
# import scipy


# gpu_id = 1  # 사용할 GPU ID를 지정
# torch.cuda.set_device(gpu_id)  # 선택한 GPU를 설정

# repo_id = "cvssp/audioldm2"
# pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch.float16)
# pipe = pipe.to(f"cuda:{gpu_id}")  # 선택한 GPU로 이동

# #text prompt 
# prompt = "A powerful, cinematic orchestral track with thunderous percussion, driving strings, and an undercurrent of ruthless intensity, capturing the lethal tension of a blood-soaked showdown on the river."
# audio = pipe(prompt, num_inference_steps=200, audio_length_in_s=60.0).audios[0]
# # audio_length_in_s = 생성 음악 시간.

# audiofile_name = "knife-fight1.wav"
# scipy.io.wavfile.write(audiofile_name, rate=32000, data=audio)