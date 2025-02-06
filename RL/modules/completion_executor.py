import json

import requests


class CompletionExecutor:
    """모델 피드백을 요청하는 클래스"""

    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            "Authorization": self._api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }

        final_content = ""
        with requests.post(
            self._host + "/serviceapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=True,
        ) as r:
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data:"):
                        try:
                            data = json.loads(decoded_line[5:])
                            if "message" in data and "content" in data["message"]:
                                final_content = data["message"]["content"]
                        except json.JSONDecodeError:
                            continue
        return final_content
