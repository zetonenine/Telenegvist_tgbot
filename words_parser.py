import requests
import re
from mongodb import Mongodb
import random

mng = Mongodb()

baseURL = 'https://dictionary.skyeng.ru/api/public/v1/'
word_endpoint = f"{baseURL}meanings?ids="


def parse_random_word(num):
    api_data = requests.get(f"{word_endpoint}{num}")

    word = api_data.json()[0]['text']
    translate = api_data.json()[0]['translation']['text']
    example = api_data.json()[0]['examples'][0]['text']

    ex = re.split('[ ]', example)

    for index, mean in enumerate(ex):
        if '[' in mean or ']' in mean:
            unknown = ''
            for j in range(0, len(mean)-2):
                unknown += '_'
            ex[index] = unknown

    example = ' '.join(ex)

    return [num, word, example, translate]


def adding_db(num):
    data = parse_random_word(num)
    return mng.adding_words_automatically(data)


def main(amount):
    count_exists = 0
    count = 0
    amount_before = amount
    while amount != 0:
        try:
            rand_id = random.randint(1, 120000)
            obj = adding_db(rand_id)

            if obj == 1:
                amount -= 1
                count += 1

            else:
                count_exists += 1
                count += 1

        except:
            count += 1
        print('.')

    print(f'Просканировано: {count} слов\nДобавлено: {amount_before}\nНедобавлено, потому что уже существует: {count_exists}')


main(int(input('Write an amount of words you need to parse..\n')))

