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
                                                [{'1_lvl': []},
                                                 {'2_lvl': []},
                                                 {'3_lvl': []},
                                                 {'4_lvl': []},
                                                 {'5_lvl': []}
                                                 ]
                                            })
                print('New user was added')

    def create_queue(self, user_id):
        with self.connection:
            queue = []
            available_words = []
            ALL_AMOUNT_OF_WORD = 1
            start_level = 0

            in_process = Mongodb.get_data_in_proceess(self, user_id)[1]

            for each_lvl in reversed(in_process):
                for key, value in each_lvl.items():
                    for word_id in value:
                        available_words.append([int(key[0]), word_id])

            for i, j in available_words:
                data = Mongodb.get_word_data_by_id(self, j)
                queue.append([data['word_id'], data['word'], data['sentence'], data['translate'], i, True])
                # в конце 0 нужно, чтобы пометить что слово взято из тех, что юзер уже изучал - из in_process

            AMOUNT_OF_NEW_WORDS = ALL_AMOUNT_OF_WORD - len(available_words)
            words = self.coll_words.aggregate([{"$sample": {"size": AMOUNT_OF_NEW_WORDS}}])
            for each in words:
                queue.append([each['word_id'], each['word'], each['sentence'], each['translate'], start_level])
            r.queue(user_id, queue)

            print(queue)
            return queue

    def changing_levels(self, user_id):
        with self.connection:
            answers = r.get_answers(user_id)
            print(answers)

            learned, in_process = Mongodb.get_data_in_proceess(self, user_id)
            for each in answers:
                if each['lvl'] == 6:
                    learned.append(each['word_id'])
                else:
                    in_process[each['lvl']-1][f"{each['lvl']}_lvl"].append(each['word_id'])

            self.coll_users.update_one({"id": user_id},
                                       {'$set':
                                            {"learned": learned,
                                             "in_process": in_process
                                             }
                                        }
                                       )

    def adding_word_manually(self, msg):
        with self.connection:
            count = self.coll_words.count_documents({})
            self.coll_words.insert_one(
                {'word_id': count + 1, 'word': msg[0], 'sentence': msg[1], 'translate': msg[2], "level": msg[3]})

    def adding_words_automatically(self, data):
        with self.connection:
            if self.coll_words.find_one({"word": {"$exists": False}}) is None:
                self.coll_words.insert_one(
                    {'word_id': data[0], 'word': data[1], 'sentence': data[2], 'translate': data[3], "level": None})
                return 1
            else:
                return 0

    def get_data_in_proceess(self, user_id):
        with self.connection:
            data = self.coll_users.find_one({"id": user_id})

            print(text)
            return data['learned'], data['in_process']

    def get_word_data_by_id(self, word_id):
        with self.connection:
            data = self.coll_words.find_one({'word_id': word_id})
            return data
