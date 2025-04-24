from telebot.types import ReplyKeyboardMarkup
import sqlite3 as sq
from commands_func import bot, get_logica, update_logica, form_lessons
from create_db import shkolnik_1, module4, data_folder


@bot.message_handler(commands=['start', 'take_lesson'])
def welcome(message):
    try:
        with sq.connect(data_folder + 'timetable') as cursor:
            res_of_zapr = cursor.execute(
                f"SELECT * FROM users_st WHERE user_id={message.from_user.id}").fetchall()
            cursor.commit()

            # print(res_of_zapr) -> двумерный массив

            #если пользователь зарегестрировать, сразу его на выбор урока
            if bool(res_of_zapr):
                if res_of_zapr[0][1] != '0_0':
                    message.text = res_of_zapr[0][1]
                    update_logica(message, 'input_name')
                    obrabotka(message)   # функция обработки
                    return 0
            #иначе добавляем его в базу и приветствуем
            else:
                cursor.execute(f"INSERT INTO users_st (user_id,name,chat_id) \
                                                VALUES ({message.from_user.id}, '0_0', {message.chat.id});")
                cursor.commit()

            update_logica(message, 'input_name')
            bot.send_message(message.chat.id, "Вечер добрый, <u>{0.first_name}</u>!\nНа связи бот для дня самоуправства.\nПредставься в формате:\nПётр Курочкин - 11а".format(message.from_user, bot.get_me()),
                             parse_mode='html')

    except Exception as e:
        print(str(e), '\n', 'welcome')
        cursor.close()


