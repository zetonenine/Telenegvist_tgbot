import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from utils import TestStates
from postgresql import Pstrgsqler
from mongodb import Mongodb
from time import sleep
import asyncio
from redis_file import Redis
import os
import requests
import logging
import speech_recognition as sr
from speech_recognition import Recognizer
from pydub import AudioSegment
import pyttsx3
import soundfile as sf
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())

db = Pstrgsqler()
mng = Mongodb()
r = Redis()

recoq = Recognizer()

AudioSegment.converter = os.getcwd() + "/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffmpeg = os.getcwd() + "/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = os.getcwd() + "/ffmpeg/bin/ffprobe.exe"

# print(sr.Microphone.list_microphone_names())

text_to_speach = pyttsx3.init()
# voices = text_to_speach.getProperty('voices')
# for voice in voices:
#     print('--------------------')
#     print('Имя: %s' % voice.name)
#     print('ID: %s' % voice.id)


RU_VOICE_ID = "com.apple.speech.synthesis.voice.yuri.premium"
text_to_speach.getProperty('voice')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    mng.add_new_user(message.from_user.id)
    await message.reply('Привет, отправь войс')

    # db.create_words_tab()
    # db.create_unique_user_tab(message.from_user.id)
    # db.create_users_tab()


@dp.message_handler(commands=['addword'])
async def start(message: types.Message):
    await TestStates.add_new_word_state.set()
    await message.answer('Отправь сообщение в формате {word}={sentence}={translate}={1-5}')


@dp.message_handler(state=TestStates.add_new_word_state, commands=['stopadd'])
async def stop_add_word(message: types.Message, state: FSMContext):
    await message.answer('Не будем добавлять')
    await state.reset_state()


@dp.message_handler(state=TestStates.add_new_word_state, content_types=['text'])
async def add_word(message: types.Message, state: FSMContext):
    obj = message.text
    values = obj.split('=')
    if len(values) == 4:
        mng.adding_word_manually(values)
        await message.answer('Добавил новое слово ' + values[0])
    else:
        await message.answer('Ошибка в формате ввода, попробуй ещё раз')
    await state.reset_state()


@dp.message_handler(commands=['startpack'])
async def start_pack(message: types.Message):

    """ Запускается стейт, внутри которого все сообщения будут
        восприниматься как ответы на вопрос.
        Отправвляется запрос в Монгу, готовиться очередь из слов
    """

    await TestStates.pack_showing_state.set()
    await message.answer('Подготавливаем пак..')
    user_id = message.from_user.id

    mng.create_queue(user_id)
    que = r.stack_queue(user_id)
    gen = asyncio.create_task(asker(message, que))
    r.del_answers(user_id) # очищает стек с ответами, если там что-то есть
    await asyncio.gather(gen)


@dp.message_handler(state=TestStates.pack_showing_state, commands=['stoppack'])
async def stop_pack(message: types.Message, state: FSMContext):

    """ Команда для прекращения подачи слов и отключения стейта """

    await state.reset_state()
    mng.changing_levels(message.from_user.id)
    await message.answer('Заканчиваем пак')


async def asker(message, que):

    """ Генератор, который задаёт вопрос """

    text = f'{que[2]}\nПеревод: {que[3]}'
    await bot.send_message(message.from_user.id, text)


@dp.message_handler(state=TestStates.pack_showing_state, content_types=['text'])
async def loop(message: types.Message, state: FSMContext):

    """ loop реагирует только на сообщения текстового формата, тем самым ожидая ответ от юзера
        делает проверку на верность ответа, и после запускает генератор asker(), который задаёт вопрос
    """

    ans = message.text
    user_id = message.from_user.id

    que = r.stack_queue(user_id)
    r.check_queue(user_id)

    if ans == que[1]:
        await message.answer('Верно!')

        # Level: 0. Repeat - No. Уровень становится 6, позже перейдет в learned
        if que[4] == 0:
            obj = {"word_id": que[0], 'lvl': 6}
            r.add_answer(user_id, obj)

        # Level: 1. Repeat - Yes.
        if que[4] == 1:
            que[4] += 1
            obj = {"word_id": que[0], 'lvl': que[4]}
            r.re_add_word(message.from_user.id, que)

        # Level: 2. Repeat - Yes. Добавлятся в стек снова для повторного изучения
        elif que[4] == 2:
            que[4] += 1
            obj = {"word_id": que[0], 'lvl': que[4]}
            r.add_answer(user_id, obj)

        # Level: 3-5. Repeat - No. Если que[5] True, то уровень повышается. False - остаётся на том же месте
        if len(que) > 5:

            if que[5]:
                que[4] += 1
                obj = {"word_id": que[0], 'lvl': que[4]}

            elif not que[5]:
                obj = {"word_id": que[0], 'lvl': que[4]}

            r.add_answer(user_id, obj)

    else:
        await message.answer(f'Неверно :(\nПравильный ответ: {que[1]}')

        # Level: 0. Делает лвл'ом 1
        if que[4] == 0:
            que[4] += 1

        # Проверка на 3-5 лвлы. Метка T/F может быть только у этих лвл'ов
        if len(que) > 5 and que[5]:
            que[5] = False

        r.re_add_word(message.from_user.id, que)

    try:
        que = r.stack_queue(message.from_user.id)
        gen = asyncio.create_task(asker(message, que))
        await asyncio.gather(gen)
    except:
        mng.changing_levels(message.from_user.id)
        await message.answer(f'Молодец! Пак закончен!')
        await state.reset_state()


@dp.message_handler(content_types=['voice'])
async def voice_messages_resender(message: types.voice):
    await bot.send_message(message.from_user.id, 'еще' + message.voice.file_id)

    print('__________________')
    file_info = bot.get_file(message.from_user.id)
    print(file_info)
    print('__________________')

    print('')
    print('__________________')
    file_path = requests.get(f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={message.voice.file_id}')
    print(file_path)
    print('__________________')

    print('')
    print('__________________')
    file = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path}')
    print(file)
    print('__________________')

    # data, samplerate = sf.read(file_path)
    # sf.write('template/new_file222222.ogg', data, samplerate)

    # print()
    # print('__________________')
    # print(requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'))
    # print('__________________')

    # file_path = requests.get(f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={message.voice.file_id}').json()['result']['file_path']
    # file = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path}')

    # data, samplerate = sf.read('template/my_audio.wav')
    # sf.write('new_file.wav', data, samplerate)

    await bot.send_message(message.from_user.id, 'о да')


# def sound_catcher():
#     mic = sr.Microphone(2)
#     with mic as audio_file:
#         print("\nСколько будет 7+3?\n")
#
#         recoq.adjust_for_ambient_noise(audio_file)
#         audio_content = recoq.listen(audio_file)
#
#         print("Converting Speech to Text...")
#
#         try:
#             text = recoq.recognize_google(audio_content, language= 'ru-RU')
#             text = text.split()
#             for i in text:
#                 if i.lower() == num:
#                     print('\nДа, правильно!\n🎊 🎊 🎊 🎊')
#                     return
#
#             # print("You said: " + text)
#         except:
#             print("Неправильно, лох")
#
#
#
# sound_catcher()

# with sample_audio as audio_file:
#     recoq.adjust_for_ambient_noise(audio_file)
#     audio_content = recoq.record(audio_file, duration=7)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
