import redis
import json

r = redis.Redis()


class Redis:
    def __init__(self, host='localhost', port=6379):
        self.conn = redis.Redis(host=host, port=port)

    def queue(self, user_id, queue):
        print(queue)
        pack_name = f'{user_id}_pack'
        self.conn.delete(pack_name)

        for i in queue:
            jason = json.dumps(i)
            self.conn.rpush(pack_name, jason)
            self.conn.rpush(pack_name, jason) # добавляю дважды, потому что в основном коде пока приходится поп-ать дважды

        print(self.conn.lrange(pack_name, 0, -1))

    def stack_access(self, user_id):
        try:
            return json.loads(self.conn.lpop(f'{user_id}_pack'))
        except:
            return None

    def check_queue(self, user_id):
        # print((self.conn.lrange(f'{user_id}_pack', 0, -1)))
        pass

    def re_add_word(self, user_id, que):
        jason = json.dumps(que)
        self.conn.rpush(f'{user_id}_pack', jason)
        self.conn.rpush(f'{user_id}_pack', jason)

    def add_answer(self, user_id, answer):
        answers_name = f'{user_id}_answers'
        jason = json.dumps(answer)
        self.conn.rpush(answers_name, jason)

    def get_answers(self, user_id):
        answers_name = f'{user_id}_answers'
        answers = []
        data = self.conn.lrange(answers_name, 0, -1)
        for each in data:
            answers.append(json.loads(each))
        r.delete(f'{user_id}_answers')
        return answers



