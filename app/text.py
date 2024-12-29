hello_text = (
    "Привет! Бот предоставляет доступ к искусственному интеллекту — ChatGPT: gpt-4o-mini, "
    "gpt-o1-preview, gpt-4o (Omni), DALL.\n"
    "Здесь вы можете выполнять самые разнообразные задачи:\n"
    "1. Копирайтинг и рерайтинг.\n"
    "2. Написание и редактирование кода.\n"
    "3. Перевод с любого языка.\n"
    "4. Разбор неструктурированного текста и резюмирование.\n"
    "5. Создание высококачественного текстового контента.\n"
    "6. Чат.\n"
    "7. Генерация изображений по текстовому описанию.\n\n"
    "Чтобы получить ответ, напишите свой вопрос в чат.\n"
    "Приятного пользования!"
)


support_text = ("Здравствуйте! Вы обратились в службу поддержки. Если у вас возникли вопросы или проблемы, "
        "пожалуйста, напишите ваш запрос, и мы постараемся помочь вам как можно скорее.")


tarif_text=("Mini — 4$ в месяц\n"
    "— GPT 4o (Mini): 100 сообщений в день\n"
    "— GPT 4: 5 сообщений в день\n"
    "— DALL: 10 изображений\n\n"
    "Start — 8$ в месяц\n"
    "— GPT 4o (Mini): безлимитно\n"
    "— GPT 4: 25 сообщений в день\n"
    "— DALL: 30 изображений в день\n\n"
    "Premium — 12$ в месяц\n"
    "— GPT 4o (Mini): безлимитно\n"
    "— GPT 4o (Omni): 50 сообщений в день\n"
    "— GPT 4: 50 сообщений в день\n"
    "— gpt-o1-preview: 25 сообщений в день\n"
    "— DALL: 100 изображений\n\n")

free_limit_text = (
    'Сегодня вы уже отправили 5 запросов боту. Чтобы увеличить свой лимит ежедневных бесплатных запросов в два раза до 10, подпишитесь на наши каналы или оформите любой тариф.\n\n\n'
    'Вы также можете мгновенно активировать БЕЗЛИМИТНЫЕ запросы, более мощные и продвинутые модели искусственного интеллекта GPT-4o, OpenAI o1 и открыть новые возможности бота с тарифом /premium'
)

free_limit_textact = (
    'Ваш дневной лимит запросов исчерпан.\n' 
    'Чтобы увеличить лимит запросов оформите тариф на месяц.\n'
    'Ваши БЕСПЛАТНЫЕ запросы обновятся через 24 часа.'

)

podpiska_activna = (
    'Подтверждена подписка на каналы.\n\n'
    'Количество БЕСПЛАТНЫХ суточных запросов увеличено до 10.'
)

def stats_text(balance,new_users,total_users): 
    
    return (
        "📊 *Статистика бота*\n\n"
        f"💰 *Баланс:* `{balance:.2f} ₽`\n"
        f"👥 *Новые пользователи сегодня:* `{new_users}`\n"
        f"🌍 *Общее количество пользователей:* `{total_users}`\n\n"
        "Для управления используйте кнопки ниже."
    )

gpt4mini_text = (
    'Вы превысили лимит использования. Однако вы можете продолжить работать с моделью, оформив тариф Start или Premium. Эти тарифы позволят вам получить доступ к безлимитным возможностям и наслаждаться работой без ограничений!'
)

free_choice_model =(
    'У вас нет доступа к этой модели. Вы можете оформить месячный тариф, чтобы разблокировать её возможности и пользоваться всеми функциями'
)

def change_model(plan,limits):
    return (
        f"💎 Ваш тариф: <b>{plan.capitalize()}</b>\n\n"
        "📊 <u>Доступные лимиты:</u>\n"
        f"🔹 GPT 4o Mini: <b>{limits['gpt_4_mini_limit']}</b>\n"
        f"🔹 GPT 4: <b>{limits['gpt_4_limit']}</b>\n"
        f"🔹 GPT 4o Omni: <b>{limits['gpt_4_omni_limit']}</b>\n"
        f"🔹 DALL-E: <b>{limits['dalle_limit']}</b>\n"
        f"🔹 GPT-o1-Preview: <b>{limits['gpt_o1_limit']}</b>\n\n"
        "💡 Выберите модель для продолжения."
    )