# основной цикл
@bot.message_handler(content_types=["text"])
def obrabotka(message):
    message.text = message.text.strip()
    us_lg = get_logica(message)

    #команда для тестирования, чтобы вручную менять переменную логика
    if us_lg == 'set_logica':
        update_logica(message, message.text)
        bot.send_message(message.chat.id, 'Всё сделано. Ваша  logica -> ' + message.text)

    #команда для отказа от урока
    try:
        if us_lg == 'otkaz_input':
            grade, les_numb = map(str.strip, message.text.split(' --- '))
            les_numb = les_numb[0]
            with sq.connect(data_folder + 'timetable') as cursor:
                us_data = cursor.execute(f"SELECT * FROM users_st WHERE user_id = {message.from_user.id}").fetchall()[0]
                cursor.commit()
                les_data = cursor.execute(f"SELECT * FROM les_{les_numb} WHERE grade = '{grade}'").fetchall()[0]
                cursor.commit()
                if us_data[1] in les_data[1]:
                    cursor.execute(f'''UPDATE les_{les_numb} SET student = "0" WHERE grade = "{grade}"''')
                    cursor.commit()
                    cursor.execute(f'''UPDATE users_st SET les_{les_numb} = 'false' 
                                    WHERE user_id = {message.from_user.id}''')
                    cursor.commit()
                    bot.send_message(message.from_user.id, 'ок. Ты свободен')
                else:
                    bot.send_message(message.from_user.id, 'Ты не задействован в этом уроке -> не можешь его освободить')
    except Exception as e:
        print(str(e), 'ошибка в блоке otkaz_input -> ', message.text)

    try:
        # input_name (1) ввод имени
        if us_lg == 'input_name':
            name, grade = map(str.strip, message.text.split('-'))

            with sq.connect(data_folder + 'timetable') as cursor:
                autorized_students = cursor.execute(f"SELECT name FROM users_st").fetchall()
                cursor.commit()

            if name in shkolnik_1:
                if (name+'-'+grade,) not in autorized_students:
                    with sq.connect(data_folder + 'timetable') as cursor:
                        cursor.execute(f'''UPDATE users_st SET name = '{name+" - "+grade}' WHERE user_id = {message.from_user.id};''')

                    markup1 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
                    markup1.add(*('Да', 'Нет'))
                    bot.send_message(message.chat.id, ' ок. Будешь вести с другом?', reply_markup=markup1)
                    print(name + '  -  ' + grade + '  -> подключился')

                    update_logica(message, 'input_status')
                else:
                    bot.send_message('Этот пользователь уже авторизован')
            else:
                bot.send_message('Я не могу тебя найти, попробуй ещё раз. Я тебя вижу как'+name+'-'+grade)

    except Exception as e:
        print(str(e))
        print(message.text, 'ошибка в блоке input_name')
        bot.send_message(message.chat.id, 'что-то пошло не так. Проверь формат ввода данных')

    try:
        # input_status (2) ввод статуса один или с компаньоном
        if us_lg == 'input_status':
            if message.text.lower() == 'да':
                bot.send_message(message.chat.id, 'Вводи имя друга')
                update_logica(message, 'input_companion')

            elif message.text.lower() == 'нет':

                markup2 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
                subj = form_lessons(message)
                if bool(subj) is False:
                    bot.send_message(message.chat.id, 'Предметов нет')
                    update_logica(message, 'input_name')
                    return 0

                markup2.add(*subj)

                bot.send_message(message.chat.id, 'ок, теперь введи предмет', reply_markup=markup2)

                update_logica(message, 'input_subject')

            else:
                bot.send_message(message.chat.id, 'Да или нет?')

    except Exception as e:
        print(str(e))
        print(message.text, 'ошибка в блоке input_status')
        bot.send_message(message.chat.id, 'что-то пошло не так')

    try:
        # input_companion (2.1) ввод компаньона
        if us_lg == 'input_companion':
            with sq.connect(data_folder + 'timetable') as cursor:
                cursor.execute(f"UPDATE users_st SET friend = '{message.text}' WHERE user_id = {message.from_user.id};")

            markup3 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
            subj = form_lessons(message)
            if bool(subj) is False:
                bot.send_message(message.chat.id, 'Предметов нет')
                return 0

            markup3.add(*subj)

            bot.send_message(message.chat.id, 'ок, теперь введи предмет', reply_markup=markup3)
            update_logica(message, 'input_subject')

    except Exception as e:
        print(str(e), '\n', 'input_subject - error\nmessage: ' + message.text)
        bot.send_message(message.chat.id, 'что-то пошло не так')

    try:
        # input_subject (3) ввод предмета
        if us_lg == 'input_subject':

            markup4 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)

            for i in range(1, 5):
                if i == 4 and not(module4):
                    continue

                with sq.connect(data_folder + 'timetable') as cursor:
                    # str
                    fl = cursor.execute(f'''SELECT les_{i} FROM users_st WHERE user_id = {message.from_user.id}''')

                    if fl.fetchall()[0][0].lower() == 'true':
                        continue

                with sq.connect(data_folder + 'timetable') as cursor:
                    lesson_i = cursor.execute(f'''SELECT grade FROM les_{i} 
                    WHERE subject="{message.text}" AND (student ="0" OR student = "0_o");''').fetchall()
                    markup4.add(*map(lambda x: x[0] + ' ---' + f' {i} урок', lesson_i))

            update_logica(message, 'input_lesson')
            bot.send_message(message.chat.id, 'Выбери урок', reply_markup=markup4)

    except Exception as e:
        print(str(e), '\nОшибка в блоке input_subject')
        bot.send_message(message.chat.id, 'что-то пошло не так')

    try:
        # input_lesson (4) ввод урока
        if us_lg == 'input_lesson':
            try:
                grade, les_numb = map(str.strip, message.text.split(' --- '))

                les_numb = les_numb[0]
                with sq.connect(data_folder + 'timetable') as cursor:
                    ans = cursor.execute(f'''SELECT * FROM les_{les_numb} WHERE grade = "{grade}"''').fetchall()[0]
                    if ans[1] != '0' and ans[1] != '0_o':
                        bot.send_message(message.chat.id, 'Нехорошо выбивать людей из уроков')
                        return 0
                    cursor.commit()

                    inf_from_user = cursor.execute(f"SELECT * FROM users_st WHERE user_id = {message.from_user.id}").fetchall()[0]
                    new_st = inf_from_user[1] + (" и " + inf_from_user[3] if inf_from_user[3] != 'T_T' else '')
                    cursor.commit()
                    cursor.execute(f'''
                                    UPDATE les_{les_numb} SET student = "{new_st}" WHERE grade = "{grade}"''')
                    cursor.commit()
                    cursor.execute(f'''UPDATE users_st SET les_{les_numb} = "True";''')
                    cursor.commit()
                    tch = cursor.execute(f'''SELECT teacher FROM les_{les_numb} WHERE grade = "{grade}"''').fetchall()[0][0]
                    bot.send_message(message.chat.id, f'ок. Ты заменяешь - {tch}. Хочешь ещё - введи /start')

            except Exception as e:
                print(str(e), 'проблема в блоке input_lesson', message.text)

    except Exception as e:
        print(str(e), '\n Не валидный ввод в input_lesson ', message.text)
        bot.send_message(message.chat.id, 'Неправильно ввёл')


# print(bot.message_handlers)

bot.infinity_polling()
print(1)

