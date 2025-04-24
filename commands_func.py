from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
import sqlite3 as sq

from tokens import TOKEN  # bot token rom @BotFather
from create_db import module4, data_folder
bot = TeleBot(token=TOKEN)


def get_logica(message):
    '''

    :param message: message из obrabotka (в нём хранится chat id и user id)
    :return:  строка со значением logica для ученика
    '''
    try:
        with sq.connect(data_folder + 'timetable') as cursor:
            return cursor.execute(f"SELECT logica FROM users_st WHERE user_id = {message.from_user.id};").fetchall()[0][0]
    except Exception as e:
        print(str(e), '\n', 'get_logica')
        cursor.close()


def update_logica(message, status):
    '''

    :param message: message из obrabotka (в нём хранится chat id и user id)
    :param status: status пишем сами - str. На что хотим изменить логику, то есть куда пойдёт юзер дальше
    :return:
    '''
    try:
        with sq.connect(data_folder + 'timetable') as cursor:
            cursor.execute(f"UPDATE users_st SET logica = '{status}' WHERE user_id = {message.from_user.id};")
    except Exception as e:
        print(str(e), '\n', 'update_logica')
        cursor.close()


def form_lessons(message):
    '''
    Нам в двух ситуациях надо формировать такое множество, поэтому написал функцию, чтобы занимало меньше места
    :param message: message из obrabotka (в нём хранится chat id и user id)
    :return: множество (неупорядоченный массив без повторений) доступных для ученика предметов
    '''
    subjects = set()
    try:

        for i in range(1, 5):
            if (i == 4 and not(module4)):
                continue

            with sq.connect(data_folder + 'timetable') as cursor:
                # str
                fl = cursor.execute(f'''SELECT les_{i} FROM users_st WHERE user_id = {message.from_user.id}''')

                if fl.fetchall()[0][0].lower() == 'true':
                    continue
            with sq.connect(data_folder + 'timetable') as cursor:
                subject_i = cursor.execute(f'''SELECT subject FROM les_{i}
                WHERE student = '0' OR student = "0_o"''').fetchall()
                # print(subject_i)

                [subjects.add(x[0]) for x in subject_i]

        return subjects
    except Exception as e:
        print(str(e), '\nПроблема в блоке form_lessons')


@bot.message_handler(commands=['otkaz'])
def otkaz(message):
    try:
        user_lesson = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)

        with sq.connect(data_folder + 'timetable') as cursor:

            user_data = cursor.execute(f'''SELECT * FROM users_st WHERE user_id = {message.from_user.id}''').fetchall()[0]
            cursor.commit()
            for i in range(4):
                if (i == 4 and not(module4)) or user_data[5+i].lower() == 'false': continue

                user_lesson_i = cursor.execute(f'''SELECT * FROM les_{i+1} WHERE student LIKE "{user_data[1]}%"''').fetchall()[0]
                user_lesson.add(user_lesson_i[0] + f' --- {i+1} урок')

        update_logica(message, 'otkaz_input')
        bot.send_message(message.chat.id, 'Вводи предмет, от которого отказываешься', reply_markup=user_lesson)
    except Exception as e:
        print(str(e), '-> ошибка в команде otkaz')






@bot.message_handler(commands=['timetable'])
def timetable(message):
    try:
        with sq.connect(data_folder + 'timetable') as cursor:
            for i in range(1, 4):
                if (i == 4 and not(module4)): continue

                data = cursor.execute(f'''SELECT * FROM les_{i}''').fetchall()
                with open(f'lesson_{i}.txt', 'w', encoding='UTF-8') as f:
                    f.write('grade'+' '*8+'student'+' '*46 + 'teacher' + ' '*25 + 'subject'+' '*10+'\n')
                    for x in data:
                        f.write(x[0].center(13)+x[1].center(53)+x[2].center(32)+x[3].center(17)+'\n')
                bot.send_document(message.chat.id, document=open(f'lesson_{i}.txt', 'rb'))
    except Exception as  e:
        print(str(e), '-> ошибка в команде timetable')

# вещь для проверок
@bot.message_handler(commands=['set_logica'])
def set_logica(message):
    update_logica(message, 'set_logica')
    bot.send_message(message.chat.id, 'Вводи логику')
