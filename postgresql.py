import psycopg2

class Pstrgsqler:

    def __init__(self, user="postgres", password="postgres", dbname="postgres", host="localhost"):
        self.connection = psycopg2.connect(
            user=user,
            password=password,
            dbname=dbname,
            host=host)
        self.cursor = self.connection.cursor()

    def create_users_tab(self):
        command = (
            """
            CREATE TABLE IF NOT EXISTS users_list (
            id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            user_id INTEGER,
            vocab INTEGER,
            eng_level INTEGER DEFAULT 0 
            )
            """
        )

        with self.connection:
            return self.cursor.execute(command)

    def create_words_tab(self):
        command = (
            """
            CREATE TABLE IF NOT EXISTS words (
            id INTEGER NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            word TEXT NOT NULL,
            sentence TEXT NOT NULL,
            level INTEGER NOT NULL
            )
            """
        )

        with self.connection:
            return self.cursor.execute(command)

    def create_unique_user_tab(self, userID):
        command = (
            f"""
            CREATE TABLE IF NOT EXISTS table_{userID} (
            stage1 INTEGER,
            stage2 INTEGER,
            stage3 INTEGER,
            stage4 INTEGER,
            stage5 INTEGER,
            completed INTEGER
            )
            """
        )

        with self.connection:
            return self.cursor.execute(command)

    def add_user(self, userID):
        with self.connection:
            return self.cursor.execute("INSERT INTO users_list (user_id) VALUES (%s)", (userID,))

    def count_words(self, userID, stage):
        with self.connection:
            return self.cursor.execute(f"SELECT COUNT(*) FROM '{userID}'-table WHERE (%s)",(stage))

    def pack_process(self, userID):
        with self.connection:
            if Pstrgsqler.count_words(userID, 'stage5') >= 12:
                Pstrgsqler.five_stage(userID)
                #запустить 5 уровень

            if Pstrgsqler.count_words(userID, 'stage4') >= 14:
                Pstrgsqler.four_stage(userID)
                #запустить 4 уровень

            if Pstrgsqler.count_words(userID, 'stage3') >= 16:
                Pstrgsqler.three_stage(userID)



                #запустить 3 уровень
                pass
            # запустить 2 уровень
            # запустить 1 уровень

        pass

    def five_stage(self, userID):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM {userID}-table WHERE stage5 LIMIT 6")

    def four_stage(self, userID):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM {userID}-table WHERE stage4 LIMIT 11")

    def three_stage(self, userID):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM {userID}-table WHERE stage3")

    def two_stage(self, userID):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM {userID}-table WHERE stage2")

    def one_stage(self, userID):
        with self.connection:
            self.cursor.execute("SELECT RANDOM !!!!!!?????? FROM words")


    def request_new_word(self, userID):
        pass

    def move_word_throw_levels(self, userID):
        pass

    def show_random_word(self, userID):
        pass

    def adding_new_word(self, values):
        with self.connection:
            self.cursor.execute("INSERT INTO words (word, sentence, level) VALUES (%s, %s, %s)", (values[0], values[1], values[2]))

    def check(self):
        with self.connection:
            self.cursor.execute("SELECT word FROM words LIMIT 2")
            obj = self.cursor.fetchall()
            print(obj[0])
            return obj

    def take_words(self):
        with self.connection:
            self.cursor.execute(f"SELECT word, sentence FROM words ORDER BY random() LIMIT 1")
            ans = self.cursor.fetchall()
            return ans








# def loop(user, count):
#     stage5(user)
#
# def stage5(user):
#     if Pstrgsqler.count_words(user, 'stage5') >= 12:
#         return Pstrgsqler.five_stage(user)
#
# def stage4():
#     pass
#
# def stage3():
#     pass
# def stage2():
#     pass




# async def func(message: types.Message, count):
#
#     if Pstrgsqler.count_words(message.from_user.id, 'stage5') >= 12:
#         Pstrgsqler.five_stage(message.from_user.id)
#
#     if Pstrgsqler.count_words(message.from_user.id, 'stage4') >= 14:
#         Pstrgsqler.four_stage(message.from_user.id)
#
#     if Pstrgsqler.count_words(message.from_user.id, 'stage3') >= 16:
#         Pstrgsqler.three_stage(message.from_user.id)
