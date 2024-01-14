# -*- coding: utf-8 -*-

from config import NAME, VERSION, ALIASES, TBR, CMD_LIST
from core import Microphone, Voice

from fuzzywuzzy import fuzz
from datetime import datetime
from time import sleep

from num2t4ru import num2text
from webbrowser import get as web

from random import choice
from wikipediaapi import Wikipedia

from urllib.parse import quote_plus
from requests import get as requests

speak = Voice().speak
listen = Microphone().listen


def search_for_definition_on_wikipedia(text: str):
    wiki = Wikipedia('ru')
    wiki_page = wiki.page(text)
    try:
        if wiki_page.exists():
            web().open(wiki_page.fullurl)
            speak(str(wiki_page.summary.split(".")[:1]))
        else:
            url = f'https://yandex.ru/search/?text={quote_plus(text)}'
            web().open(url)

    except Exception as e:
        speak('Произошла какая-то ошибка')
        print(e)


def get_weather(city_name: str) -> None:
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        "q": city_name,
        "appid": "295f286d77a869327ed8dfae72a0542d",
        "units": "metric",
        "lang": "ru",
    }
    response = requests(url, params=params)
    if response.status_code != 200:
        speak("Извините, не могу получить данные о погоде")
        return
    data = response.json()
    weather = data['weather'][0]['description']
    temperature = round(data['main']['temp'])
    humidity = data['main']['humidity']
    wind_speed = round(data['wind']['speed'])
    result = f"В {city_name} {weather} ... {num2text(temperature)} градусов ..." \
             f" влажность {num2text(humidity)} процента ... скорость ветра {num2text(wind_speed)} метров в секунду"
    speak(result)


def search_for_video_on_youtube(text: str):
    url = f"https://www.youtube.com/results?search_query={quote_plus(text)}"
    web().open(url)

    speak(f"вот что я нашел по запросу ... {text} на ютубе")


def va_respond(voice: str):
    print(voice) if voice else None
    if voice.startswith(ALIASES):
        cmd = recognize_cmd(filter_cmd(voice))

        if cmd['cmd'] not in CMD_LIST.keys():
            speak("Что?")
        else:
            execute_cmd(cmd['cmd'], voice)


def filter_cmd(raw_voice: str) -> str:
    cmd = raw_voice.strip()

    for alias in ALIASES:
        cmd = cmd.removeprefix(alias)

    for word in TBR:
        cmd = cmd.replace(word, "")
    return cmd


def filter_search(voice: str, cmd: str) -> str:
    if 'найди' in voice:
        voice = voice.replace('найди', '')
    for word in CMD_LIST[cmd]:
        voice = voice.replace(word, '').strip()

    for alias in ALIASES:
        voice = voice.removeprefix(alias).strip()

    return voice


def recognize_cmd(cmd: str) -> dict:
    recognize = {'cmd': '', 'percent': 0}
    for values, keys in CMD_LIST.items():
        for value in keys:
            vrt = fuzz.ratio(cmd, value)
            if vrt > recognize['percent']:
                recognize['cmd'] = values
                recognize['percent'] = vrt

    return recognize


def execute_cmd(cmd: str, voice: str) -> None:
    search_text = filter_search(voice, cmd)
    commands = {
        'help': lambda: speak("Я умею: ... произносить время ... рассказывать анекдоты ... и открывать браузер"),
        'time': lambda: speak(f"Сейчас {num2text(datetime.now().hour)} {num2text(datetime.now().minute)}"),
        'joke': lambda: speak(choice(['Как смеются программисты? ... ехе ехе ехе',
                                      'ЭсКьюЭль запрос заходит в бар, подходит к двум столам и спрашивает'
                                      ' .. «можно присоединиться?»',
                                      'Программист это машина для преобразования кофе в код'])),
        'search': lambda: search_for_definition_on_wikipedia(search_text),
        'youtube': lambda: search_for_video_on_youtube(search_text),
        'close': lambda: (speak(f"возвращайтесь скорее без вас мне будет скучно"), sleep(0.1), quit()),
        'open_browser': lambda: web().open("https://google.com"),
        'weather': lambda: get_weather(search_text),
    }

    if cmd in commands:
        commands[cmd]()
    else:
        speak(f"Команда {cmd} не найдена. Попробуйте еще раз.")


if __name__ == '__main__':
    try:
        print(f"{NAME} (v{VERSION}) начал свою работу ...")
        speak(f"{NAME} начал свою работу ...")
        listen(va_respond)
    except KeyboardInterrupt:
        speak(f"возвращайтесь скорее без вас мне будет скучно")
        sleep(0.1)
        quit()
