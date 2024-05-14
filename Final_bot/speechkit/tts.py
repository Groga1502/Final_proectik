import requests
import iam_token_generation
import info.config
import info.creds
import telebot

bot = telebot.TeleBot(info.config.TOKEN)

def text_to_speech(text, voice, message):
    iam_token = info.creds.iam_token
    folder_id = info.creds.folder_id
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': voice,
        'folderId': folder_id,
    }
    # Выполняем запрос
    response = requests.post(
        'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        bot.send_audio(message.chat.id, response.content)
    else:
        bot.send_message(message.chat.id, f"Что-то пошло не так! Ошибка: {response.status_code}")
