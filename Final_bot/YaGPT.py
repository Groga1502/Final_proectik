import requests
import info.creds
import info.config

def ask_gpt(text):
    folder_id = info.creds.folder_id

    headers = {
        'Authorization': f'Bearer {info.creds.iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": info.config.MAX_TOKENS
        },
        "messages": [
            {
                "role": "user",
                "text": text
            }
        ]
    }

    response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)
    try:
        if response.status_code == 200:
            answer = response.json()["result"]["alternatives"][0]["message"]["text"]
            return answer
        else:
            return f"Ошибка: {response.status_code}"
    except:
        raise RuntimeError(
            'Invalid response received: code: {}, message: {}'.format(
                    {response.status_code}, {response.text}
            )
        )