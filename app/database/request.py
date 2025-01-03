from app.database.models import async_session
from app.database.models import User, Subscription, Channels, Advertise
from sqlalchemy import select, func
from datetime import datetime, date, timedelta
from aiogram import Bot
from aiogram.types import ChatMember
from sqlalchemy import update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import IntegrityError

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
        tg_id = tg_id
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
            elif model == 'dall-e-3':
                return subscription.dalle_limit
    return 0

@connection
async def check_all_gpt_limits(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        subscription = await session.scalar(select(Subscription).where(Subscription.id == user.subscription_id))
        if subscription:
            return {
                "gpt_4_mini_limit": subscription.gpt_4_mini_limit,
                "gpt_4_limit": subscription.gpt_4_limit,
                "gpt_4_omni_limit": subscription.gpt_4_omni_limit,
                "gpt_o1_limit": subscription.gpt_o1_limit,
                "dalle_limit": subscription.dalle_limit,
            }
    return None  # Если пользователь или подписка не найдены

@connection
async def change_gpt4(session, tg_id,model):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        user.gpt_model = model
        await session.commit() 


        
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
    
    # Получаем пользователя из базы данных
    user = await session.execute(select(User).where(User.tg_id == tg_id))
    user = user.scalar_one_or_none()

    if user:  # Если пользователь найден
        is_active = True  # По умолчанию считаем, что пользователь активен

        # Проверяем, состоит ли пользователь в каждом канале
        for channel in channels:
            try:
                member: ChatMember = await bot.get_chat_member(chat_id=channel, user_id=tg_id)
                if member.status not in ("member", "administrator", "creator"):
                    is_active = False  # Если хотя бы в одном канале статус не подходящий, ставим False
                    break
            except Exception as e:
                print(f"Ошибка при проверке канала {channel}: {e}")
                is_active = False  # Ошибка при проверке канала также ставит False
                break

        # Обновляем поле verification_free в базе данных
        user.verification_free = is_active
        await session.commit()

        return is_active  # Возвращаем фактическую проверку подписки (True или False)
    
    else:
        print(f"Пользователь с tg_id {tg_id} не найден.")
        return False  # Если пользователь не найден, возвращаем False


@connection
async def reset_limits(session):
    await session.execute(
        update(Subscription)
        .where(Subscription.plan_name == 'mini')
        .values(
            gpt_4_mini_limit=100,
            gpt_4_limit=5,
            dalle_limit=10
        )
    )
    await session.execute(
        update(Subscription)
        .where(Subscription.plan_name == 'start')
        .values(
            gpt_4_mini_limit=10000,
            gpt_4_limit=25,
            dalle_limit=30
        )
    )
    await session.execute(
        update(Subscription)
        .where(Subscription.plan_name == 'premium')
        .values(
            gpt_4_mini_limit=10000,
            gpt_4_omni_limit=50,
            gpt_4_limit=50,
            gpt_o1_limit=25,
            dalle_limit=100
        )
    )
    await session.commit()
    print('Все окей')


@connection
async def update_free_user_limits(session):
    free_users = await session.execute(
        select(User).join(Subscription, User.subscription_id == Subscription.id)
        .where(Subscription.plan_name == 'free')
    )
    users_to_update = free_users.scalars().all()
    for user in users_to_update:
        is_active = user.verification_free
        new_limit = 10 if is_active else 5
        await session.execute(
            update(Subscription)
            .where(Subscription.id == user.subscription_id)
            .values(gpt_4_mini_limit=new_limit)
        )
    await session.commit()
    print("Лимиты для пользователей с подпиской 'free' успешно обновлены.")



def schedule_daily_task(scheduler):
    scheduler.add_job(
        reset_limits,  # Функция для выполнения
        "cron", 
        hour=0, 
        minute=0, 
        timezone="Europe/Moscow"  # Указываем часовой пояс
    )
        # Добавляем задачу для update_free_user_limits
    scheduler.add_job(
        update_free_user_limits,  # Используем лямбда-функцию для передачи bot
        "cron", 
        hour=0,  # Пример времени
        minute=0, 
        timezone="Europe/Moscow"  # Указываем часовой пояс
    )


@connection
async def get_today_users_count(session):
    today = date.today()  # Получаем текущую дату
    result = await session.scalar(
        select(func.count(User.id)).where(User.registration_date == today)
    )
    return result or 0

@connection
async def get_total_users_count(session):
    result = await session.scalar(select(func.count(User.id)))
    return result or 0


@connection
async def get_all_channels(session):
    result = await session.execute(select(Channels))  # Извлекаем все каналы
    channels = result.scalars().all()  # Преобразуем результат в список объектов
    return channels


@connection
async def add_channel(session, channel_name: str):
    # Проверяем, что имя канала начинается с '@'
    if not channel_name.startswith('@'):
        raise ValueError("Имя канала должно начинаться с '@'")
    
    # Создаем новый объект канала
    new_channel = Channels(channel_name=channel_name)
    
    # Добавляем в сессию и коммитим изменения
    session.add(new_channel)
    try:
        await session.commit()  # Сохраняем изменения в базе данных
    except IntegrityError:
        await session.rollback()  # Откатываем, если есть ошибка уникальности
        raise ValueError(f"Канал с именем {channel_name} уже существует в базе данных.")
    

@connection
async def delete_channel(session, channel_name: str):
    # Находим канал по имени
    channel = await session.scalar(select(Channels).where(Channels.channel_name == channel_name))
    
    if not channel:
        raise ValueError(f"Канал с именем {channel_name} не найден.")
    
    # Удаляем канал
    await session.delete(channel)
    await session.commit()  # Сохраняем изменения в базе данных


@connection
async def change_subscription_by_tg_id(session, tg_id: int, new_plan: str):
    # Находим пользователя по его tg_id
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    
    if user:
        # Находим тариф по названию плана
        subscription = await session.scalar(select(Subscription).where(Subscription.plan_name == new_plan))
        
        if subscription:
            # Обновляем подписку пользователя
            user.subscription_id = subscription.id
            await session.commit()  # Сохраняем изменения в базе данных
            return True
        else:
            raise ValueError(f"Тариф с именем {new_plan} не найден.")
    else:
        raise ValueError(f"Пользователь с tg_id {tg_id} не найден.")


@connection
async def get_all_adverts(session):
    result = await session.execute(select(Advertise.text))  # Извлекаем только поле text
    texts = result.scalars().all()  # Преобразуем результат в список текстов
    print("Adverts in DB:", texts)
    return texts


@connection
async def get_user_advert_index(session, user_id: int):
    result = await session.execute(
        select(User.advert_index).where(User.tg_id == user_id)
    )
    index = result.scalar()
    print(f"User {user_id} advert index:", index)
    return index if index is not None else 0  # Если нет индекса, начинаем с 0


@connection
async def set_user_advert_index(session, user_id: int, index: int):
    result = await session.execute(
        select(User).where(User.tg_id == user_id)
    )
    user = result.scalar()
    if user:
        print(f"Updating user {user_id} advert index to {index}")
        user.advert_index = index
        await session.commit()
    else: 
        print(f"User {user_id} not found!")


@connection
async def add_advertise(session, text):
    new_advert = Advertise(text=text)
    session.add(new_advert)
    await session.commit()


@connection
async def delete_advertise(session, advert_id):
    advert = await session.scalar(select(Advertise).where(Advertise.id == advert_id))
    if advert:
        await session.delete(advert)
        await session.commit()
        return True
    return False 


@connection
async def get_all_advertises(session):
    adverts = await session.execute(select(Advertise))
    return adverts.scalars().all()


@connection
async def create_subscription(session, tg_id: int, plan_name: str):
    plan_limits = {
        "mini": {"gpt_4_mini_limit": 100, "gpt_4_limit": 5, "dalle_limit": 10},
        "start": {"gpt_4_mini_limit": 10000, "gpt_4_limit": 25, "dalle_limit": 30},
        "premium": {
            "gpt_4_mini_limit": 10000,
            "gpt_4_limit": 50,
            "dalle_limit": 100,
            "gpt_4_omni_limit": 50,
            "gpt_o1_limit": 25,
        },
    }
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user:
        raise ValueError("Пользователь с указанным Telegram ID не найден")
    limits = plan_limits[plan_name]
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=30)
    new_subscription = Subscription(
        plan_name=plan_name,
        start_date=start_date,
        end_date=end_date,
        gpt_4_mini_limit=limits.get("gpt_4_mini_limit", 0),
        gpt_4_limit=limits.get("gpt_4_limit", 0),
        gpt_4_omni_limit=limits.get("gpt_4_omni_limit", 0),
        gpt_o1_limit=limits.get("gpt_o1_limit", 0),
        dalle_limit=limits.get("dalle_limit", 0),
        tg_id = tg_id
    )
    session.add(new_subscription)
    await session.flush()
    user.subscription_id = new_subscription.id
    await session.commit()
    return new_subscription

@connection
async def get_user_subscriptions(session,tg_id: int):
    # Выполняем запрос на получение всех подписок для указанного tg_id
    result = await session.execute(
        select(Subscription).filter(Subscription.tg_id == tg_id)
    )
    # Возвращаем все подписки пользователя
    return result.scalars().all()


@connection
async def delete_subscription(session, tg_id: int, plan_name: str):
    subscription = await session.scalar(
        select(Subscription).where(
            Subscription.tg_id == tg_id, Subscription.plan_name == plan_name
        )
    )
    if not subscription:
        raise ValueError(f"Подписка с именем '{plan_name}' для пользователя с ID {tg_id} не найдена.")
    await session.delete(subscription)
    await session.commit() 
