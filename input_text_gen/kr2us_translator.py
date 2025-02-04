import json
import urllib.request

import yaml


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


config_api = load_config("../config/config_api.yaml")

client_id = config_api["TRANSLATOR"]["CLIENT_ID"]
client_secret = config_api["TRANSLATOR"]["CLIENT_SECRET"]
url = config_api["TRANSLATOR"]["URL"]

text_to_translate = input("번역할 문장을 입력하세요: ").strip()

if text_to_translate:  # 번역할 문장이 비어있지 않을 경우 수행
    encText = urllib.parse.quote(text_to_translate)
    data = f"source=ko&target=en&text={encText}"

    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)

    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()

        if rescode == 200:
            response_body = response.read()
            response_json = json.loads(response_body.decode("utf-8"))  # JSON 변환

            translated_text = response_json.get("message", {}).get("result", {}).get("translatedText", "번역 실패")

            print("번역 결과:", translated_text)

        else:
            print(f"Error Code: {rescode}")

    except Exception as e:
        print(f"요청 중 오류 발생: {str(e)}")

else:
    print("번역할 문장이 입력되지 않았습니다!")
