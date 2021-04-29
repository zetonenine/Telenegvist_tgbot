from aiogram.dispatcher.filters.state import State, StatesGroup


class TestStates(StatesGroup):

    add_new_word_state = State()
    pack_showing_state = State()


if __name__ == '__main__':
    print(TestStates.all())