import telebot
from telebot import types
import info.config
import speechkit.tts
import speechkit.stt
from data.data_for_tts import *
from data.data_for_stt import prepare_database_for_stt, new_stt, answer_writing, ask_answer
from data.data_for_gpt import prepare_database, regestration_for_people, regestration_for_assistent, get_answer, get_prompt
import YaGPT
import validators

bot = telebot.TeleBot(info.config.TOKEN)
users = {}
"""
!!! ЗНАЮ, СЛОВАРЬ - НЕ ЛУЧШИЙ СПОСОБ ДЛЯ БОТОВ, НО:
1. ЭТО БОТ С МАЛЫМ КОЛЛИЧЕСТВОМ ПОЛЬЗОВАТЕЛЕЙ
2. БОТ БУДЕТ ЗАГРУЖЕН НА ВМ => СЛОВАРЬ НЕ ПРИДЕТСЯ ПИСАТЬ ЗАНОВО
"""
voice_dictionary = {
    "Алена": "alena", "Филипп": "filipp", "Джейн": "jane", "Захар": "zahar", "Даша": "dasha", "Юлия": "julia", "Лера": "lera", "Маша": 'masha', "Марина": "marina", "Александр": "alexander", "Кирилл": "kirill"
    }
def create_keyboard(buttons_list):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    """
    Стартовая функция, в нее входит: запуск таблиц, приветственное сообщение.
    :param message:
    :return: None
    """
    bot.send_message(message.chat.id, "Приветствую! Я обновленный бот-помошник)! Теперь я воспринимаю голосовые сообщения и отвечаю на них)", reply_markup=create_keyboard(["/tts", '/help', '/stt', '/ask_GPT', '/dialog_with_GPT']))
    users[message.chat.id] = False
    prepare_database_for_stt()
    prepare_database_for_tts()
    prepare_database()
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Здесь пока ничего нет!")

@bot.message_handler(commands=['tts'])
def tts_funck(message):
    """
    Начальная функция tts, для выбора голоса (запрос отдельно от GPT)
    :param message:
    :return: None
    """
    webApp = types.WebAppInfo(
        "https://yandex.cloud/ru/docs/speechkit/tts/voices?utm_referrer=https%3A%2F%2Fwww.google.com%2F")
    button = types.KeyboardButton(text='Информация о голосах', web_app=webApp)
    bot.send_message(message.chat.id,
                     "Здесь вы можете протестировать озвучку текста! Для этого просто отправьте сообщения:) Но перед этим прошу вас выберите оператора озвучки)",
                     reply_markup=create_keyboard(
                         ["Алена", 'Филипп', 'Джейн', 'Захар', 'Даша', 'Юлия', 'Лера', 'Маша', 'Марина', 'Александр',
                          'Кирилл', button]))
    bot.register_next_step_handler(message, what_is_voice)

@bot.message_handler(commands=['stt'])
def stt_funck(message):
    """
    Начальная функция stt (запрос аудио)
    :param message:
    :return: None
    """
    bot.send_message(message.chat.id, "Здесь вы можете протестировать разбор голосового сообщения! Отправьте аудио сообщение!")
    bot.register_next_step_handler(message, stt_rek)

@bot.message_handler(commands=['ask_GPT'])
def ask_GPT(message):
    bot.send_message(message.chat.id, "Я уже жду вашего запроса! :)")
    bot.register_next_step_handler(message, get_prompt_and_work)

@bot.message_handler(commands=['dialog_with_GPT'])
def go_to_the_dialog(message):
    bot.send_message(message.chat.id, "Добро пожаловать в режим диалогов! Если надоест - /stop")
    dialog(message)
"""
ФУНКЦИИ TTS START
"""
def what_is_voice(message):
    """
    Функция для записи стартовых данных и текста для озвучки.
    :param message:
    :return: None
    """
    for i in voice_dictionary:
        if i == message.text and message.text != 'Информация о голосах':
            voice = voice_dictionary[i]
            start_regestration(id=message.chat.id, voice=voice)
            bot.send_message(message.chat.id, "Вам только осталось ввести текст для озвучки)")
            bot.register_next_step_handler(message, add_text_to_datebase_tts)
            break
    else:
        bot.send_message(message.chat.id, "Видимо вы введи несуществующего героя озвучки")
        tts_funck(message)

