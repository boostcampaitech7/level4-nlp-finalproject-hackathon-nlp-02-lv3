import json
import urllib.request
from loguru import logger
import yaml

def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

config_api = load_config("../config/config_api.yaml")

client_id = config_api["TRANSLATOR"]["CLIENT_ID"]
client_secret = config_api["TRANSLATOR"]["CLIENT_SECRET"]
url = config_api["TRANSLATOR"]["URL"]

class Translator():
    @staticmethod
    def Translate(kr_content: str) -> str : # KR -> US 문장

        if not kr_content or not isinstance(kr_content, str): # 번역할 문장이 비어있지 않을 경우 수행
            logger.warning("번역할 문장이 비어있거나, 잘못된 Type입니다.")
            return "번역 실패"
        
        encText = urllib.parse.quote(kr_content)
            
        data = f"source=ko&target=en&text={encText}"
        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
        request.add_header("X-NCP-APIGW-API-KEY", client_secret)

        try:
            response = urllib.request.urlopen(request, data=data.encode("utf-8"))
            rescode = response.getcode()

            if rescode == 200:
                response_body = response.read()
                response_json = json.loads(response_body.decode("utf-8")) 

                translated_text = response_json.get("message", {}).get("result", {}).get("translatedText", "번역 실패")
                    
                logger.info(f"번역 성공:\n{translated_text[:100]}...")
                return translated_text

            else:
                logger.error(f"번역 실패: API 상태 코드 {rescode}")
                return "번역 실패"

        except Exception as e:
            logger.exception(f"번역 요청 중 오류 발생: {str(e)}")
            return "번역 실패"