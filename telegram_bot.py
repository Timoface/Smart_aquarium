import dotenv
from os import getenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import commands

dotenv.load_dotenv()
TOKEN = getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    start_message = ("<b>Привет! Это бот для управления умным аквариумом! 🐟\n"
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


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
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
    elif call.data == "feed_big":
        bot.answer_callback_query(call.id, "Большие рыбки накормлены! 🐠🥬")
        commands.feed_big()
    elif call.data == "temperature":
        temperature = commands.temperature()
        bot.answer_callback_query(call.id, f"Температура воды: {temperature}°C 🌡")
    elif call.data == "light":
        bot.answer_callback_query(call.id, "Свет переключен! 💡")
        commands.light()


if __name__ == '__main__':
    bot.infinity_polling()
