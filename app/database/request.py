from app.database.models import async_session
from app.database.models import User, Subscription, Channels
from sqlalchemy import select
from datetime import datetime
from aiogram import Bot
from aiogram.types import ChatMember
from sqlalchemy import update
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner
    

@connection
async def set_user(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        return 
    new_subscription = Subscription(
        plan_name='free',  
        start_date=datetime.utcnow(),
        gpt_4_mini_limit=5,
        gpt_4_limit=0,
        gpt_4_omni_limit=0,
        dalle_limit=0,
        unlimited_gpt_4_mini=False
    )
    session.add(new_subscription)
    await session.flush()  
    new_user = User(tg_id=tg_id, subscription_id=new_subscription.id)
    session.add(new_user)
    await session.commit() 


@connection
async def get_gpt_model(session,tg_id):
    user = await session.scalar(select(User.gpt_model).where(User.tg_id == tg_id))
    return user 


@connection
async def get_user(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user

@connection
async def get_user_plan_name(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        subscription = await session.scalar(select(Subscription).where(Subscription.id == user.subscription_id))
        if subscription:
            return subscription.plan_name
    return None


@connection
async def check_gpt_limit(session, tg_id, model):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        subscription = await session.scalar(select(Subscription).where(Subscription.id == user.subscription_id))
        if subscription:
            if model == 'gpt-4o-mini':
                return subscription.gpt_4_mini_limit
            elif model == 'gpt-4':
                return subscription.gpt_4_limit
            elif model == 'gpt-4o':
                return subscription.gpt_4_omni_limit
            elif model == 'o1':
                return subscription.gpt_o1_limit
    return 0


@connection
async def change_gpt4(session, tg_id,model):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        user.gpt_model = model
        await session.commit() 


@connection
async def check_unlimit_gpt(session,tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        subscription = await session.scalar(select(Subscription).where(Subscription.id == user.subscription_id))
        if subscription:
            response = subscription.unlimited_gpt_4_mini
            print(f'Ваш безлимит:{response}')
            return response
        
@connection
async def decrement_gpt_limit(session, tg_id, model):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        subscription = await session.scalar(select(Subscription).where(Subscription.id == user.subscription_id))
        if subscription:
            if model == 'gpt-4o-mini':
                subscription.gpt_4_mini_limit -= 1
            elif model == 'gpt-4':
                subscription.gpt_4_limit -= 1
            elif model == 'gpt-4o':
                subscription.gpt_4_omni_limit -= 1
            elif model == 'o1':
                subscription.gpt_o1_limit -= 1
            await session.commit()


@connection
async def check_user_subscription(session, bot, tg_id):
    channels = await session.execute(select(Channels.channel_name))
    channels = channels.scalars().all()
    for channel in channels:
        try:
            member: ChatMember = await bot.get_chat_member(chat_id=channel, user_id=tg_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except Exception as e:
            print(f"Ошибка при проверке канала {channel}: {e}")
            return False
    return True


@connection
async def reset_limits(session):
    # Обновляем лимиты для пользователей с подпиской "mini"
    await session.execute(
        update(Subscription)
        .where(Subscription.plan_name == 'mini')
        .values(
            gpt_4_mini_limit=100,
            gpt_4_limit=5,
            dalle_limit=10
        )
    )
    
    # Обновляем лимиты для пользователей с подпиской "start"
    await session.execute(
        update(Subscription)
        .where(Subscription.plan_name == 'start')
        .values(
            gpt_4_mini_limit=1,
            gpt_4_limit=25,
            dalle_limit=30
        )
    )

    # Обновляем лимиты для пользователей с подпиской "premium"
    await session.execute(
        update(Subscription)
        .where(Subscription.plan_name == 'premium')
        .values(
            gpt_4_mini_limit=1,
            gpt_4_omni_limit=50,
            gpt_4_limit=50,
            gpt_o1_limit=25,
            dalle_limit=100
        )
    )

    # Сохраняем изменения
    await session.commit()


def schedule_daily_task():
    scheduler.add_job(
        reset_limits,  # Функция для выполнения
        "cron", 
        hour=0, 
        minute=0, 
        timezone="Europe/Moscow"  # Указываем часовой пояс
    )
    scheduler.start()