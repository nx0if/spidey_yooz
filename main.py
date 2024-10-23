import telebot
import requests
import time
import json
from threading import Timer

# ايدي حسابك
ALLOWED_USER_IDS = [6033616268]
# توكن بوت
bot = telebot.TeleBot('7433110227:AAHlcgVzKQz-T-BS28rFCt1Ep10WTABTNEE')

# تحميل البيانات من ملف JSON
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

data = load_data()

# حفظ البيانات في ملف JSON
def save_data():
    with open('data.json', 'w') as file:
        json.dump(data, file)

@bot.message_handler(func=lambda message: message.from_user.id in ALLOWED_USER_IDS, content_types=['text'])
def handle_message(message):
    if message.text.startswith('/start'):
        bot.send_message(message.chat.id, 'Enter your phone number:')
        bot.register_next_step_handler(message, get_phone_number)
    elif message.text.startswith('/reset'):
        reset_bot(message)
    else:
        bot.send_message(message.chat.id, 'Invalid command. Please start with /start or /reset')

def reset_bot(message):
    bot.send_message(message.chat.id, 'Bot has been reset.')
    # Add any code here to clean up or reset the bot's state

def get_phone_number(message):
    num = message.text
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.9.3',
    }

    data_request = {
        'client_id': 'ibiza-app',
        'grant_type': 'password',
        'mobile-number': num,
        'language': 'AR',
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data_request)

    if 'ROOGY' in response.text:
        bot.send_message(message.chat.id, 'OTP code sent. Enter OTP:')
        bot.register_next_step_handler(message, get_otp, num)
    else:
        bot.send_message(message.chat.id, 'Error, please try again later.')

def get_otp(message, num):
    otp = message.text
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.9.3',
    }

    data_request = {
        'client_id': 'ibiza-app',
        'otp': otp,
        'grant_type': 'password',
        'mobile-number': num,
        'language': 'AR',
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data_request)

    access_token = response.json().get('access_token')
    if access_token:
        # حفظ البيانات في JSON
        data[num] = {
            'token': access_token,
            'otp': otp
        }
        save_data()

        bot.send_message(message.chat.id, 'Data saved. Internet will be sent every 20 minutes.')
        
        # بدء مهمة إرسال الإنترنت كل 20 دقيقة
        send_internet_periodically(num)
    else:
        bot.send_message(message.chat.id, 'Error verifying OTP.')

def send_internet_periodically(num):
    if num in data:
        access_token = data[num]['token']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'language': 'AR',
            'request-id': 'ef69f4c6-2ead-4b93-95df-106ef37feefd',
            'flavour-type': 'gms',
            'Content-Type': 'application/json'
        }

        payload = {
            "mgmValue": "ABC"  
        }

        response = requests.post('https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/mgm/info/apply', headers=headers, json=payload)
        
        if 'EU1002' in response.text:
            bot.send_message(data[num]['chat_id'], 'تم ارسال الانترنت')
        else:
            bot.send_message(data[num]['chat_id'], 'تحقق من الانترنت عندك الان وعد لاحقا ....')

        # إعداد مؤقت جديد لتكرار المهمة كل 20 دقيقة
        Timer(1200, send_internet_periodically, args=[num]).start()

# بدء البوت
bot.polling(none_stop=True)
