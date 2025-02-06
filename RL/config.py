import os

from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()

# 환경 변수 불러오기
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
CLOVA_API_KEY = os.getenv("API_KEY")
