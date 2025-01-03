from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
import app.text as txt
from app.database.request import (set_user, get_gpt_model, get_user_plan_name,get_all_adverts,
                                  change_gpt4, check_gpt_limit,get_all_channels,check_all_gpt_limits,
                                  decrement_gpt_limit,check_user_subscription,reset_limits, update_free_user_limits,
                                  set_user_advert_index,get_user_advert_index, create_subscription)
from app.generators import gpt_text, gpt_image, get_balance
from app.state import Chat, Image
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from aiogram import Bot


user = Router()

@user.message(F.text =='Главное меню')
@user.message(F.text=='Выйти из чата')
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await set_user(message.from_user.id)
    await message.answer(txt.hello_text, reply_markup= kb.main_user)
    

@user.message(F.text=='Создать новый чат')
async def chatting(message: Message, state: FSMContext, bot: Bot):
    model = await get_gpt_model(message.from_user.id)
    limit = await check_gpt_limit(message.from_user.id,model)
    plan = await get_user_plan_name(message.from_user.id)
    podpiski = await check_user_subscription(bot, message.from_user.id)
    if limit == 0 and plan == 'free' and podpiski == False:
        channels = await get_all_channels()
        await message.answer(txt.free_limit_text,reply_markup=kb.inline_keyboard(channels))
        await message.answer('Можете проверить подписку по кнопке ниже⬇️',reply_markup=kb.check_channels)
    elif limit == 0 and plan == 'free' and podpiski == True:
        await message.answer(txt.free_limit_textact,reply_markup=kb.tarif_inline)
    elif limit == 0 and plan in ["premium", "start"] and model in['gpt-4','gpt-4o','dall-e-3','o1-mini']:
        await message.answer('У закончился лимит, смените модель',reply_markup=kb.main_user)
    elif limit == 0 and plan == 'mini' and model in ['gpt-4o-mini','gpt-4','gpt-4o','dall-e-3','o1-mini']:
        await message.answer('У закончился лимит, смените модель',reply_markup=kb.main_user)
    else:
        if model == 'dall-e-3':
            await state.set_state(Image.text)
            await message.answer('Введите ваш запрос картинки',reply_markup=kb.chat_exit)
        else:
            await state.set_state(Chat.text)
            await message.answer('Введите ваш запрос',reply_markup=kb.chat_exit)


@user.message(Image.text)
async def chat_response(message: Message, state: FSMContext):
    limit = await check_gpt_limit(message.from_user.id,model)
    model = await get_gpt_model(message.from_user.id)
    if limit == 0:
        await message.answer('У вас закончился лимит..', reply_markup=kb.main_user)
        await state.clear()
    else:
        await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_PHOTO)
        await state.set_state(Image.wait)
        await decrement_gpt_limit(message.from_user.id, model)
        response = await gpt_image(message.text, model)
        await message.answer_photo(photo=response['response'])
        await state.set_state(Image.text)


@user.message(Chat.text)
async def generate_text(message: Message, state: FSMContext):
    model = await get_gpt_model(message.from_user.id)
    subscription = await get_user_plan_name(message.from_user.id)
    limit = await check_gpt_limit(message.from_user.id, model)
    
    if limit == 0:
        await state.clear()
        await message.answer('У вас закончился лимит', reply_markup=kb.main_user)
        return

    # Получаем историю из состояния
    data = await state.get_data()
    history = data.get('history', [])
    history.append({"role": "user", "content": message.text})
    history = history[-20:]  # Оставляем только последние 20 сообщений

    if subscription == 'free':
        if limit > 0: 
            await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
            await state.set_state(Chat.wait)
            
            # Работа с рекламой
            adverts = await get_all_adverts()
            current_index = await get_user_advert_index(message.from_user.id)
            next_index = (current_index + 1) % len(adverts)
            next_advert = adverts[next_index]
            await set_user_advert_index(message.from_user.id, next_index)

            # GPT-ответ
            response = await gpt_text(history, model)
            await decrement_gpt_limit(message.from_user.id, model)
            
            # Обновляем историю
            history.append({"role": "assistant", "content": response})
            await state.update_data(history=history)

            await message.answer(response, parse_mode='Markdown')
            await message.answer(f"_Реклама_\n\n  {next_advert.text}", parse_mode='Markdown', reply_markup=kb.off_advert)
            await state.set_state(Chat.text)
        else:
            await message.answer('У вас закончился лимит..', reply_markup=kb.main_user)
            await state.clear()

    elif subscription in ["premium", "start"] and model == "gpt-4o-mini":
        await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
        await state.set_state(Chat.wait)
        
        # GPT-ответ
        response = await gpt_text(history, model)

        # Обновляем историю
        history.append({"role": "assistant", "content": response})
        await state.update_data(history=history)

        await message.answer(response, parse_mode='Markdown')
        await state.set_state(Chat.text)

    else:
        if limit > 0: 
            await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
            await state.set_state(Chat.wait)

            # GPT-ответ
            response = await gpt_text(history, model)
            await decrement_gpt_limit(message.from_user.id, model)

            # Обновляем историю
            history.append({"role": "assistant", "content": response})
            await state.update_data(history=history)

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


