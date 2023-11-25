import telebot
from pytube import YouTube
import os

TOKEN = '6469448180:AAGCbMlI2mEe2foARHIuY_ytqatMVPqMMG0'
bot = telebot.TeleBot(TOKEN)

users = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать! Введите ваше имя:')
    bot.register_next_step_handler(message, register)


def register(message):
    users[message.chat.id] = {'name': message.text}
    bot.send_message(message.chat.id,
                     f'Привет, {message.text}! Отправьте мне ссылку на YouTube видео для скачивания.')


@bot.message_handler(func=lambda message: True)
def send_video_options(message):
    url = message.text
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')
    options = {str(i + 1): stream for i, stream in enumerate(streams)}
    reply_markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for option, stream in options.items():
        reply_markup.row(telebot.types.KeyboardButton(f"{option}: {stream.resolution}"))
    bot.send_message(message.chat.id, "Выберите качество видео:", reply_markup=reply_markup)
    bot.register_next_step_handler(message, download_video, options)

def download_video(message, options):
    choice = message.text.split(":")[0]
    if choice in options:
        stream = options[choice]
        bot.send_message(message.chat.id, "Скачиваю видео...")
        stream.download()
        video_file = open(stream.default_filename, 'rb')
        bot.send_video(message.chat.id, video_file)
        video_file.close()
        os.remove(stream.default_filename)
    else:
        bot.send_message(message.chat.id, "Неверный выбор.")

bot.infinity_polling()

#
# @bot.message_handler(func=lambda message: True)
# def download_video(message):
#     if message.chat.id in users:
#         try:
#             yt = YouTube(message.text)
#             video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
#             video.download()
#             video_file = open(video.default_filename, 'rb')
#             bot.send_video(message.chat.id, video_file)
#             video_file.close()
#             os.remove(video.default_filename)
#         except Exception as e:
#             bot.send_message(message.chat.id, f'Ошибка: {e}')
#     else:
#         bot.send_message(message.chat.id, 'Зарегистрируйтесь сначала, /start.')
#
#
# bot.infinity_polling()
