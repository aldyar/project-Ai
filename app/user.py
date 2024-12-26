from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from app.text import hello_text,support_text,tarif_text
from app.database.request import (set_user, get_gpt_model, get_user_plan_name, 
                                  change_gpt4, check_gpt_limit, check_unlimit_gpt, 
                                  decrement_gpt_limit, check_subscription,check_user_subscription)
from app.generators import gpt_text, gpt_image
from app.state import Chat, Image
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from aiogram import Bot


user = Router()


@user.message(F.text=='Выйти из чата')
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await set_user(message.from_user.id)
    await message.answer(hello_text, reply_markup= kb.main_user)
    

@user.message(F.text=='Создать новый чат')
async def chatting(message: Message, state: FSMContext, bot: Bot):
    model = await get_gpt_model(message.from_user.id)
    limit = await check_gpt_limit(message.from_user.id,model)
    plan = await get_user_plan_name(message.from_user.id)
    podpiski = await check_user_subscription(bot, message.from_user.id)
    if limit == 0 and plan == 'free' and podpiski == False:
        await message.answer('Вы не подписаны',reply_markup=kb.check_channels)
    else:
        if model == 'dall-e-3':
            await state.set_state(Image.text)
            await message.answer('Введите ваш запрос картинки',reply_markup=kb.chat_exit)
        else:
            await state.set_state(Chat.text)
            await message.answer('Введите ваш запрос',reply_markup=kb.chat_exit)


@user.message(Image.text)
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
 

@user.message(Chat.text)
async def generate_text(message: Message, state: FSMContext):
    model = await get_gpt_model(message.from_user.id)
    subscription = await get_user_plan_name(message.from_user.id)
    if subscription == "premium" and model == "gpt-4o-mini":
        await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
        await state.set_state(Chat.wait)
        response = await gpt_text(message.text, model)
        await message.answer(response, parse_mode='Markdown')
        await state.set_state(Chat.text)
    else:
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit > 0: 
            await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
            await state.set_state(Chat.wait)
            response = await gpt_text(message.text, model)
            await decrement_gpt_limit(message.from_user.id, model)
            await message.answer(response, parse_mode='Markdown')
            await state.set_state(Chat.text)
        else:
            await message.answer('У вас закончился лимит..', reply_markup=kb.main_user)
            await state.clear()


@user.message(Image.wait)
async def wait_wait(message:Message):
    await message.answer('Ваша картинка генеируется, подождите...')


@user.message(Chat.wait)
async def wait_wait(message:Message):
    await message.answer('Ваше сообщение генеируется, подождите...')


@user.message(F.text=='Смена модели')
async def models(message: Message):
    await message.answer('Выберите модель..', reply_markup=kb.models_user)


@user.message(F.text=='Поддержка')
async def support(message:Message):
    await message.answer(support_text, reply_markup=kb.support_inline)


@user.message(F.text =='Тарифы')
async def tarif(message: Message):
    await message.answer(tarif_text,reply_markup=kb.tarify_inline)


@user.message(F.text == 'Профиль')
async def user_profile(message: Message):
    user_id = message.from_user.id
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name:
        response_text = (
            f"Ваш профиль:\n"
            f"• **Ваш ID**: `{user_id}`\n"
            f"• **Ваш тарифный план**: `{plan_name.capitalize()}`\n"
        )
    else:
        response_text = (
            f"Ваш профиль:\n"
            f"— Ваш ID: {user_id}\n"
            f"— Тарифный план не найден. Пожалуйста, зарегистрируйтесь или обратитесь в поддержку."
        )
    await message.answer(response_text,parse_mode='Markdown')


@user.message(F.text == 'GPT 4o mini')
async def change_gpt_4(message: Message):
    model = 'gpt-4o-mini'
    subscription = await get_user_plan_name(message.from_user.id)
    if subscription == "premium":
        await change_gpt4(message.from_user.id, model)
        await message.answer('Ваша модель изменена...', reply_markup=kb.main_user)
    else:
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit > 0: 
            await change_gpt4(message.from_user.id, model)
            await message.answer('Ваша модель изменена...', reply_markup=kb.main_user)
        else:
            await message.answer('У вас превышен лимит.')


@user.message(F.text=='GPT 4')
async def change_gpt_4(message:Message):
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name in ['mini', 'start', 'premium']:
        model = 'gpt-4'
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit>0:
            await change_gpt4(message.from_user.id,model)
            await message.answer('Ваша модель изменена...',reply_markup=kb.main_user)
        else:
            await message.answer('У вас превышен лимит.')
    else:
        await message.answer('У вас нет доступа к этой модели')


@user.message(F.text=='GPT 4o Omni')
async def change_gpt_4(message:Message):
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name =='premium':
        model = 'gpt-4o'
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit>0:
            await change_gpt4(message.from_user.id, model)
            await message.answer('Ваша модель изменена...',reply_markup=kb.main_user)
        else:
            await message.answer('У вас превышен лимит.')
    else:
        await message.answer('У вас нет доступа к этой модели') 


@user.message(F.text=='DALLE')
async def change_gpt_4(message:Message):
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name in ['mini', 'start', 'premium']:
        model = 'dall-e-3'
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit>0:
            await change_gpt4(message.from_user.id,model)
            await message.answer('Ваша модель изменена...',reply_markup=kb.main_user)
        else:
            await message.answer('У вас превышен лимит.')
    else:
        await message.answer('У вас нет доступа к этой модели')



@user.message(F.text=='GPT-o1-Preview')
async def change_gpt_4(message:Message):
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name =='premium':
        model = 'o1-mini'
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit>0:
            await change_gpt4(message.from_user.id, model)
            await message.answer('Ваша модель изменена...',reply_markup=kb.main_user)
        else:
            await message.answer('У вас превышен лимит.')
    else:
        await message.answer('У вас нет доступа к этой модели') 


@user.message(F.text == 'Проверить')
async def check(message: Message,bot: Bot):
    status = await check_user_subscription(bot, message.from_user.id )
    if status == True:
        await message.answer('Вы подписаны')
    else:
        await message.answer('Вы ne подписаны')








