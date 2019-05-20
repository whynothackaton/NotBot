import redis
import secrets
from difflib import SequenceMatcher
import os


class PaiFlow():
    def __init__(self):
        self.Redis = redis.from_url(os.environ.get('REDIS_URL'), db=0)

    def similar(a, b):
        '''[summary]
        
        Arguments:
            a {[type]} -- [description]
            b {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        '''
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def add(self, T1, T2):
        '''[summary]

        Arguments:
            T1 {str} -- key
            T2 {str} -- value
        '''
        self.Redis.sadd(T1, T2)

    def get_categories(self):
        '''[summary]

        Returns:
            [str] -- [description]
        '''
        categories = list(self.Redis.smembers('CATEGORY'))
        return categories

    def get_questions(self, category=None):
        '''[summary]

        Keyword Arguments:
            category {[str]} -- [description] (default: {None})

        Returns:
            [str] -- [description]
        '''
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
        '''[summary]

        Arguments:
            key {[str]} -- [description]
            value {[str]} -- [description]
        '''
        self.Redis.srem(key, value)

    def get_responses(self, category):
        '''[summary]

        Arguments:
            category {[str]} -- [description]

        Returns:
            [list] -- [description]
        '''
        responses = list(self.Redis.smembers(category))
        return [r.decode() for r in responses]

    def get_category(self, word):
        '''[summary]

        Arguments:
            word {[str]} -- [description]

        Returns:
            [str] -- [description]
        '''
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
        return 'misunderstanding'

    def get_response(self, category):
        '''[summary]

        Arguments:
            category {[str]} -- [description]

        Returns:
            [str] -- [description]
        '''
        resp = list(self.Redis.smembers(category))
        if resp != None:
            return secrets.choice(resp).decode()
