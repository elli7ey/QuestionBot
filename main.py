import csv
import os
import telebot
import random
import pickle

FOLDER = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(FOLDER, "History", "questions.csv")
SOCIAL_PATH = os.path.join(FOLDER, "Social", "questions.csv")
MESSAGE_PATH = os.path.join(FOLDER, "Last messages", "messages.json")
ebot = telebot.TeleBot("901348189:AAGQTBn9fmO_lKD6O9skilxZaWNvCkYW6ik")

def store(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f, 2)


def fetch(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def add_question(path, f_column, s_column):

    with open(path, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        for row in reader:
            if row["question"] == f_column or row["answer"] == s_column:
                return False

    with open(path, 'a') as csv_file:
        fieldnames = ["question", "answer"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        writer.writerow({"question": f_column, "answer": s_column})
        return True


def get_questions(path, numbers):
    result = []
    with open(path, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")

        for id, row in enumerate(reader):
            if id+1 in numbers:
                result.append([row["question"], row["answer"]])
    return result


def get_question_quantity(path):
    with open(path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        return len([row for row in reader])


def generate_numbers(quantity, path):
    numbers = set()
    while len(numbers) != quantity:
        numbers.add(random.randint(1, get_question_quantity(path)))
    return list(numbers)


command = ["start"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def start_message(message):
    with open(os.path.join(FOLDER, "start_message.txt"), "r", encoding="utf-8") as file:
        ebot.reply_to(message, file.read())
        msgs = fetch(MESSAGE_PATH)
        msgs[message.from_user.id] = "Еще ничего не отправил"
        store(MESSAGE_PATH, msgs)




command = ["history_add"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def history_add(message):
    ebot.reply_to(message, "Вы хотите добавить вопрос/вопросы по истории. Для этого отправьте все одним сообщением. Сообщение должно быть отформатированно так:\n\nВопрос[enter]\n[enter]\nОвтет[enter]\n[enter]\n[enter]\nВопрос[enter]\n[enter]\nОтвет[enter]\n[enter]\n[enter]\n\nИ так далее. \nНе обессудь брат братишка просто надо как-то разделить вопрос и ответ")
    msgs = fetch(MESSAGE_PATH)
    msgs[message.from_user.id] = ["Ожидание вопроса", "История"]
    store(MESSAGE_PATH, msgs)


command = ["social_add"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def history_add(message):
    ebot.reply_to(message, "Вы хотите добавить вопрос/вопросы по обществознанию. Для этого отправьте все одним сообщением. Сообщение должно быть отформатированно так:\n\nВопрос[enter]\n[enter]\nОвтет[enter]\n[enter]\n[enter]\nВопрос[enter]\n[enter]\nОтвет[enter]\n[enter]\n[enter]\n\nИ так далее. \nНе обессудь брат братишка просто надо как-то разделить вопрос и ответ")
    msgs = fetch(MESSAGE_PATH)
    msgs[message.from_user.id] = ["Ожидание вопроса", "Общество"]
    store(MESSAGE_PATH, msgs)

command = ["history_generate"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def history_generate(message):
    msgs = fetch(MESSAGE_PATH)
    cid = message.chat.id
    res = ""
    valid_questions = []

    numbers = generate_numbers(20, HISTORY_PATH)
    questions = get_questions(HISTORY_PATH, numbers)

    for id, row in enumerate(questions):
        res += f"{id+1}. {row[0]}\n{row[1]}\n\n"
        valid_questions.append([row[0], row[1]])

    ebot.reply_to(message, res)

    ebot.send_message(cid, "Если вы хотите изменить какой-то вопрос, то отправьте мне его номер по счету. За раз, вы сможете изменить только один вопрос.")
    msgs[message.from_user.id] = ["Возможна замена", valid_questions]
    store(MESSAGE_PATH, msgs)


command = ["social_generate"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def social_generate(message):
    msgs = fetch(MESSAGE_PATH)
    cid = message.chat.id
    res = ""
    valid_questions = []

    numbers = generate_numbers(20, SOCIAL_PATH)
    questions = get_questions(SOCIAL_PATH, numbers)

    for id, row in enumerate(questions):
        res += f"{id+1}. {row[0]}\n{row[1]}\n\n"
        valid_questions.append([row[0], row[1]])

    ebot.reply_to(message, res)

    ebot.send_message(cid, "Если вы хотите изменить какой-то вопрос, то отправьте мне его номер по счету. За раз, вы сможете изменить только один вопрос.")
    msgs[message.from_user.id] = ["Возможна замена", valid_questions]
    store(MESSAGE_PATH, msgs)





@ebot.message_handler(func=lambda m: True)
def echo_all(message):
    msgs = fetch(MESSAGE_PATH)
    cid = message.chat.id
    last_msg = msgs[message.from_user.id]

    if last_msg[0] == "Ожидание вопроса":
        ebot.reply_to(message, "Проверьте свое сообщение еще раз. Удалить добавленный в базу данных вопрос может только мой создатель. Он очень ленивый, поэтому лучше бы вам не ошибаться. Напишите 'Да', если ввели все правильно")
        msgs[message.from_user.id] = [message.text, last_msg[1]]
        store(MESSAGE_PATH, msgs)

    elif message.text == "Да":
        if "\n\n\n" in last_msg[0] or "\n\n" in last_msg[0]:
            questions = last_msg[0].split("\n\n\n")
            x = 0
            valid_questions = []
            for question in questions:
                print(x, question)
                if question.count("\n\n") == 1:
                    f_column, s_column = question.split("\n\n")
                    x += 1

                    if last_msg[1] == "Общество":
                        q_path = SOCIAL_PATH
                    elif last_msg[1] == "История":
                        q_path = HISTORY_PATH

                    if add_question(q_path, f"*{f_column}*", f"({s_column})"):
                        valid_questions.append([f_column, s_column])
                        ebot.send_message(cid, f"Вопрос номер {x} - успешно добавлен")
                    else:
                        ebot.send_message(cid, f"{x} - вопрос уже присутвует в базе данных")

                else:
                    ebot.send_message(cid, f"Ты не правильно отформатировал сообщение под номером {x}")


            msgs[message.from_user.id] = ["Ждемс", ""]
            store(MESSAGE_PATH, msgs)

    elif last_msg[0] == "Возможна замена" and message.text.isdigit():
        num = int(message.text)
        if num <= 20:
            ebot.reply_to(message, "Отправь мне новый вариант вопроса.\n\nВопрос[enter]\n\nОтвет")
            msgs[message.from_user.id] = ["Ожидание исправленного вопроса", (num, last_msg[1])]
        else:
            ebot.reply_to(message, "Такого номера не существует. Отправь номер заново")

    elif last_msg[0] == "Ожидание исправленного вопроса":
        num, new_questions = last_msg[1]
        new_f_c, new_s_c = message.text.split["\n\n"]
        last_f_c, last_s_c = new_questions[-1]

        new_questions[num-1] = [f"*{new_f_c}*", f"({new_s_c})"]
        res = ""
        for id, row in enumerate(new_questions):
            res += f"{id+1}. {row[0]}\n{row[1]}\n\n"
        ebot.send_message(cid, res)









ebot.polling(none_stop=True)