@user.message(F.text == 'Смена модели')
async def models(message: Message):
    plan = await get_user_plan_name(message.from_user.id)
    limits = await check_all_gpt_limits(message.from_user.id)
    await message.answer(txt.change_model(plan,limits), reply_markup=kb.models_user, parse_mode="HTML")


@user.message(F.text=='Поддержка')
async def support(message:Message):
    adverts = await get_all_adverts()  # Получаем только тексты объявлений
    if adverts:  # Если объявления существуют
        text = "\n\n".join(adverts)
    await message.answer(text)
    await message.answer(txt.support_text, reply_markup=kb.support_inline)


@user.message(F.text =='Тарифы')
async def tarif(message: Message):
    await message.answer(txt.tarif_text,reply_markup=kb.tarify_inline)


@user.callback_query(F.data == 'tarif')
async def tarif_inline( callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(txt.tarif_text,reply_markup=kb.tarify_inline)
    await callback.answer()


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
        await message.answer('Ваша модель изменена', reply_markup=kb.main_user)
    elif subscription =='mini':
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit > 0: 
            await change_gpt4(message.from_user.id, model)
            await message.answer('Ваша модель изменена', reply_markup=kb.main_user)
        else:
            await message.answer(txt.gpt4mini_text, reply_markup=kb.tarif_inline)
    elif subscription =='free':
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit > 0:
            await change_gpt4(message.from_user.id, model)
            await message.answer('Ваша модель изменена', reply_markup=kb.main_user)
        else:
            await message.answer(txt.free_limit_textact, reply_markup=kb.tarif_inline)


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
            await message.answer('У вас закончился дневной лимит, он обновится в 00:00 по МСК')
    else:
        await message.answer(txt.free_choice_model,reply_markup=kb.tarif_inline)


@user.message(F.text=='GPT 4o Omni')
async def change_gpt_4(message:Message):
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name =='premium':
        model = 'gpt-4o'
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit>0:
            await change_gpt4(message.from_user.id, model)
            await message.answer('Ваша модель изменена',reply_markup=kb.main_user)
        else:
            await message.answer('У вас закончился дневной лимит, он обновится в 00:00 по МСК')
    else:
        await message.answer(txt.free_choice_model,reply_markup=kb.tarif_inline) 


@user.message(F.text=='DALLE')
async def change_gpt_4(message:Message):
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name in ['mini', 'start', 'premium']:
        model = 'dall-e-3'
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit>0:
            await change_gpt4(message.from_user.id,model)
            await message.answer('Ваша модель изменена',reply_markup=kb.main_user)
        else:
            await message.answer('У вас закончился дневной лимит, он обновится в 00:00 по МСК')
    else:
        await message.answer(txt.free_choice_model,reply_markup=kb.tarif_inline)



@user.message(F.text=='GPT-o1-Preview')
async def change_gpt_4(message:Message):
    plan_name = await get_user_plan_name(message.from_user.id)
    if plan_name =='premium':
        model = 'o1-mini'
        limit = await check_gpt_limit(message.from_user.id, model)
        if limit>0:
            await change_gpt4(message.from_user.id, model)
            await message.answer('Ваша модель изменена',reply_markup=kb.main_user)
        else:
            await message.answer('У вас закончился дневной лимит, он обновится в 00:00 по МСК')
    else:
        await message.answer(txt.free_choice_model,reply_markup=kb.tarif_inline)


@user.message(F.text == 'Проверить')
async def check(message: Message,bot: Bot):
    status = await check_user_subscription(bot, message.from_user.id )
    if status == True:
        await message.answer(txt.podpiska_activna)
    else:
        await message.answer('Вы не подписались')


@user.callback_query(F.data == 'buy_mini')
async def buy_mini(callback: CallbackQuery):
    plan_name = 'mini'
    await create_subscription(callback.from_user.id, plan_name)
    await callback.answer('Вы успешно приобрели тариф')
    await callback.message.edit_text('Вы успешно приобрели тариф', reply_markup=None)


@user.callback_query(F.data == 'buy_start')
async def buy_mini(callback: CallbackQuery):
    plan_name = 'start'
    await create_subscription(callback.from_user.id, plan_name)
    await callback.answer('Вы успешно приобрели тариф')
    await callback.message.edit_text('Вы успешно приобрели тариф', reply_markup=None)


@user.callback_query(F.data == 'buy_premium')
async def buy_mini(callback: CallbackQuery):
    plan_name = 'premium'
    await create_subscription(callback.from_user.id, plan_name)
    await callback.answer('Вы успешно приобрели тариф')
    await callback.message.edit_text('Вы успешно приобрели тариф', reply_markup=None)





