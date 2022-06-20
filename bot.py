import telebot
import time
from telebot import types
import requests
import json
from webbrowser import get
import sqlite3
token = '<Your token>'
bot = telebot.TeleBot(token)
name1 = None
busies = None
done = False
btc_usdt = None
eth_usdt = None
usd_rub = None
eur_rub = None
sol_usdt = None
temp = None
condition = None
secret_text = None
secret_pass = None
feels_like = None

with sqlite3.connect("data.db") as db:
    cursor = db.cursor()
    query = """CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        name VARCHAR(30),
        busies TEXT(500),
        admin NOT NULL DEFAULT 1,
        banned DEFAULT 0
    )"""
    cursor.executescript(query)

@bot.message_handler(commands=['start'])
def greeting_message(message):
     startmsg = bot.send_message(message.chat.id, "Привет👋\n\nЯ - твой личный помощник, каждый день буду составлять тебе распорядок дня и присылать свежие данные🗒\n\nЧтобы начать, введи своё имя ⬇️")
     bot.register_next_step_handler(startmsg, busy)

@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Мой Распорядок Дня")
    markup.add(btn)
    bot.send_message(message.chat.id, "Сейчас загружу меню...", reply_markup=markup)
    donee_reload(message)

@bot.message_handler(commands=['admin'])
def admin_menu(message):
    user_id = message.from_user.id
    if user_id == 1274013505:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(text='📣Рассылка', callback_data='post')
        btn2 = types.InlineKeyboardButton(text='📊Статистика', callback_data='stats')
        btn3 = types.InlineKeyboardButton(text='🔴Забанить', callback_data='ban')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Здравствуй, Илья 🌟\nВот команды админ меню: ", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Вы не админ, у вас нет доступа к этому меню.")

@bot.callback_query_handler(func= lambda call: True)
def adm_functions(call):
    if call.data == 'post':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='⬅️ Назад', callback_data='back')
        markup.add(button)
        ass = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Введите текст для рассылки', reply_markup=markup)
        bot.register_next_step_handler(ass, post)
    elif call.data == 'stats':
        stats(call.message)
    elif call.data == 'ban':
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='⬅️ Назад', callback_data='back')
        markup.add(button)
        assip = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Введи ID пользователя, которого хочешь забанить', reply_markup=markup)
        bot.register_next_step_handler(assip, ban)
    elif call.data == 'back':
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(text='📣Рассылка', callback_data='post')
        btn2 = types.InlineKeyboardButton(text='📊Статистика', callback_data='stats')
        btn3 = types.InlineKeyboardButton(text='🔴Забанить', callback_data='ban')
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Здравствуй, Илья 🌟\nВот команды админ меню: ', reply_markup=markup)
    elif call.data == 'change_busies':
        markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('Отмена')
        markup2.add(btn)
        be = bot.send_message(call.message.chat.id, "Все дела закончены? Отлично! 👌 \nТеперь напиши мне новый список дел", reply_markup=markup2)
        bot.register_next_step_handler(be, reload_busies)
    elif call.data == 'crypto':
        currency1(call.message)


def post(message):
    if message.text != "Мой Распорядок дня":
     db = sqlite3.connect("data.db")
     cursor = db.cursor()
     post_text = message.text
     cursor.execute("SELECT user_id FROM users")
     users = cursor.fetchall()
     for u in users:
        user = u[0]
        bot.send_message(user, post_text)
    else:
        donee_reload(message)

def ban(message):
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    ban_user = message.text
    cursor.execute("SELECT banned FROM users WHERE user_id = ?;",(ban_user,))
    is_banned = cursor.fetchone()
    if is_banned != None:
     cursor.execute("UPDATE users SET banned = 1 WHERE user_id = ?;",(ban_user,))
     db.commit()
     bot.send_message(message.chat.id, "Пользователь забанен \nДля разбана напиши /unban ID")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден, или вы ввели неправильный ID")

