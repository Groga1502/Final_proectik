import sqlite3

def prepare_database_for_tts():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()

    query = (f'CREATE TABLE IF NOT EXISTS users' \
             f'(id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
             f'user_id INTEGER, ' \
             f'voice TEXT, ' \
             f'text TEXT, ' \
             f'tokens INTEGER)')

    cur.execute(query)
    connection.commit()
    cur.close()
def start_regestration(id, voice):
    first_info = (id, voice)
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute(
            f'INSERT INTO users (user_id, voice) VALUES (?, ?);', first_info)
    connection.commit()
    cur.close()

def add_text(text, id, tokens):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute(f'UPDATE users SET text = ?, tokens = ? WHERE user_id = ?;', (f"{text}", tokens, id))
    connection.commit()
    cur.close()
    pass

def to_speech_1(id):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT text FROM users WHERE user_id = {id} ORDER BY id DESC;')
    for res in results:
        text = res[0]
        return text

def to_speech_2(id):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT voice FROM users WHERE user_id = {id} ORDER BY id DESC;')
    for res in results:
        voice = res[0]
        return voice