def add_text_to_datebase_tts(message):
    """
    Функция для проверки димита + сохранение текста (запроса) в БД
    :param message:
    :return: None
    """
    if validators.SUM() + len(message.text) > info.config.MAX_PROJECT_FOR_TTS_TEXT:
        bot.send_message(message.chat.id, "Бот остановлен из-за преувеличения лимита!")
        bot.stop_bot()
    add_text(text=message.text, id=message.chat.id, tokens=len(message.text))
    get_answer_of_tts(message)

def get_answer_of_tts(message):
    """
    Получение данных из БД + получение ответа
    :param message:
    :return: None
    """
    text = to_speech_1(id=message.chat.id)
    voice = to_speech_2(id=message.chat.id)
    speechkit.tts.text_to_speech(text=text, voice=voice, message=message)
"""
TTS FINISH
"""

"""
STT_START
"""
def stt_rek(message):
    """
    Анализ аудио сообщения, проверка пользователя и бота (колличество блоков)
    + вывод текста пользователю, работа с БД (145, 146 строки)
    :param message:
    :return: None
    """
    if not message.voice:
        bot.send_message(message.chat.id, "Бот в этом режиме распознает только аудио сообщения, начните сначала!")
        stt_funck(message)
    else:
        file = work_with_file(message)
        answer = speechkit.stt.speech_to_text(file)
        blocks = validators.blocks(message)
        if info.config.MAX_BLOCKS_ON_ALL < validators.SUM_ALL():
            bot.send_message(message.chat.id, "Все блоки израсходованы, бот будет отключен!")
            bot.stop_bot()
        elif info.config.MAX_BLOCKS_ON_ALL < validators.SUM_ALL():
            bot.send_message(message.chat.id, "Попробуйте записать сообщение поменьше, возможно оно очень длинное!")
            stt_funck(message)
        if info.config.MAX_LEN_OF_VOICE < message.voice.duration:
            bot.send_message(message.chat.id, "Аудио слишком длинное! Я не могу продолжать работу!")
            stt_funck(message)
        new_stt(id=message.chat.id, blocks=blocks)
        answer_writing(answer=answer, id=message.chat.id)
        ask_answer_of_stt(message)
def ask_answer_of_stt(message):
    """
    Вывод ответа пользователю
    :param message:
    :return: None
    """
    answer = ask_answer(id=message.chat.id)
    bot.send_message(message.chat.id, answer)
def work_with_file(message):
    """
    Работа с голосовым сообщением
    :param message:
    :return: file
    """
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    return file
"""
STT FINISH
"""

"""
FOR_GPT START
"""
def prompt_plus(message):
    """
    Создание подходящего промпта
    :param message:
    :return: a
    """
    if users[message.chat.id] != 0:
        a = info.config.FOR_PROMPT_IF_DIALOG
    else:
        a = info.config.FOR_PROMPT
    return a
def get_prompt_and_work(message):
    """
    Создание запроса, проверка на правильность сообщения пользователя + запись данных в БД
    :param message:
    :return: None
    """
    validators.count_tokens_in_project(message=message)
    if message.text:
        if len(message.text) <= info.config.MAX_LEARN_MESSAGE_IN_TEXT:
            bot.send_message(message.chat.id, "...")
            a = prompt_plus(message)
            tokens = validators.count_tokens(prompt_or_answer=a + message.text)
            regestration_for_people(user_id=message.chat.id, role="user", content=a + message.text, tokens=tokens)
            ask_gpt_if_text(message)
    elif message.voice:
        if message.voice.duration > info.config.MAX_LEN_OF_VOICE:
            bot.send_message(message.chat.id, "Слишком большой объем сообщения!")
            ask_GPT(message)
        else:
            bot.send_message(message.chat.id, "...")
            file = work_with_file(message)
            answer = speechkit.stt.speech_to_text(file)
            a = prompt_plus(message)
            prompt = a + answer
            len_prompt = validators.count_tokens(prompt_or_answer=prompt)
            regestration_for_people(user_id=message.chat.id, role="user", content=prompt, tokens=len_prompt)
            ask_gpt_if_voice(message)
def ask_gpt_if_voice(message):
    """
    Формирование данных для промпта (Их запись в БД)
    -> Отправка промпта и запись ответа в БД
    :param message:
    :return: None
    """
    prompt = get_prompt(user_id=message.chat.id)
    if validators.count_tokens(prompt) > info.config.MAX_LEARN_MESSAGE_IN_TOKEN:
        bot.send_message(message.chat.id, "Слишком большой объем сообщения! Попробуйте снова!")
        ask_GPT(message)
    else:
        answer = YaGPT.ask_gpt(text=prompt)
        tokens = validators.count_tokens(prompt_or_answer=answer)
        regestration_for_assistent(user_id=message.chat.id, role="assistent", content=answer, tokens=tokens)
        answer_voice(message)
