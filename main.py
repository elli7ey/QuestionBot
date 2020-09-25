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
    ebot.reply_to(message, "Вы хотите добавить вопрос по истории. Для этого отправь мне вопрос, который ты хочешь добавить в базу данных")
    msgs = fetch(MESSAGE_PATH)
    msgs[message.from_user.id] = ["Ожидание вопроса", "История"]
    store(MESSAGE_PATH, msgs)


command = ["social_add"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def history_add(message):
    ebot.reply_to(message, "Вы хотите добавить вопрос по обществознанию. Для этого отправь мне вопрос, который ты хочешь добавить в базу данных. Отступи три строчки и напиши ответ на этот вопрос. Не обессудь брат братишка, мне просто надо как-то разделить вопрос и ответ")
    msgs = fetch(MESSAGE_PATH)
    msgs[message.from_user.id] = ["Ожидание вопроса", "Общество"]
    store(MESSAGE_PATH, msgs)

command = ["history_generate"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def history_generate(message):
    res = ""
    numbers = generate_numbers(20, HISTORY_PATH)
    questions = get_questions(HISTORY_PATH, numbers)
    for row in questions:
        res += f"{row[0]}\n{row[1]}\n\n"
    ebot.reply_to(message, res)


command = ["social_generate"]
@ebot.message_handler(commands=command)
@ebot.edited_message_handler(commands=command)
def history_generate(message):
    res = ""
    numbers = generate_numbers(20, SOCIAL_PATH)
    questions = get_questions(SOCIAL_PATH, numbers)
    for row in questions:
        res += f"{row[0]}\n{row[1]}\n\n"
    ebot.reply_to(message, res)




@ebot.message_handler(func=lambda m: True)
def echo_all(message):
    msgs = fetch(MESSAGE_PATH)
    last_msg = msgs[message.from_user.id]

    if last_msg[0] == "Ожидание вопроса":
        ebot.reply_to(message, "Проверьте свое сообщение еще раз. Удалить добавленный в базу данных вопрос может только мой создатель. Он очень ленивый, поэтому лучше бы вам не ошибаться. Напишите 'Да', если ввели все правильно")
        msgs[message.from_user.id] = [message.text, last_msg[1]]
        store(MESSAGE_PATH, msgs)

    if message.text == "Да":
        if "\n\n\n" in last_msg[0]:
            f_column, s_column = last_msg[0].split("\n\n\n")

            if last_msg[1] == "Общество":
                if add_question(SOCIAL_PATH, f"*{f_column}*", f"({s_column})"):
                    ebot.reply_to(message, "Готово")
                else:
                    ebot.reply_to(message, "Данный вопрос уже присутвует в базе данных")

            if last_msg[1] == "История":
                if add_question(HISTORY_PATH, f"*{f_column}*", f"({s_column})"):
                    ebot.reply_to(message, "Готово")
                else:
                    ebot.reply_to(message, "Данный вопрос уже присутвует в базе данных")

            msgs[message.from_user.id] = "Ждемс запроса"
            store(MESSAGE_PATH, msgs)

        else:
            ebot.reply_to(message, "Вы не правильно отформатировали свое сообщение")
            msgs[message.from_user.id] = ["Ожидание вопроса", last_msg[1]]
            store(MESSAGE_PATH, msgs)





ebot.polling(none_stop=True)