@bot.message_handler(commands=['unban'])
def unban(message):
    if message.from_user.id == 1274013505:
     db = sqlite3.connect("data.db")
     cursor = db.cursor()
     bui = message.text
     try:
      banned_id = int(bui[6:])
      cursor.execute("UPDATE users SET banned = 0 WHERE user_id = ?;",(banned_id,))
      db.commit()
     except ValueError:
        bot.send_message(message.chat.id, "Вы не ввели ID пользователя \nПравильное использование команды /unban ID")
    else:
        bot.send_message(message.chat.id, "Вы не админ, у вас нет доступа к этой команде.")

def stats(message):
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM users")
    us = cursor.fetchall()
    users = len(us)
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='⬅️ Назад', callback_data='back')
    markup.add(button)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f'Общее число пользователей бота: {users}', reply_markup=markup)

def busy(message):
    global name1
    name1 = message.text
    ps = bot.send_message(message.chat.id, f"Здравствуй, {name1} \nТеперь напиши несколько самых важных дел на день\nВот Так:\nДело 1\nДело 2\nДело 3")
    bot.register_next_step_handler(ps, donee)

def donee(message):
    global btc_usdt, eth_usdt, sol_usdt, eur_rub, usd_rub, done, temp, condition, feels_like, name1
    currencies()
    weather()
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    try:
        busies = message.text
        user_id = message.from_user.id
        cursor.execute("INSERT INTO users(user_id, name, busies) VALUES(?, ?, ?)",(user_id,name1,busies))
        db.commit()
        cursor.execute("SELECT name, busies FROM users WHERE user_id = ?;",(user_id,))
        busies1 = cursor.fetchone()
        print(busies1)
    except sqlite3.Error as e:
        print("SQL Error: ", e)
    ass = bot.send_message(message.chat.id, "Почти все готово! ✅ \n\nСейчас подготовлю твой список дел...")
    time.sleep(2)
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='📋 Поменять список дел', callback_data='change_busies')
    btn2 = types.InlineKeyboardButton(text='💸 Узнать курс криптовалюты', callback_data='crypto')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f"Здравствуй, {name1} 🌟\n========================\nВот твои дела на день:\n{busies}\n========================\n🅱️BTC: {btc_usdt}$ \n💠ETH: {eth_usdt}$ \n🌀SOL: {sol_usdt}$ \n💵USD: {usd_rub}₽\n💶EUR: {eur_rub}₽\n========================\n{condition} +{temp}\nОщущается как: +{feels_like}", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def shedule(message):
    if message.text == "Мой Распорядок Дня":
        donee_reload(message)
    if message.text == "Отмена":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("Мой Распорядок Дня")
        markup.add(btn)
        bot.send_message(message.chat.id, "Отменяю..", reply_markup=markup)

def currency1(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = "Отмена"
    markup.add(btn)
    isi = bot.send_message(message.chat.id, "Пришлите мне название валюты на английском, курс которой хотите узнать 💸", reply_markup=markup)
    bot.register_next_step_handler(isi, custom_currency)

def reload_busies(message):
    global busies
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    user_id = message.from_user.id
    if message.text != "Отмена":
     try: 
         cursor.execute("UPDATE users SET busies = ? WHERE user_id = ?;",(message.text, user_id))
         db.commit()
         cursor.execute("SELECT busies FROM users WHERE user_id = ?;",(user_id,))
         busiesl = cursor.fetchone()
         print(busiesl)
         busies = busiesl[0]
         print(busies)
     except sqlite3.Error as e:
        print("SQL error: ", e)
    donee_reload(message)


def donee_reload(message):
    global btc_usdt, eth_usdt, sol_usdt, eur_rub, usd_rub, temp, condition, name1, busies, feels_like
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    user_id = message.from_user.id
    busies = None
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='📋 Поменять список дел', callback_data='change_busies')
    btn2 = types.InlineKeyboardButton(text='💸 Узнать курс криптовалюты', callback_data='crypto')
    markup.add(btn1, btn2)
    try:
        cursor.execute("SELECT busies, name FROM users WHERE user_id = ?;", (user_id,))
        busies1 = cursor.fetchone()
        busies = busies1[0]
        name1 = busies1[1]
    except sqlite3.Error as e:
        print("Error: ", e)
    weather()
    currencies()
    bot.send_message(message.chat.id, f"Здравствуй, {name1} 🌟\n========================\nВот твои дела на день:\n{busies}\n========================\n🅱️BTC: {btc_usdt}$ \n💠ETH: {eth_usdt}$ \n🌀SOL: {sol_usdt}$ \n💵USD: {usd_rub}₽\n💶EUR: {eur_rub}₽\n========================\n{condition} +{temp}\nОщущается как: +{feels_like}", reply_markup=markup)

