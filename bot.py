import sys
import configparser
import redis
import textwrap
import telebot
import os
from datetime import date
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from telebot import types

config = configparser.ConfigParser()
config.sections()
config.read('bot.conf')

TOKEN = config['BOT']['TOKEN']

bot = telebot.TeleBot(TOKEN)

def redis_get(chatid): # Redis - Ler valor
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r.get(chatid).decode('utf-8')

def redis_set(chatid, val): # Redis - Escrever valor
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.set(chatid, val)

menu_series = types.InlineKeyboardMarkup()
menu_series.row(types.InlineKeyboardButton('Bridgerton', callback_data="Bridgerton.jpeg"))
menu_series.row(types.InlineKeyboardButton('Elite', callback_data="Elite.jpeg"))
menu_series.row(types.InlineKeyboardButton('Emily Em Paris', callback_data="EmilyEmParis.jpeg"))
menu_series.row(types.InlineKeyboardButton('Eu Nunca', callback_data="EuNunca.jpeg"))
menu_series.row(types.InlineKeyboardButton('Lucifer', callback_data="Lucifer.jpeg"))
menu_series.row(types.InlineKeyboardButton('Lupin', callback_data="Lupin.jpeg"))
menu_series.row(types.InlineKeyboardButton('Round6', callback_data="Round6.jpeg"))
menu_series.row(types.InlineKeyboardButton('Sex Education', callback_data="SexEducation.jpeg"))
menu_series.row(types.InlineKeyboardButton('Vicenzo', callback_data="Vicenzo.jpeg"))

@bot.callback_query_handler(lambda q: True)
def set_serie(call):
    redis_set(call.from_user.id, call.data)
    bot.answer_callback_query(call.id, call.data.replace('.jpeg', ''))

@bot.message_handler(commands=['start', 'serie', 'Serie'])
def set_serie(message):
    bot.send_message(message.from_user.id, "Escolha a série:", parse_mode='HTML', reply_markup=menu_series)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    Create_Image(message)

def Create_Image(message):
    bot.send_chat_action(message.from_user.id, 'upload_document')

    nome = message.text
    data_hoje = date.today().strftime("%d/%m/%Y")
    assinatura = 'AcademiaNetflixBot'
    fonte_nome = ImageFont.truetype('SCRIPTIN.ttf', 88)
    fonte_assinatura = ImageFont.truetype('SCRIPTIN.ttf', 35)
    fonte_data = ImageFont.truetype('eb-garamond.ttf', 50)

    try:
        img = Image.open(redis_get(message.from_user.id))
    except AttributeError:
        set_serie(message)
        return

    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(nome, font = fonte_nome)
    draw.text((1000-w/2,811), nome, (0,0,0), font = fonte_nome)
    draw.text((350,1213), data_hoje, (0,0,0), font = fonte_data)
    draw.text((1420,1195), assinatura, (0,0,0), font = fonte_assinatura)

    img.save(str(message.from_user.id) + '.jpg')
    photo = open(str(message.from_user.id) + '.jpg', 'rb')
    bot.send_photo(message.from_user.id, photo)
    os.remove(str(message.from_user.id) + '.jpg')
bot.polling(none_stop=True)

