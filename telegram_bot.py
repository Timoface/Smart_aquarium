import dotenv
import os
import datetime
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import commands

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

def load_last_data():
    try:
        with open("last_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_last_data(data):
    with open("last_data.json", "w") as file:
        json.dump(data, file, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    start_message = ("<b>Привет! Это бот для управления умным аквариумом! 🐟\n"
                     "Ты можешь ввести команду /last для указания последних измерений аквариума! 📏\n"
                     "Выбери, что ты хочешь сделать! 👇</b>")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text="Покормить рыбок 🥬",
        callback_data="feed"
    ))
    markup.add(InlineKeyboardButton(
        text="Узнать температуру воды 🌡",
        callback_data="temperature"
    ))
    markup.add(InlineKeyboardButton(
        text="Переключить свет 💡",
        callback_data="light"
    ))

    bot.send_message(
        text=start_message,
        parse_mode="HTML",
        chat_id=message.chat.id,
        reply_markup=markup
    )

@bot.message_handler(commands=['last'])
def last(message):
    last_data = load_last_data()

    if not last_data:
        bot.send_message(
            chat_id=message.chat.id,
            text="<b>Нет данных о последних измерениях.</b>",
            parse_mode="HTML"
        )
        return

    response = "<b>Последние измерения: 📏</b>\n\n"

    if "last_feed_small" in last_data:
        response += f"🐟 <b>Маленькие рыбки покормлены:</b> {last_data['last_feed_small']}\n"
    if "last_feed_big" in last_data:
        response += f"🐠 <b>Большие рыбки покормлены:</b> {last_data['last_feed_big']}\n"
    if "last_temperature" in last_data:
        response += f"🌡 <b>Температура воды:</b> {last_data['last_temperature']['value']}°C (измерено: {last_data['last_temperature']['time']})\n"
    if "last_light_toggle" in last_data:
        response += f"💡 <b>Свет переключен:</b> {last_data['last_light_toggle']}\n"

    bot.send_message(
        chat_id=message.chat.id,
        text=response,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    last_data = load_last_data()

    if call.data == "feed":
        feed_markup = InlineKeyboardMarkup()
        feed_markup.add(InlineKeyboardButton(
            text="Покормить маленьких рыбок 🐟",
            callback_data="feed_small"
        ))
        feed_markup.add(InlineKeyboardButton(
            text="Покормить больших рыбок 🐠",
            callback_data="feed_big"
        ))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="<b>🗒 Выбери, кого ты хочешь покормить:</b>",
            reply_markup=feed_markup,
            parse_mode="HTML"
        )
    elif call.data == "feed_small":
        bot.answer_callback_query(call.id, "Маленькие рыбки накормлены! 🐟🥬")
        commands.feed_small()
        last_data["last_feed_small"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_last_data(last_data)
    elif call.data == "feed_big":
        bot.answer_callback_query(call.id, "Большие рыбки накормлены! 🐠🥬")
        commands.feed_big()
        last_data["last_feed_big"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_last_data(last_data)
    elif call.data == "temperature":
        temperature = commands.temperature()
        bot.answer_callback_query(call.id, f"Температура воды: {temperature}°C 🌡")
        last_data["last_temperature"] = {
            "value": temperature,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_last_data(last_data)
    elif call.data == "light":
        bot.answer_callback_query(call.id, "Свет переключен! 💡")
        commands.light()
        last_data["last_light_toggle"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_last_data(last_data)


if __name__ == '__main__':
    bot.infinity_polling()