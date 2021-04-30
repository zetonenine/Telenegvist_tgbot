import redis
import json

r = redis.Redis()


class Redis():
    def __init__(self, host='localhost', port=6379):
        self.conn = redis.Redis(host=host, port=port)

    def queue(self, user_id, queue):
        print(queue)
        pack_name = f'{user_id}_pack'
        self.conn.delete(pack_name)

        for i in queue:
            jason = json.dumps(i)
            self.conn.rpush(pack_name, jason, jason) # добавляю дважды, потому что в основном коде пока приходится поп-ать дважды

    def stack_access(self, user_id):
        return json.loads(self.conn.lpop(f'{user_id}_pack'))


