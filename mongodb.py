import pymongo
from redis_file import Redis

r = Redis()


class Mongodb:
    def __init__(self, user="root", password="qwerty", host="localhost", port="27019"):
        self.connection = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{port}/")
        self.cursor = self.connection['test']
        self.coll_users = self.cursor['users']
        self.coll_words = self.cursor['words']

    def add_new_user(self, user_id):
        with self.connection:
            if self.coll_users.find_one({"id": user_id}) is None:
                self.coll_users.insert_one({"id": user_id,
                                            "learned": [],
                                            "in_process":
                                                [ { '1_lvl': [] },
                                                  { '2_lvl': [] },
                                                  { '3_lvl': [] },
                                                  { '4_lvl': [] },
                                                  { '5_lvl': [] }
                                                  ]
                                            })
                print('New user was added')

    def create_queue(self, user_id):
        with self.connection:
            queue = []
            words = self.coll_words.aggregate([{ "$sample": {"size": 3}}])
            for each in words:
                queue.append([each['word_id'], each['word'], each['sentence'], each['translate']])
            r.queue(user_id, queue)
            return queue

    def changing_levels(self, user_id):
        with self.connection:
            answers = r.get_answers(user_id)
            print(answers)
            for i in answers:
                if i['answer'] == True:
                    self.coll_users.insert_one({"id": user_id,
                                                "learned": [],
                                                "in_process":
                                                    [{'1_lvl': []},
                                                     {'2_lvl': []},
                                                     {'3_lvl': []},
                                                     {'4_lvl': []},
                                                     {'5_lvl': []}
                                                     ]
                                                })

            # self.coll_users.update_many({id: user_id}, {})

    def adding_word_manualy(self, msg):
        with self.connection:
            count = self.coll_words.count_documents({})
            self.coll_words.insert_one({'word_id': count+1, 'word': msg[0], 'sentence': msg[1], 'translate': msg[2], "level": msg[3]})

    def adding_words_automatically(self, data):
        with self.connection:
            if self.coll_words.find_one({"word": { "$exists": False }}) is None:
                self.coll_words.insert_one({'word_id': data[0], 'word': data[1], 'sentence': data[2], 'translate': data[3], "level": None})
                return 1
            else:
                return 0