def ask_gpt_if_text(message):
    """
        Формирование данных для промпта (Их запись в БД)
        -> Отправка промпта и запись ответа в БД
        :param message:
        :return: None
        """
    prompt = get_prompt(user_id=message.chat.id)
    if validators.count_tokens(prompt) > info.config.MAX_LEARN_MESSAGE_IN_TOKEN:
        bot.send_message(message.chat.id, "Слишком большой объем сообщения! Попробуйте снова!")
        ask_GPT(message)
    else:
        last_answer = YaGPT.ask_gpt(text=prompt)
        tokens = validators.count_tokens(prompt_or_answer=last_answer)
        regestration_for_assistent(user_id=message.chat.id, role="assistent", content=last_answer, tokens=tokens)
        answer_text(message)
def answer_text(message):
    """
    Ответ для текстаб работа с БД, Провека на диалог
    :param message:
    :return: None
    """
    last_answer = get_answer(user_id=message.chat.id)
    bot.send_message(message.chat.id, last_answer)
    if users[message.chat.id] == False:
        bot.send_message(message.chat.id, "Выберите дальнейшее действие! :)", reply_markup=create_keyboard(['Диалог', 'Новый вопрос', 'Хороший ответ', "Плохой ответ"]))
        bot.register_next_step_handler(message, reaction)
    else:
        dialog(message)
def answer_voice(message):
    """
       Ответ для текста работа с БД, Провека на диалог
       Доп. обработка ответа для audio сообщения!
       :param message:
       :return: None
       """
    answer = get_answer(user_id=message.chat.id)
    if validators.SUM()  < info.config.MAX_PROJECT_FOR_TTS_TEXT:
        start_regestration(id=message.chat.id, voice="alena")
        add_text(text=answer, id=message.chat.id, tokens=len(answer))
        ask_answer_of_gpt_if_voice(message)
    else:
        bot.send_message(message.chat.id, "Вы исчерпали допустимое колличество символов, бот заблокирован!")
        bot.stop_bot()

def ask_answer_of_gpt_if_voice(message):
    """
    Даем ответ для гс запроса, запрашиваем дальнейшее действие или отзыв
    :param message:
    :return: None
    """
    answer = to_speech_1(id=message.chat.id)
    voice = to_speech_2(id=message.chat.id)
    speechkit.tts.text_to_speech(text=answer, voice=voice, message=message)
    if users[message.chat.id] == False:
        bot.send_message(message.chat.id, "Выберите дальнейшее действие! :)", reply_markup=create_keyboard(
        ['Диалог', 'Новый вопрос', 'Хороший ответ', "Плохой ответ"]))
        bot.register_next_step_handler(message, reaction)
    else:
        dialog(message)
def reaction(message):
    """
    Просмотр выбраного действия
    :param message:
    :return:
    """
    if message.text == 'Диалог':
        bot.send_message(message.chat.id, "Добро пожаловать в режим диалогов! Здесь вы сможете бсприрывно общаться с ботом! Если надоест - /stop.")
        dialog(message)
    elif message.text == 'Новый вопрос':
        ask_GPT(message)
    elif message.text == 'Хороший ответ':
        bot.send_message(message.chat.id, "Спасибо! :)")
    elif message.text == 'Плохой ответ':
        bot.send_message(message.chat.id, "На самом деле я могу многое), попробуйте что-то вам точно понравится!")
    else:
        bot.send_message(message.chat.id, "Я такое не умею!")
def dialog(message):
    """
    Начало диалога
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Ваша реплика: (Уже можно общаться)")
    bot.register_next_step_handler(message, do_or_not)
def do_or_not(message):
    """
    Проверка: хочет ли пользователь продолжать беседу!
    :param message:
    :return:
    """
    if message.text != "/stop" or message.audio:
        users[message.chat.id] = True
        try:
            get_prompt_and_work(message)
        except:
            bot.send_message(message.chat.id, "Попробуйте снова, произошла ошибка (не по вашей вине!)")
    else:
        bot.send_message(message.chat.id, "Вы вышли из диалогового окна!")
        users[message.chat.id] = False
"""
FOR_GPT FINISH
"""

bot.polling()
