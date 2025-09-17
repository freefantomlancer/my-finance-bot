import os
import logging
import asyncio # <<< ДОБАВЛЕНО: для асинхронной инициализации БД
import aiosqlite # <<< ДОБАВЛЕНО: для асинхронной работы с БД
import datetime
import threading # <<< ДОБАВЛЕНО: для запуска веб-сервера в отдельном потоке
from flask import Flask # <<< ДОБАВЛЕНО: для создания веб-сервера

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

ADMIN_ID = 432303629
DB_NAME = 'bot_database.db'
BOT_TOKEN = os.getenv("BOT_TOKEN")

def run_health_check_server():
    app = Flask(__name__)
    
    @app.route('/')
    def health_check():
        return "Bot is alive!", 200

    # Timeweb (и другие PaaS) передают порт через переменную окружения PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- СПИСОК ОФФЕРОВ ПО КРЕДИТАМ ---
CREDIT_OFFERS = [
    {
        "name": "Т-Банк",
        "image_id": "https://i.postimg.cc/wMCB6t1K/TBANK.png",
        "caption": (
            "🚀 **Т-Банк**\n\n"
            "Один из самых популярных сервисов. \n\n"
            "✅ **Сумма до 30 000 000 рублей на любые цели на срок от 3 месяцев до 15 лет**\n"
            "✅ Без справок о доходах и переоформления недвижимости на банк\n"
            "✅ Решение по заявке в день обращения"
        ),
        "url": "https://trk.ppdu.ru/click/s2VvyniV?erid=Kra244d1S&sub1=TGBOT"
    },
    {
        "name": "Банк ПСБ",
        "image_id": "https://i.postimg.cc/PqsFmdwt/PSB.png",
        "caption": (
            "💰 **Банк ПСБ**\n\n"
            "Надежный сервис с высоким процентом одобрения.\n\n"
            "✅ **Максимальная сумма 5 000 000 рублей. Рассчитывается, исходя из платежеспособности и кредитной истории заемщика.**\n"
            "✅ Минимальная сумма от 100 000 рублей\n"
            "✅ Срок кредита от 1 года до 7 лет"
        ),
        "url": "https://trk.ppdu.ru/click/l5iLa80x?erid=2SDnjcVVfjj&sub1=BOTTG"
    },
]

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING) # <<< ДОБАВЛЕНО: отключаем лишние логи от Flask
logger = logging.getLogger(__name__)


async def init_db(_) -> None:
    """Асинхронно инициализирует БД и создает таблицу, если ее нет."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            first_seen TEXT,
            last_seen TEXT
        )
        ''')
        await db.commit()
    logger.info("База данных успешно инициализирована.")

async def add_or_update_user(user):
    """Асинхронно добавляет/обновляет пользователя в БД."""
    user_id = user.id
    username = user.username
    first_name = user.first_name
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user_exists = await cursor.fetchone()

        if user_exists:
            await db.execute(
                "UPDATE users SET last_seen = ?, username = ?, first_name = ? WHERE user_id = ?",
                (now, username, first_name, user_id)
            )
        else:
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, first_name, now, now)
            )
        await db.commit()

async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Асинхронно получает и отправляет статистику (только для админа)."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(user_id) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]

        today = datetime.date.today().strftime('%Y-%m-%d')
        async with db.execute("SELECT COUNT(user_id) FROM users WHERE date(first_seen) = ?", (today,)) as cursor:
            today_users = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(user_id) FROM users WHERE date(last_seen) = ?", (today,)) as cursor:
            active_today = (await cursor.fetchone())[0]

    await update.message.reply_text(f"""
📊 **Статистика бота:**

- Всего пользователей: {total_users}
- Новых за сегодня: {today_users}
- Активных сегодня: {active_today}
""", parse_mode='Markdown')

# --- ФУНКЦИЯ ДЛЯ КОМАНДЫ /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await add_or_update_user(update.effective_user) 
    keyboard = [
        [InlineKeyboardButton("💸 Микрозаймы", callback_data='mfo')],
        [InlineKeyboardButton("💵 Кредит наличными", callback_data='cash_credit')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "Выберите продукт.\n\n"
        "Что именно вас интересует?"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    

# --- ОБРАБОТЧИК НАЖАТИЙ НА КНОПКИ ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await add_or_update_user(query.from_user) 
    await query.answer()

    if query.data == 'mfo':
        mfo_text = (
            "Чтобы получить займ от 1 000 до 100 000 руб. необходимо перейти по одной из ссылок ниже и заполнить анкету на сайте. (В течение 5 минут деньги придут вам на карту):\n\n"
            "🙋‍♀️ **Совет:** чтобы увеличить вероятность и скорость одобрения займа, оставьте анкеты сразу в нескольких компаниях, а лучше во всех!\n\n"
            "❤️ **ЗАЙМЕР** - Акция «Первый займ под 0% до 30.000₽»\n"
            "➡️ https://clck.ru/3Ns9sK\n\n"
            "🔥 **MONEYMAN** - Первый займ под 0% до 100.000₽.\n"
            "➡️ https://clck.ru/3Ns9tX\n\n"
            "**Webbankir** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NtDVN\n\n"
            "🔥 **Е-КАПУСТА** - Первый займ до 50 000 руб.\n"
            "➡️ https://clck.ru/3Ns9wo\n\n"
            "🔥 **Cashiro** - Первый займ под 0% до 30.000\n"
            "➡️ https://clck.ru/3Ns9yS\n\n"
            "🔥 **Max.Credit** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NsA6G\n\n"
            "🔥 **До Зарплаты** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NsA7M\n\n"
            "**Умные Наличные** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NtDWC\n\n"
            "**Credit7** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NtDWs\n\n"
            "**Boostra** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NtDXh\n\n"
            "🔥 **А Деньги** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NsA8o\n\n"
            "**Ваш кредит** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NsAAC\n\n"
            "**Свои люди** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NsAAj\n\n"
            "**ЗАЁМ.РУ** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NsA84\n\n"
            "**ДеньгиСразу** - Первый займ под 0% до 30.000₽\n"
            "➡️ https://clck.ru/3NsA5X\n\n"
            "↩️ Чтобы вернуться в главное меню, просто напишите /start"
        )
        
        await query.message.reply_text(
            text=mfo_text,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
            
    elif query.data == 'cash_credit':
        await query.message.reply_text("Так, кажется, я кое-что нашел для тебя. Посмотри, пожалуйста:")
        for offer in CREDIT_OFFERS:
            keyboard = [[InlineKeyboardButton("➡️ Получить деньги", url=offer["url"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # --- ИСПРАВЛЕНО: Восстановил недостающие строки и закрывающую скобку ---
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=offer["image_id"],
                caption=offer["caption"],
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="↩️ Чтобы вернуться в главное меню, просто напишите /start"
        )
    
    else:
        await query.edit_message_text(text="Этот раздел пока в разработке. Нажмите /start, чтобы вернуться в меню.")



# --- ЗАПУСК БОТА ---

def main() -> None:
    """Основная функция для запуска бота и сервера проверки здоровья."""

    # <<< ИЗМЕНЕНО: Запускаем веб-сервер в отдельном потоке >>>
    health_thread = threading.Thread(target=run_health_check_server, daemon=True)
    health_thread.start()
    logger.info("Health check server started in a separate thread.")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(init_db)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", get_stats))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()