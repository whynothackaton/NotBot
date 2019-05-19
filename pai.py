import redis
import secrets
from difflib import SequenceMatcher
import os


def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

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
        self.Redis = redis.from_url(os.environ.get('REDIS_URL'), db=0)

    def add(self, T1, T2):
        '''[summary]

        Arguments:
            T1 {str} -- key
            T2 {str} -- value
        '''
        self.Redis.sadd(T1, T2)

    def get_categories(self):
        return self.Redis.keys('[a-z]*[^@]')

    def get_questions(self, category=None):
        questions = self.Redis.keys('[а-я0-9]*')
        if category is None:
            return questions
        category_questions = []
        for question in questions:
            cat = list(self.Redis.smembers(question.decode()))[0].decode()
            if cat == category:
                category_questions.append(question.decode())
        return category_questions

    def delete(self, key, value):
        self.Redis.srem(key, value)

    def get_responses(self, category):
        responses = list(self.Redis.smembers(category))
        return [r.decode() for r in responses]

    def get_category(self, word):
        max_sim = 0.5
        best = ''
        for key in self.Redis.keys('[а-я0-9]*'):
            s = key.decode()
            sim = similar(word, s)
            if sim > max_sim:
                best = s
                max_sim = sim
        resp = list(self.Redis.smembers(best))[0]
        if resp != None:
            print(resp, best)
            return resp.decode()
        return '2'

    def get_response(self, category):
        resp = list(self.Redis.smembers(category))
        if resp != None:
            return secrets.choice(resp).decode()

    def help(self):
        helpstr = 'Я понимаю следующие команды:'
        i = 0
        for key in self.Redis.keys():
            helpstr = helpstr+'\n'+str(i)+')'+key.decode()
            i = i+1
        return helpstr
