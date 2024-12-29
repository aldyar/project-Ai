from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.request import (get_gpt_model,change_gpt4, get_today_users_count,
                                  get_total_users_count,get_all_channels,add_channel,
                                  delete_channel,get_user_plan_name,add_advertise,
                                  delete_advertise,get_all_advertises)
from app.state import Chat, Image, Admins
from app.generators import gpt_text, gpt_image,get_balance
from aiogram.enums import ChatAction
import app.text as txt


admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [1075213318]
    

@admin.message(Admin(), CommandStart())
async def start_admin(message: Message,state: FSMContext):
    await state.clear()
    await message.answer('Hello ADMIN',reply_markup=kb.main_admin)
    

@admin.message(Admin(),F.text=='Создать новый чат')
async def chatting(message: Message, state: FSMContext):
    model = await get_gpt_model(message.from_user.id)
    if model == 'dall-e-3':
        await state.set_state(Image.text)
        await message.answer('Введите ваш запрос картинки',reply_markup=kb.chat_exit)
    else:
        await state.set_state(Chat.text)
        await message.answer('Введите ваш запрос',reply_markup=kb.chat_exit)
    await message.answer('rabotaet')


@admin.message(Admin(),Image.wait)
async def wait_wait(message:Message):
    await message.answer('Ваша картинка генеируется, подождите...')


@admin.message(Admin(),Chat.wait)
async def wait_wait(message:Message):
    await message.answer('Ваше сообщение генеируется, подождите...')


@admin.message(Admin(),Image.text)
async def chat_response(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_PHOTO)
    await state.set_state(Image.wait)
    model = await get_gpt_model(message.from_user.id)
    response = await gpt_image(message.text, model)
    print(response)
    try:
        await message.answer_photo(photo=response['response'])
    except Exception as e:
        print(e)
        await message.answer(response['response'])
    await state.set_state(Image.text)


@admin.message(Admin(),Chat.text)
async def generate_text(message: Message, state: FSMContext):
    model = await get_gpt_model(message.from_user.id)
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await state.set_state(Chat.wait)
    response = await gpt_text(message.text, model)
    await message.answer(response, parse_mode='Markdown')
    await state.set_state(Chat.text)
    

@admin.message(Admin(),F.text=='Смена модели')
async def models(message: Message):
    await message.answer('Выберите модель..', reply_markup=kb.models_user)


@admin.message(Admin(),F.text == 'GPT 4o mini')
async def change_gpt_4(message: Message):
    model = 'gpt-4o-mini'
    await change_gpt4(message.from_user.id, model)
    await message.answer('Ваша модель изменена...', reply_markup=kb.main_admin)


@admin.message(Admin(),F.text=='GPT 4')
async def change_gpt_4(message:Message):
    model = 'gpt-4'
    await change_gpt4(message.from_user.id,model)
    await message.answer('Ваша модель изменена...',reply_markup=kb.main_admin)


@admin.message(Admin(),F.text=='GPT 4o Omni')
async def change_gpt_4(message:Message):
    model = 'gpt-4o'
    await change_gpt4(message.from_user.id, model)
    await message.answer('Ваша модель изменена...',reply_markup=kb.main_admin)


@admin.message(Admin(),F.text=='DALLE')
async def change_gpt_4(message:Message):
    model = 'dall-e-3'
    await change_gpt4(message.from_user.id,model)
    await message.answer('Ваша модель изменена...',reply_markup=kb.main_admin)


@admin.message(Admin(),F.text=='GPT-o1-Preview')
async def change_gpt_4(message:Message):
    model = 'o1-mini'
    await change_gpt4(message.from_user.id, model)
    await message.answer('Ваша модель изменена...',reply_markup=kb.main_admin)

@admin.message(Admin(),F.text=='Назад')
@admin.message(Admin(),F.text=='Админ панель')
async def admin_menu(message: Message,state:FSMContext):
    await state.clear()
    balance = await get_balance()
    new_users = await get_today_users_count()
    total_users = await get_total_users_count()
    await message.answer(txt.stats_text(balance,new_users,total_users),parse_mode="Markdown",reply_markup=kb.refresh_inline)
    await message.answer("Выберите действие из меню ниже ⬇️",reply_markup=kb.admin_menu)


@admin.message(Admin(),F.text=='Вернуться в главное меню')
async def back_to_menu(message: Message):
    await message.answer('Hello ADMIN', reply_markup=kb.main_admin)


