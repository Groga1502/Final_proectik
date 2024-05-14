import info.creds
import requests
import sqlite3
import info.config
import telebot

bot = telebot.TeleBot(info.config.TOKEN)

def count_tokens(prompt_or_answer):
    """
    ФУНКЦИЯ ДЛЯ ПОТЩЕТА ТОКЕНОВ ИСПОЛЬЗОВАННЫХ ПОЛЬЗОВАТЕЛЕМ
    """
    headers = {
        'Authorization': f'Bearer {info.creds.iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{info.creds.folder_id}/yandexgpt/latest",
       "maxTokens": info.config.MAX_TOKENS,
       "text": prompt_or_answer
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()['tokens']
    )

def blocks(message):
    time = message.voice.duration // 15 + message.voice.duration % 15
    return time

def count_tokens_in_project(message):
    count = 0
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    results = cursor.execute(f'SELECT SUM(tokens) FROM users3;')
    for result in results:
        if result == None:
            count = 0
        else:
            count += result[0]
    if count >= info.config.MAX_PROJECT_TOKENS:
        bot.send_message(message.chat.id, "Вы израсходовали все токены, доступ к боту закрыт!")
        bot.stop_bot()

def SUM():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT SUM(tokens) FROM users')
    for res in results:
        if res[0] != None:
            summ = res[0]
        else:
            summ = 0
        return summ

def SUM_ALL():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT SUM(stt_blocks) FROM users2;')
    for res in results:
        if res[0] != None:
            summ = res[0]
        else:
            summ = 0
        return summ
