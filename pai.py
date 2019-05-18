import redis
import secrets
from difflib import SequenceMatcher
import os


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

#  Categories
#  1 --- hello
#  2 --- what I can
#  3 --- add
#  4 --- dont know
#  5 --- services
#
#


class PaiFlow():
    def __init__(self):
        self.Redis = redis.from_url(os.environ.get("REDIS_URL"), db=0)
        

    def build(self):
        self.build_cat1()
        self.build_cat2()
        self.build_cat3()
        self.build_cat4()
        self.build_cat5()
        self.build_cat6()
        self.build_cat7()
        self.build_cat8()
        self.build_cat9()
        self.build_cat10()
        self.build_cat11()

    def build_cat1(self):
        self.Redis.sadd("привет", 'hello')
        self.Redis.sadd("зравствуй", 'hello')
        self.Redis.sadd("добрый день", 'hello')
        self.Redis.sadd("добрый вечер", 'hello')
        self.Redis.sadd("здравствуйте", 'hello')
        self.Redis.sadd("старт", 'hello')
        self.Redis.sadd('hello', "Привет ")
        self.Redis.sadd('hello', "Зравствуй ")
        self.Redis.sadd('hello', "Добрый день ")
        self.Redis.sadd('hello', "Добрый вечер ")
        self.Redis.sadd('hello', "Здравствуйте ")

    def build_cat2(self):
        self.Redis.sadd("misunderstanding", "Извините, но я Вас не понимаю ")
        self.Redis.sadd("misunderstanding", "Пожалуйста, напишите что Вы хотите ")
        self.Redis.sadd("misunderstanding", "Пожалуйста, напишите что Вам нужно ")

    def build_cat3(self):
        self.Redis.sadd("что ты можешь", 'affairs')
        self.Redis.sadd("что ты умеешь", 'affairs')

        self.Redis.sadd(
            'affairs', "Я могу отправлять Вам уведомления о новый письмах на электронной почте. ")
        self.Redis.sadd(
            'affairs', "Вы будете получать сообщение с уведомлением о новом письме. ")

    def build_cat4(self):
        self.Redis.sadd('unknown' , "Я не знаю такой сервис. ")
        self.Redis.sadd('unknown' , "Попробуйте другой почтовый сервис. ")
        self.Redis.sadd('unknown' , "К сожалению я не работаю с этим сервисом. ")

    def build_cat5(self):
        self.Redis.sadd('can', "\n Я могу работать с почтовыми сервисами \n\t 1) yandex.ru \n\t 2) mail.ru \n\t 3) gmail.com \n")

    def build_cat6(self):
        self.Redis.sadd("помощь", 'help')
        self.Redis.sadd("помоги", 'help')
        self.Redis.sadd("спаси", 'help')
        self.Redis.sadd("выручай", 'help')

    def build_cat7(self):
        self.Redis.sadd("Авторизация", 'auth')
        self.Redis.sadd("Войти", 'auth')
        self.Redis.sadd("Начать", 'auth')
        self.Redis.sadd("Получать", 'auth')

        self.Redis.sadd(
            'auth', "\n Для авторизации напишите комманду: \n <<Авторизация + Ваш e-mail>. ")

    def build_cat8(self):
        self.Redis.sadd("link", "Держите ссылку для авторизации. ")
        self.Redis.sadd("link", "Перейдите по ссылке для авторизации. ")

    def build_cat9(self):
        self.Redis.sadd("thanks", "Спасибо. ")
        self.Redis.sadd("thanks", "Благодарю. ")
        self.Redis.sadd("thanks", "Авторизация успешна. ")

    def build_cat10(self):
        self.Redis.sadd("error", "Что-то пошло не так. ")

    def build_cat11(self):
        self.Redis.sadd("Кто ты", "name")
        self.Redis.sadd("Вы кто", "name")
        self.Redis.sadd("Как тебя зовут", "name")
        self.Redis.sadd("Твое имя", "name")

        self.Redis.sadd("name", "Меня зовут ")
        self.Redis.sadd("name", "Я чат-бот ")
        self.Redis.sadd("name", "Я ваш помошник ")

    def get_category(self, word):
        max_sim = 0.5
        best = ""
        for key in self.Redis.keys():
            s = key.decode()
            sim = similar(word, s)
            if sim > max_sim:
                best = s
                max_sim = sim

        resp = list(self.Redis.smembers(best))
        if resp != None:
            return resp[0].decode()
        return '2'

    def get_response(self, category):
        resp = list(self.Redis.smembers(category))
        if resp != None:
            return secrets.choice(resp).decode()

    def help(self):
        helpstr = "Я понимаю следующие команды:"
        i = 0
        for key in self.Redis.keys():
            helpstr = helpstr+"\n"+str(i)+")"+key.decode()
            i = i+1
        return helpstr