def currencies():
    global btc_usdt, eth_usdt, sol_usdt, eur_rub, usd_rub
    response = requests.get(url="https://api.coingecko.com/api/v3/coins/bitcoin")
    jresponse = json.loads(response.text)
    btc_usdt = str(round(jresponse.get("market_data").get("current_price").get("usd")))
    response2 = requests.get(url="https://api.coingecko.com/api/v3/coins/ethereum")
    jresponse2 = json.loads(response2.text)
    eth_usdt = str(round(jresponse2.get("market_data").get("current_price").get("usd")))
    response3 = requests.get(url="https://api.coingecko.com/api/v3/coins/solana")
    jresponse3 = json.loads(response3.text)
    sol_usdt = str(round(jresponse3.get("market_data").get("current_price").get("usd")))
    response_fiat = requests.get(url="https://www.cbr-xml-daily.ru/daily_json.js")
    jfiat = json.loads(response_fiat.text)
    usd_rub = str(round(jfiat.get("Valute").get("USD").get("Value")))
    eur_rub = str(round(jfiat.get("Valute").get("EUR").get("Value")))

def custom_currency(message):
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    user_id = message.from_user.id
    cursor.execute("SELECT banned FROM users WHERE user_id = ?;",(user_id,))
    is_banned = cursor.fetchone()[0]
    if is_banned == 0:
     if message.text != "Отмена":
      coin = message.text
      response = requests.get(url=f"https://api.coingecko.com/api/v3/coins/{coin}")
      jresp = json.loads(response.text)
     try:
      custom_value = str(round(jresp.get("market_data").get("current_price").get("usd")))
     except AttributeError:
        bot.send_message(message.chat.id, "Вы ввели неверное название, или ввели его с маленькой буквы")
        bot.send_message(message.chat.id, f"{coin} - USD: {custom_value}$")
     else:
        donee_reload(message)
    else:
        bot.send_message(message.chat.id, "Вы заблокированы администраторам. \n__Не согласен? Пиши - @risely__", parse_mode="Markdown")

def weather():
    global temp, condition, feels_like
    weather1 = requests.get(url="https://api.weather.yandex.ru/v2/forecast?lat=53.507852&lon=49.420411", headers={"X-Yandex-API-Key" : "8e45e1a6-86fb-44ce-8035-480574a446df"})
    jweather = json.loads(weather1.text)
    act_weather = str(jweather.get("fact").get("temp"))
    temp = act_weather
    pre_condition = str(jweather.get("fact").get("condition"))
    feels_like = str(jweather.get("fact").get("feels_like"))
    if pre_condition == "overcast":
        condition = "☁️ Пасмурно"
    elif pre_condition == "partly-cloudy":
        condition = "⛅️ Малооблачно"
    elif pre_condition == "clear":
        condition = "☀️ Ясно"
    elif pre_condition == "cloudy":
        condition = "🌥 Облачно с прояснениями"
    elif pre_condition == "drizzle":
        condition = "💧 Мелкий дождь (морось)"
    elif pre_condition == "light-rain":
        condition = "💦 Небольшой дождь"
    elif pre_condition == "rain":
        condition = "🌧 Дождь"
    elif pre_condition == "moderate-rain":
        condition = "🌧 Умеренно сильный дождь"
    elif pre_condition == "heavy-rain":
        condition = "🌧 Сильный дождь"
    elif pre_condition == "continous-heavy-rain":
        condition = "🌧 Продолжительный сильный дождь"
    elif pre_condition == "showers":
        condition = "🌊 Ливень"
    elif pre_condition == "wet-snow":
        condition = "🌨 Снег с дождём"
    elif pre_condition == "snow":
        condition = "❄️ Снег"
    elif pre_condition == "thunderstorm":
        condition = "🌩 Гроза"
    elif pre_condition == "thunderstorm-with-rain":
        condition = "⛈ Дождь с грозой"
    print(temp, pre_condition)


bot.infinity_polling()

    


