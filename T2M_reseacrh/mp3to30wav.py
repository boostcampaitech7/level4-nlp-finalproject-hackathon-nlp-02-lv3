import os
from pydub import AudioSegment

def split_mp3_to_wav_chunks(origin_dir='origin_music', sep_dir='sep_music', chunk_seconds=30):
    # sep_music 폴더가 없으면 생성
    if not os.path.exists(sep_dir):
        os.makedirs(sep_dir)

    # origin_dir 내부의 파일들 순회
    for filename in os.listdir(origin_dir):
        if filename.lower().endswith('.mp3'):
            # mp3 파일 경로
            mp3_path = os.path.join(origin_dir, filename)
            
            # AudioSegment로 불러오기
            audio = AudioSegment.from_mp3(mp3_path)
            duration_ms = len(audio)  # 오디오 전체 길이(밀리초)
            
            chunk_length_ms = chunk_seconds * 1000
            
            # 30초 단위로 잘라낼 수 있는 횟수(정확히 나누어떨어지는 구간 수)
            full_chunks_count = duration_ms // chunk_length_ms
            remainder = duration_ms % chunk_length_ms
            
            # 파일 이름에서 확장자를 뺀 부분(출력 wav 파일 이름에 사용)
            base_name = os.path.splitext(filename)[0]
            
            # 1) 30초 단위로 나누어서 저장
            for i in range(full_chunks_count):
                start_ms = i * chunk_length_ms
                end_ms = start_ms + chunk_length_ms
                chunk_audio = audio[start_ms:end_ms]
                
                # part{i} 형식으로 파일명 지정
                chunk_filename = f"{base_name}_part{i}.wav"
                chunk_path = os.path.join(sep_dir, chunk_filename)
                
                # wav 형식으로 내보내기
                chunk_audio.export(chunk_path, format="wav")
                print(f"Saved: {chunk_path}")
            
            # 2) 30초 단위로 딱 떨어지지 않는다면, 마지막 구간 대신 파일 끝에서 30초 추출
            if remainder != 0:
                last_chunk_audio = audio[-chunk_length_ms:]  # 끝에서부터 30초
                last_chunk_filename = f"{base_name}_last.wav"
                last_chunk_path = os.path.join(sep_dir, last_chunk_filename)
                
                last_chunk_audio.export(last_chunk_path, format="wav")
                print(f"Saved: {last_chunk_path}")

if __name__ == "__main__":
    split_mp3_to_wav_chunks(
        origin_dir='origin_music',  # MP3 원본 폴더
        sep_dir='sep_music',        # 잘린 WAV가 저장될 폴더
        chunk_seconds=30            # 30초 단위
    )
