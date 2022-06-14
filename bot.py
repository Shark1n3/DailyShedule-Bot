import telebot
import time
from telebot import types
import requests
import json
from webbrowser import get
token = '5433287136:AAFkvFzi0AhAKhpjTlwk38lXXEZ-HMIPeAE'
bot = telebot.TeleBot(token)
name = None
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

@bot.message_handler(commands=['start'])
def greeting_message(message):
    startmsg = bot.send_message(message.chat.id, "Привет👋\n\nЯ - твой личный помощник, каждый день буду составлять тебе распорядок дня и присылать свежие данные🗒\n\nЧтобы начать, введи своё имя ⬇️")
    bot.register_next_step_handler(startmsg, busy)

def busy(message):
    global name
    name = message.text
    ps = bot.send_message(message.chat.id, f"Здравствуй, {name} \nТеперь напиши несколько самых важных дел на день\nВот Так:\nДело 1\nДело 2\nДело 3")
    bot.register_next_step_handler(ps, donee)

def donee(message):
    global btc_usdt, eth_usdt, sol_usdt, eur_rub, usd_rub, done, busies, temp, condition
    currencies()
    weather()
    ass = bot.send_message(message.chat.id, "Почти все готово! ✅ \n\nСейчас подготовлю твой список дел...")
    busies = message.text
    time.sleep(2)
    markup_inline = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_btn1 = types.KeyboardButton('Мой Распорядок Дня')
    item_btn2 = types.KeyboardButton('Поменять Список Дел')
    item_btn3 = types.KeyboardButton('Узнать Курс Криптовалюты')
    markup_inline.add(item_btn1, item_btn2, item_btn3)
    bot.send_message(message.chat.id, f"Здравствуй, {name} 🌟\n========================\nВот твои дела на день:\n{busies}\n========================\n🅱️BTC: {btc_usdt}$ \n💠ETH: {eth_usdt}$ \n🌀SOL: {sol_usdt}$ \n💵USD: {usd_rub}₽\n💶EUR: {eur_rub}₽\n========================\n{condition} +{temp}", reply_markup=markup_inline)

@bot.message_handler(content_types=['text'])
def shedule(message):
    if message.text == "Поменять Список Дел":
        reload = bot.send_message(message.chat.id, "Все дела закончены? Отлично!👌 \nТеперь напиши мне новый список дел")
        bot.register_next_step_handler(reload, reload_busies)
    elif message.text == "Мой Распорядок Дня":
        donee_reload(message)
    elif message.text == "Узнать Курс Криптовалюты":
        currency1(message)
    elif message.text == "Мои Секреты":
        secrets(message)

def secrets(message):
    global secret_text
    if secret_text != None:
        secrets_pass(message)
    else:
     sg = bot.send_message(message.chat.id, "Эй, а ты знал, что я умею хранить секреты? 😉 \nНапиши мне что-нибудь, что хотел бы оставить в секрете, и я буду надежно хранить эту информацию под паролем 🔑")
     bot.register_next_step_handler(sg, secrets2)

def secrets2(message):
    global secret_text
    secret_text = message.text
    st = bot.send_message(message.chat.id, "Хорошо, я всё записал 👌 \nТеперь придумай пароль, только с помощью него можно получить доступ к этой информации")
    bot.register_next_step_handler(st, secret_pass_go)

def secret_pass_go(message):
    global secret_pass
    secret_pass = message.text
    bot.send_message(message.chat.id, "Всё готово! ✅ \nТеперь ты можешь получить доступ к своим секретам с помощью кнопки из главного меню")

def secrets_pass(message):
    markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('Удалить Секрет')
    markup2.add(btn)
    hy = bot.send_message(message.chat.id, "Введи пароль для доступа к секретной информации", reply_markup=markup2)
    bot.register_next_step_handler(hy, enter_pass)

def enter_pass(message):
    global secret_pass, secret_text
    if message.text == secret_pass:
        bot.send_message(message.chat.id, secret_text)
    else:
        bot.send_message(message.chat.id, "Пароль не верный")


def currency1(message):
    isi = bot.send_message(message.chat.id, "Пришлите мне название валюты на английском, курс которой хотите узнать 💸")
    bot.register_next_step_handler(isi, custom_currency)

def reload_busies(message):
    global busies
    busies = message.text
    donee_reload(message)


def donee_reload(message):
    global btc_usdt, eth_usdt, sol_usdt, eur_rub, usd_rub, temp, condition
    weather()
    currencies()
    bot.send_message(message.chat.id, f"Здравствуй, {name} 🌟\n========================\nВот твои дела на день:\n{busies}\n========================\n🅱️BTC: {btc_usdt}$ \n💠ETH: {eth_usdt}$ \n🌀SOL: {sol_usdt}$ \n💵USD: {usd_rub}₽\n💶EUR: {eur_rub}₽\n========================\n{condition} +{temp}")

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
    coin = message.text
    response = requests.get(url=f"https://api.coingecko.com/api/v3/coins/{coin}")
    jresp = json.loads(response.text)
    try:
     custom_value = str(round(jresp.get("market_data").get("current_price").get("usd")))
    except AttributeError:
        bot.send_message(message.chat.id, "Вы ввели неверное название, или ввели его с маленькой буквы")
    bot.send_message(message.chat.id, f"{coin} - USD: {custom_value}$")

def weather():
    global temp, condition
    weather1 = requests.get(url="https://api.weather.yandex.ru/v2/forecast?lat=53.5303&lon=49.3461", headers={"X-Yandex-API-Key" : "8e45e1a6-86fb-44ce-8035-480574a446df"})
    jweather = json.loads(weather1.text)
    act_weather = str(jweather.get("fact").get("temp"))
    temp = act_weather
    pre_condition = str(jweather.get("fact").get("condition"))
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

# 13.06 content types [text]
# Поискать API курсы фиатных валют
# Декорация

# 14.06
# Точная погода по кнопочке
# Купить сервак и залить туда бота

# Итого бот разработан за 3 дня, по 5 часов в день.

    


