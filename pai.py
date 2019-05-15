import redis
import secrets
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
        self.RedisPh = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
        self.RedisRes = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)

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

    def build_cat1(self):
        self.RedisPh.set("привет", 1)
        self.RedisPh.set("зравствуй", 1)
        self.RedisPh.set("добрый день", 1)
        self.RedisPh.set("добрый вечер", 1)
        self.RedisPh.set("здравствуйте", 1)
        self.RedisPh.set("старт", 1)
        self.RedisRes.sadd(1, "Привет ")
        self.RedisRes.sadd(1, "Зравствуй ")
        self.RedisRes.sadd(1, "Добрый день ")
        self.RedisRes.sadd(1, "Добрый вечер ")
        self.RedisRes.sadd(1, "Здравствуйте ")

    def build_cat2(self):
        self.RedisRes.sadd(2, "Я не знаю что Вы хотите.")

    def build_cat3(self):
        self.RedisPh.set("что ты можешь", 3)
        self.RedisPh.set("что ты можешь", 3)

        self.RedisRes.sadd(3, "Я могу отправлять Вам уведомления о новый письмах на электронной почте. ")
        self.RedisRes.sadd(3, "Вы будете получать сообщение с уведомлением о новом письме. ")

    def build_cat4(self):
        self.RedisRes.sadd(4, "Я не знаю такой сервис. ")
        self.RedisRes.sadd(4, "Попробуйте другой почтовый сервис. ")
        self.RedisRes.sadd(4, "К сожалению я не работаю с этим сервисом. ")

    def build_cat5(self):
        self.RedisRes.sadd(5, "\n Я могу работать с почтовыми сервисами \n\t 1) yandex.ru \n\t 2) mail.ru \n\t 3) gmail.com \n")
        
    def build_cat6(self):
        self.RedisPh.set("помощь", 6)
        self.RedisPh.set("помоги", 6)
        self.RedisPh.set("спаси", 6)
        self.RedisPh.set("выручай", 6)

    def build_cat7(self):
        self.RedisRes.sadd(7, "\n Для авторизации напишите комманду: \n <<Авторизация + Ваш e-mail>. ")

    def build_cat8(self):
        self.RedisRes.sadd(8, "Держите ссылку для авторизации. ")
        self.RedisRes.sadd(8, "Перейдите по ссылке для авторизации. ")

    def build_cat9(self):
        self.RedisRes.sadd(9, "Спасибо. ")
        self.RedisRes.sadd(9, "Благодарю. ")
        self.RedisRes.sadd(9, "Авторизация успешна. ")
    
    def build_cat10(self):
        self.RedisRes.sadd(10, "Что-то пошло не так. ")
        

    

    def get_category(self, word):
        resp = self.RedisPh.get(word)
        if resp != None:
            return resp.decode()
        return '2'
        

    def get_response(self, category):
        resp = list(self.RedisRes.smembers(category))
        if resp !=  None:
            return secrets.choice(resp).decode()

    def help(self):
        helpstr="Я понимаю следующие команды:"
        i=0
        for key in self.RedisPh.keys():
            helpstr=helpstr+"\n"+str(i)+")"+key.decode()
            i=i+1
        return helpstr
