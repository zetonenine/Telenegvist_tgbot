import pymongo
from redis_file import Redis

r = Redis()

class Mongodb:
    def __init__(self, user="root", password="qwerty", host="localhost", port="27019"):
        self.connection = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{port}/")

        self.cursor = self.connection['test']
        self.coll_users = self.cursor['users']
        self.coll_words = self.cursor['words']

    def add_new_word(self, msg):
        with self.connection:
            count = self.coll_words.count_documents({})
            self.coll_words.insert_one({'word_id': count+1, 'word': msg[0], 'sentence': msg[1], 'translate': msg[2], "level": msg[3]})

    def create_queue(self, user_id):
        with self.connection:
            queue = []
            for every in range(1, 6):
                queue.append([self.coll_words.find()[every]['word_id'], self.coll_words.find()[every]['word'], self.coll_words.find()[every]['sentence'], self.coll_words.find()[every]['translate']])
            r.queue(user_id, queue)
            return queue
