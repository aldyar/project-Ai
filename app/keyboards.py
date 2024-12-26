from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton

main_user = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= 'Создать новый чат')],
                                     [KeyboardButton(text = 'Профиль'),
                                     KeyboardButton(text = 'Поддержка')],
                                     [KeyboardButton(text = 'Тарифы'),
                                      KeyboardButton(text = 'Смена модели')]],
                           resize_keyboard=True,input_field_placeholder='Выберите пункт меню.')


models_user  = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= 'GPT 4o mini'),
                                     KeyboardButton(text = 'GPT 4')],
                                     [KeyboardButton(text = 'GPT 4o Omni'),
                                     KeyboardButton(text = 'DALLE'),
                                     KeyboardButton(text='GPT-o1-Preview')]
                                    ],
                           resize_keyboard=True,input_field_placeholder='Выберите пункт меню.')

chat_exit = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Выйти из чата')]
],resize_keyboard=True)

support_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Обратная связь 📩', url='https://t.me/it_razrabotka_it')]
])

tarify_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Mini', url='https://t.me/it_razrabotka_it')],
    [InlineKeyboardButton(text='Start', url='https://t.me/it_razrabotka_it')],
    [InlineKeyboardButton(text='Premium', url='https://t.me/it_razrabotka_it')],
])

check_channels  = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Проверить')]
],resize_keyboard=True)