from aiogram.fsm.state import StatesGroup, State


class Chat(StatesGroup):
    text = State()
    wait = State()

class Image(StatesGroup):
    text = State()
    wait = State()

class Admins(StatesGroup):
    add_channel = State()
    delete_channel = State()
    wait_id = State()
    wait_text = State()
    wait_advert_id = State()