import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import requests
import bs4 as bs4
import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import pyowm
import time
import json
import os
import wikipedia


class VkBot:

    def __init__(self, token):
        super(VkBot, self).__init__()
        self._COMMANDS = ["ПРИВЕТ", "ПОГОДА", "ВРЕМЯ", "ПОКА", "ПОИСК"]
        vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(vk_session)
        self.vk = vk_session.get_api()
        print("Создан объект бота!")

    def get_user_name(self, user_id):
        request = requests.get("https://vk.com/id" + str(user_id))
        bs = bs4.BeautifulSoup(request.text, "html.parser")
        user_name = self._clean_all_tag_from_str(bs.findAll("title")[0])
        return user_name.split()[0]

    @staticmethod
    def _clean_all_tag_from_str(string_line):

        """
        Очистка строки stringLine от тэгов и их содержимых
        :param string_line: Очищаемая строка
        :return: очищенная строка
        """

        result = ""
        not_skip = True
        for i in list(string_line):
            if not_skip:
                if i == "<":
                    not_skip = False
                else:
                    result += i
            else:
                if i == ">":
                    not_skip = True

        return result

    def get_time(self):
        today = datetime.datetime.today()
        return '/your city/ время: ' + today.strftime("%H:%M:%S")

    def get_weather(self, user_id):
        owm = pyowm.OWM('/your token/', language="RU")
        observation = owm.weather_at_place('/your city/', '/your country/')
        w = observation.get_weather()
        t = w.get_temperature('celsius')['temp']
        return "В городе /your city/ сейчас " + str(w.get_detailed_status()) + \
               ". Температура в районе " + str(t) + " градусов"

    def wiki_inf(self, event):
        wikipedia.set_lang("/your country/")
        self.vk.messages.send(user_id=event.user_id, message="Введите ваш запрос",
                              random_id=int(random.random() * 100000000000000000))
        for sub_event in self.longpoll.listen():
            if sub_event.type == VkEventType.MESSAGE_NEW and sub_event.to_me and sub_event.text:
                print('New message:')
                print('For me by: ', self.get_user_name(event.user_id))
                print('Text: ', sub_event.text)
                try:
                    query = wikipedia.page(sub_event.text)
                    txt = str(wikipedia.summary(sub_event.text, sentences=5))
                    txt += "\n Подробнее: "
                    txt += query.url
                    self.vk.messages.send(user_id=event.user_id, message=txt,
                                          random_id=int(random.random() * 100000000000000000))
                    break
                except wikipedia.exceptions.PageError:
                    self.vk.messages.send(user_id=event.user_id, message="Введите адекватный запрос",
                                          random_id=int(random.random() * 100000000000000000))
                except wikipedia.exceptions.DisambiguationError:
                    self.vk.messages.send(user_id=event.user_id, message="Введите более конкретный запрос",
                                          random_id=int(random.random() * 100000000000000000))
        print("----------------------------")

    def new_message(self, event):

        if event.text.upper() == self._COMMANDS[0]:
            str = 'Привет, {0}))) Меня зовут Толя Бот.\n' \
                  'Вот список моих команд:\n' \
                  'Время\n' \
                  'Поиск\n' \
                  'Погода'.format(self.get_user_name(event.user_id))
            self.vk.messages.send(user_id=event.user_id, message=str,
                                  random_id=int(random.random() * 100000000000000000))

        elif event.text.upper() == self._COMMANDS[1]:
            str = self.get_weather(event.user_id)
            self.vk.messages.send(user_id=event.user_id, message=str,
                                  random_id=int(random.random() * 100000000000000000))

        elif event.text.upper() == self._COMMANDS[2]:
            str = self.get_time()
            self.vk.messages.send(user_id=event.user_id, message=str,
                                  random_id=int(random.random() * 100000000000000000))

        elif event.text.upper() == self._COMMANDS[3]:
            str = "Пока, {0}(((".format(self.get_user_name(event.user_id))
            self.vk.messages.send(user_id=event.user_id, message=str,
                                  random_id=int(random.random() * 100000000000000000))
        elif event.text.upper() == self._COMMANDS[4]:
            self.wiki_inf(event)
        else:
            str = "Ты втираешь мне какую-то дичь..."
            self.vk.messages.send(user_id=event.user_id, message=str,
                                  random_id=int(random.random() * 100000000000000000))

    def start_bot(self):
        print("Server started")
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    print('New message:')
                    print('For me by: ', self.get_user_name(event.user_id))
                    print('Text: ', event.text)
                    self.new_message(event)
                    print("----------------------------")
