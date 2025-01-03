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
    [InlineKeyboardButton(text='Mini', callback_data='buy_mini')],
    [InlineKeyboardButton(text='Start', callback_data='buy_start')],
    [InlineKeyboardButton(text='Premium', callback_data='buy_premium')],
])

check_channels  = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Проверить')]
],resize_keyboard=True)

tarif_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ВЫБРАТЬ ТАРИФ', callback_data='tarif')]
])

main_admin = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= 'Создать новый чат')],
                                     [KeyboardButton(text = 'Профиль'),
                                     KeyboardButton(text = 'Поддержка')],
                                     [KeyboardButton(text = 'Тарифы'),
                                      KeyboardButton(text = 'Смена модели')],
                                      [KeyboardButton(text = 'Админ панель')]],
                           resize_keyboard=True,input_field_placeholder='Выберите пункт меню.')


admin_menu = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text = 'Вернуться в главное меню')],
                                     [KeyboardButton(text= 'Управление пользователями'),
                                     KeyboardButton(text = 'Управление каналами')],
                                     [KeyboardButton(text = 'Управление рекламными блоками')]],
                           resize_keyboard=True,input_field_placeholder='Выберите пункт меню.')

refresh_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ОБНОВИТЬ', callback_data='refresh')]
])

setting_channels = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= 'Добавить канал'),
                                     KeyboardButton(text = 'Удалить канал')],
                                     [KeyboardButton(text='Назад')]],
                           resize_keyboard=True,input_field_placeholder='Выберите пункт меню.')


setting_user_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Free', callback_data='refresh')],
    [InlineKeyboardButton(text='Mini', callback_data='refresh')],
    [InlineKeyboardButton(text='Start', callback_data='refresh')],
    [InlineKeyboardButton(text='Premium', callback_data='refresh')],
])

def inline_keyboard(channels):
    inline_keyboard = [
        [InlineKeyboardButton(text=f"Подписаться #{idx}", url=f"https://t.me/{channel.channel_name[1:]}")]
        for idx, channel in enumerate(channels, start=1)
    ]
    inline_keyboard.append([InlineKeyboardButton(text="ВЫБРАТЬ ТАРИФ", callback_data="tarif")])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

back = ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text= 'Главное меню')]],
                           resize_keyboard=True)

off_advert = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отключить рекламу', callback_data='tarif')]
])


advert_setting = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Добавить блок'),
     KeyboardButton(text='Удалить блок')],
     [KeyboardButton(text = 'Назад')]
],resize_keyboard=True)

inline_admin_user = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить тариф', callback_data='add_tarif')],
    [InlineKeyboardButton(text='Удалить тариф',callback_data='delete_tarif')]
])

inline_admin_user_add = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Mini', callback_data='tarif')],
    [InlineKeyboardButton(text='Start',callback_data='tarif')],
    [InlineKeyboardButton(text='Premium')]
])

inline_admin_user_delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Mini', callback_data='delete_mini')],
    [InlineKeyboardButton(text='Start',callback_data='tarif')],
    [InlineKeyboardButton(text='Premium',callback_data='tarif')]
])