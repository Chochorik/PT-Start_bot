import os
import telebot
import paramiko
import re
import logging
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = os.getenv('SSH_PORT')
SSH_USERNAME = os.getenv('SSH_USERNAME')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')

logging.basicConfig(filename='bot.log', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)


# Функция обработки почты
@bot.message_handler(commands=['find_email'])
def find_email(message):
    logging.info(f"Пользователь {message.from_user.id} запросил поиск email")
    bot.send_message(message.chat.id, "Введите текст для поиска email-адресов:")
    bot.register_next_step_handler(message, process_email_search)


# Функция для обработки текста и поиска email-адресов
def process_email_search(message):
    text = message.text
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        bot.send_message(message.chat.id, "Найденные email-адреса:")
        for email in emails:
            bot.send_message(message.chat.id, email)
    else:
        bot.send_message(message.chat.id, "Email-адреса не найдены.")


# Функция обработки номеров телефона
@bot.message_handler(commands=['find_phone_number'])
def find_phone_number(message):
    logging.info(f"Пользователь {message.from_user.id} запросил поиск номеров телефона")
    bot.send_message(message.chat.id, "Введите текст для поиска номеров телефонов:")
    bot.register_next_step_handler(message, process_phone_number_search)


# Функция для обработки текста и поиска номеров телефонов
def process_phone_number_search(message):
    text = message.text
    phone_pattern = r'(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'
    phone_numbers = re.findall(phone_pattern, text)
    if phone_numbers:
        response = "Найденные номера телефонов:\n"
        for phone_number in phone_numbers:
            response += f"{phone_number}\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Номера телефонов не найдены.")


# Функция-обработчик команды /verify_password
@bot.message_handler(commands=['verify_password'])
def verify_password(message):
    logging.info(f"User {message.from_user.id} requested password verification")
    bot.send_message(message.chat.id, "Введите пароль для проверки сложности:")
    bot.register_next_step_handler(message, process_password_verification)


# Функция для обработки пароля и проверки его сложности
def process_password_verification(message):
    password = message.text
    if re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$', password):
        bot.send_message(message.chat.id, "Пароль сложный")
    else:
        bot.send_message(message.chat.id, "Пароль простой")


@bot.message_handler(commands=['find_email'])
# Функция для установления SSH-соединения с удаленным сервером и выполнения команды
def ssh_command(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

# Информация о релизе
@bot.message_handler(commands=['get_release'])
def get_release(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о релизе")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'lsb_release -a')
    bot.send_message(message.chat.id, output)


# Информация об архитектуре процессора, имени хоста системы и версии ядра
@bot.message_handler(commands=['get_uname'])
def get_uname(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию об архитектуре процессора, имени хоста системы и версии ядра")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'uname --all')
    bot.send_message(message.chat.id, output)


# Информация о времени работы системы
@bot.message_handler(commands=['get_uptime'])
def get_uptime(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о времени работы системы")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'uptime -p')
    bot.send_message(message.chat.id, f"Система работает: {output}")


# Информация о состоянии файловой системы
@bot.message_handler(commands=['get_df'])
def get_df(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о состоянии файловой системы")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'df --all')
    bot.send_message(message.chat.id, output)


# Сбор информации о состоянии оперативной памяти
@bot.message_handler(commands=['get_free'])
def get_free(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о состоянии оперативной памяти")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'free --mega')
    bot.send_message(message.chat.id, f"В мегабайтах:\n{output}")


# Информация о производительности системы
@bot.message_handler(commands=['get_mpstat'])
def get_mpstat(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о производительности системы")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'mpstat')
    bot.send_message(message.chat.id, output)


# Информация о работающих в данной системе пользователях
@bot.message_handler(commands=['get_w'])
def get_w(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о работающих в данной системе пользователях")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'w')
    bot.send_message(message.chat.id, output)


# Информация о последних 10 входах в систему
@bot.message_handler(commands=['get_auths'])
def get_auths(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о последних 10 входах в систему")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, 'last -n 10')
    bot.send_message(message.chat.id, output)


# Информация о последних 5 критических событиях
@bot.message_handler(commands=['get_critical'])
def get_critical(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о последних 5 критических событиях")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, "journalctl -p crit -n 5")
    bot.send_message(message.chat.id, output)


# Информация о запущенных процессах
@bot.message_handler(commands=['get_ps'])
def get_ps(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о запущенных процессах")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, "ps -A u | head -n 10")
    bot.send_message(message.chat.id, output)


# Информация об используемых портах
@bot.message_handler(commands=['get_ss'])
def get_ss(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию об используемых портах")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, "ss -l | head -n 20")
    bot.send_message(message.chat.id, output)


# Информация об установленных пакетах
@bot.message_handler(commands=['get_apt_list'])
def get_apt_list(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию об установленных пакетах")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, "apt list --installed | head -n 11")
    bot.send_message(message.chat.id, output)


# Информация о запущенных сервисах
@bot.message_handler(commands=['get_services'])
def get_services(message):
    logging.info(f"Пользователь {message.from_user.id} запросил информацию о запущенных сервисах")
    output = ssh_command(SSH_HOST, int(SSH_PORT), SSH_USERNAME, SSH_PASSWORD, "systemctl list-units --type=service --state=running")
    bot.send_message(message.chat.id, output)


# Запуск бота
bot.polling()
