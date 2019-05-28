import redis
import secrets
from difflib import SequenceMatcher
import os
import re


class PaiFlow():
    def __init__(self):
        self.Redis = redis.from_url(os.environ.get('REDIS_URL'), db=0)

    def similar(self, a: str, b: str) -> float:
        '''
        Calculation of similarity measures between two strings.

        A return value of 1 matches the equal strings.
        A return value of 0 corresponds to strongly different strings.

        Arguments:
            a {str} -- String A
            b {str} -- String B

        Returns:
            [float] -- similarity
        '''
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def add(self, key: str, value: str):
        '''
        Adding {key: value} data to Redis.

        Arguments:
            key {str} -- Key
            value {str} -- Added value
        '''
        try:
            self.Redis.sadd(key, value)
        except Exception as e:
            print(e)

    def delete(self, key: str, value: str):
        '''
        Delete the value for a given key from Redis.

        Arguments:
            key {str} -- Key
            value {str} -- Value to remove
        '''
        try:
            self.Redis.srem(key, value)
        except Exception as e:
            print(e)

    def get_categories(self) -> list:
        '''
        Getting a list of all categories from Redis.

        Returns:
            [str] -- List of all categories
        '''
        try:
            return list(self.Redis.smembers('CATEGORY'))
        except Exception as e:
            print(e)

    def get_questions(self, category=None) -> list:
        '''
        Getting a list of all commands for a given category.

        Keyword Arguments:
            category {str} -- Category (default: {None})

        Returns:
            {list} -- List of all commands
        '''
        try:
            questions = self.Redis.keys('[а-я0-9]*')
            if category is None:
                return questions
            category_questions = []
            for question in questions:
                cat = list(self.Redis.smembers(question.decode()))[0].decode()
                if cat == category:
                    category_questions.append(question.decode())
            return category_questions
        except Exception as e:
            print(e)

    def get_responses(self, category: str) -> list:
        '''
        Getting a list of all bot responses for a given category.

        Arguments:
            category {str} -- Category

        Returns:
            {list}-- List of all bot responses
        '''
        try:
            responses = list(self.Redis.smembers(category))
            return [r.decode() for r in responses]
        except Exception as e:
            print(e)

    def get_category(self, sentence: str) -> str:
        '''
        Getting category by sentence.
        Searches among all commands.
        The category is selected from the most similar command.

        Arguments:
            sentence {[str]} -- Sentence

        Returns:
            [str] -- Category
        '''
        pattern = re.compile(r'[a-z0-9]+@[a-z0-9]+\.[a-z]+')
        sentence_re = re.search(pattern, sentence)

        if sentence_re:
            sentence = sentence.replace(sentence_re.group(), '')
        pattern = re.compile(r'\[[a-z0-9]+|@[a-z0-9]+\]')
        sentence_re = re.search(pattern, sentence)

        if sentence_re:
            sentence = sentence.replace(sentence_re.group(), '')
        max_sim = 0.5
        best = ''
        try:
            for key in self.Redis.keys('[а-я0-9]*'):
                s = key.decode()
                sim = self.similar(sentence, s)
                if sim > max_sim:
                    best = s
                    max_sim = sim
            resp = list(self.Redis.smembers(best))
            if resp != None and len(resp) > 0:
                print(resp, best)
                return resp[0].decode()
        except Exception as e:
            print(e)
        return 'misunderstanding'

    def get_response(self, category: str) -> str:
        '''

        Arguments:
            category {str} -- Category

        Returns:
            [str] -- Getting a random bot response.
        '''
        try:
            resp = list(self.Redis.smembers(category))
            if resp != None and len(resp) > 0:
                return secrets.choice(resp).decode()
        except Exception as e:
            print(e)
        return self.get_response('unknown')
