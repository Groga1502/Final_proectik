import sqlite3

def prepare_database_for_stt():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()

    query = (f'CREATE TABLE IF NOT EXISTS users2' \
                    f'(id INTEGER AUTO_INCREMENT PRIMARY KEY, ' \
                    f'user_id INTEGER, ' \
                    f'message TEXT, ' \
                    f'stt_blocks INTEGER)')

    cur.execute(query)
    cur.close()

def new_stt(id, blocks):
    info = (id, blocks)
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute(
        f'INSERT INTO users2 (user_id, stt_blocks) VALUES (?, ?);', info)
    connection.commit()
    cur.close()
    pass

def answer_writing(answer, id):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute(f'UPDATE users2 SET message = ? WHERE user_id = ?;', (f"{answer}", id))
    connection.commit()
    cur.close()
    pass

def ask_answer(id):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    results = cur.execute(f'SELECT message FROM users2 WHERE user_id = {id};')
    for res in results:
        answer = res[0]
        return answer