@admin.callback_query(Admin(), F.data=='refresh')
async def refresh_stats(callback: CallbackQuery):
    balance = await get_balance()
    new_users = await get_today_users_count()
    total_users = await get_total_users_count()
    if callback.message:
        await callback.message.delete()
    await callback.message.answer(txt.stats_text(balance,new_users,total_users),parse_mode="Markdown",reply_markup=kb.refresh_inline)
    await callback.answer()


@admin.message(Admin(), F.text=='Управление каналами')
async def setting_channel(message: Message):
    channels = await get_all_channels()
    if channels:
        channel_list = '\n'.join([f"`{channel.channel_name}`" for channel in channels])
        await message.answer(f"Список всех каналов:\n{channel_list}", parse_mode="Markdown",reply_markup=kb.setting_channels)
    else:
        await message.answer("Нет доступных каналов.", parse_mode="Markdown")


@admin.message(Admin(), F.text=='Добавить канал')
async def add_channel_button(message: Message,state: FSMContext):
     await message.answer("Введите имя канала, начиная с @. Пример: @example_channel")
     await state.set_state(Admins.add_channel)


@admin.message(Admin(),Admins.add_channel)
async def wait_add(message:Message, state: FSMContext):
    channel_name = message.text.strip()
    if not channel_name.startswith('@'):
        await message.answer("Имя канала должно начинаться с '@'. Попробуйте снова.")
        return
    try:
        await add_channel(channel_name)
        await message.answer(f"Канал {channel_name} успешно добавлен.")
    except ValueError as e:
        await message.answer(str(e))
    await state.clear()


@admin.message(Admin(),F.text=='Удалить канал')
async def delete_channel_button(message: Message,state:FSMContext):
    await message.answer("Введите имя канала, начиная с @. Пример: @example_channel")
    await state.set_state(Admins.delete_channel)


@admin.message(Admin(),Admins.delete_channel)
async def wait_delete(message:Message, state: FSMContext):
    channel_name = message.text.strip()
    if not channel_name.startswith('@'):
        await message.answer("Имя канала должно начинаться с '@'. Попробуйте снова.")
        return
    try:
        await delete_channel(channel_name)  # Функция для удаления канала из базы данных
        await message.answer(f"Канал {channel_name} успешно удален.")
    except ValueError as e:
        await message.answer(str(e))
    await state.clear()


@admin.message(Admin(),F.text=='Управление рекламными блоками')
async def adver_setting(message:Message):
    await message.answer('Выберите задачу', reply_markup=kb.advert_setting)


@admin.message(Admin(),F.text=='Добавить блок')
async def add_advert(message: Message, state: FSMContext):
    await message.answer('Введите текст который хотите добавить⏳')
    await state.set_state(Admins.wait_text)


@admin.message(Admin(),Admins.wait_text)
async def process_advert_text(message: Message, state: FSMContext):
    text = message.text
    try:
        await add_advertise(text=text)
        await message.answer("Текст успешно добавлен в базу данных ✅")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении текста: {e} ❌")
    await state.clear()


@admin.message(Admin(),F.text=='Удалить блок')
async def delete_advert(message:Message, state: FSMContext):
    adverts = await get_all_advertises()
    if not adverts:
        await message.answer("Нет доступных рекламных блоков для удаления ❌")
        return
    advert_list = "\n".join([f"ID: `{advert.id}` — {advert.text}" for advert in adverts])
    await message.answer(f"Отправьте ID рекламного блока, который хотите удалить:\n\n{advert_list}",parse_mode='Markdown')
    await state.set_state(Admins.wait_advert_id)


@admin.message(Admin(), Admins.wait_advert_id)
async def process_advert_deletion(message: Message, state: FSMContext): 
    advert_id = message.text.strip()
    if not advert_id.isdigit():
        await message.answer("Пожалуйста, введите корректный числовой ID ❌")
        return
    success = await delete_advertise(advert_id=int(advert_id))
    if success:
        await message.answer("Рекламный блок успешно удален ✅")
    else:
        await message.answer("Рекламный блок с таким ID не найден ❌")
    await state.clear()


@admin.message(Admin(),F.text=='Управление пользователями')
async def setting_users(message:Message,state: FSMContext):
    await message.answer('Введите id пользователя в формате: `11111111`',parse_mode='Markdown')
    await state.set_state(Admins.wait_id)


@admin.message(Admin(),Admins.wait_id)
async def change_plan(message: Message, state: FSMContext):
    user_id = message.text.strip()
    user_plan = await get_user_plan_name(user_id)
    await message.answer('')
