import telebot
import requests
import random
import re
import time

bot = telebot.TeleBot('7288229324:AAF5n1ojqPgtfKTPmUHR-c6LLJ3OE5sbUjg')
user_email = {}


# Hàm tạo địa chỉ email ngẫu nhiên
def get_email_address():
    domains = ["rteet.com", "1secmail.com"]
    response = requests.get(
        "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
    email_prefix = response.json()[0].split('@')[0]
    selected_domain = random.choice(domains)
    email_address = f"{email_prefix}@{selected_domain}"
    return email_address


# Hàm lấy tin nhắn từ email
def get_messages(email):
    login, domain = email.split('@')
    response = requests.get(
        f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    )
    return response.json()


# Hàm lấy mã OTP từ email
def get_otp_code(email):
    messages = get_messages(email)
    if messages:
        for message in messages:
            subject = message['subject']
            if re.search(r'FB-\d+', subject):
                match = re.search(r'FB-(\d+)', subject)
            else:
                match = re.search(r'\b\d{4,6}\b', subject)

            if match:
                return match.group(1) if 'FB-' in subject else match.group(0)
    return None


@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    bot.send_message(message.chat.id,
                     "/get tạo mail - /otp lấy mã.",
                     parse_mode='html')
    username = message.from_user.username if message.from_user.username else f"{message.from_user.first_name} {message.from_user.last_name}"
    print(f"User @{username} (ID: {message.chat.id}) đã khởi động bot.")


@bot.message_handler(commands=['get'])
def send_random_email(message):
    email = get_email_address()
    user_email[message.chat.id] = email
    bot.send_message(message.chat.id,
                     f"<code>{email}</code>",
                     parse_mode='html')
    username = message.from_user.username if message.from_user.username else f"{message.from_user.first_name} {message.from_user.last_name}"
    print(f"User @{username} (ID: {message.chat.id}) : {email}")


@bot.message_handler(commands=['otp'])
def send_otp_code(message):
    email = user_email.get(message.chat.id)
    if email:
        otp_code = get_otp_code(email)
        username = message.from_user.username if message.from_user.username else f"{message.from_user.first_name} {message.from_user.last_name}"

        if otp_code:
            bot.send_message(message.chat.id,
                             f"<code>{otp_code}</code>",
                             parse_mode='html')
            print(
                f"User @{username} (ID: {message.chat.id}) OTP code: {otp_code}"
            )
        else:
            bot.send_message(message.chat.id,
                             "kh tìm dc mã.",
                             parse_mode='html')
            print(f"User @{username} (ID: {message.chat.id}): kh tìm dc mã.")
    else:
        bot.send_message(message.chat.id,
                         "chưa tạo mail, dùng /get để tạo mail.",
                         parse_mode='html')
        print(
            f"User @{username} (ID: {message.chat.id}) tried to get OTP without email."
        )


while True:
    try:
        bot.polling()
    except (requests.exceptions.ReadTimeout, Exception) as e:
        print(f"An error occurred: {e}. Restarting bot...")
        time.sleep(5)  # Đợi một chút trước khi khởi động lại bot
