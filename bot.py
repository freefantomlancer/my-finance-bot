# --- НАЧАЛО ИСПРАВЛЕННОГО КОДА ---

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- НАСТРОЙКИ ---
# ВСТАВЬ СЮДА СВОЙ НОВЫЙ ТОКЕН ИЗ BOTFATHER!
BOT_TOKEN = "7390156846:AAESpYLbIwcKUy3ctMXyY6fVRKXATWQuY3g" 

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
logger = logging.getLogger(__name__)

# --- ФУНКЦИЯ ДЛЯ КОМАНДЫ /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("💸 Микрозаймы", callback_data='mfo')],
        [InlineKeyboardButton("💵 Кредит наличными", callback_data='cash_credit')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "ВЫБИРАЙ ПРОДУКТ.\n\n"
        "Что именно тебя интересует?"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )

# --- ОБРАБОТЧИК НАЖАТИЙ НА КНОПКИ ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'mfo':
        mfo_text = (
            "Чтобы получить займ от 3 000 до 30 000 руб. необходимо перейти по одной из ссылок ниже и заполнить анкету на сайте. (В течение 5 минут деньги придут вам на карту):\n\n"
            "🙋‍♀️ **Совет:** чтобы увеличить вероятность и скорость одобрения займа, оставьте анкеты сразу в нескольких компаниях, а лучше во всех!\n\n"
            "❤️ **ЗАЙМЕР** - Акция «Первый займ под 0%»\n"
            "➡️ https://clck.ru/3Ns9sK\n\n"
            "🔥 **MONEYMAN** - Первый займ под 0%.\n"
            "➡️ https://clck.ru/3Ns9tX\n\n"
            "🔥 **Е-КАПУСТА** - Первый займ до 50 000 руб.\n"
            "➡️ https://clck.ru/3Ns9wo\n\n"
            "🔥 **Cashiro** - Первый займ до 30.000\n"
            "➡️ https://clck.ru/3Ns9yS\n\n"
            "🔥 **Max.Credit** - Первый займ до 30.000₽\n"
            "➡️ https://clck.ru/3NsA6G\n\n"
            "🔥 **До Зарплаты** - Первый займ до 30.000₽\n"
            "➡️ https://clck.ru/3NsA7M\n\n"
            "🔥 **А Деньги** - Первый займ до 30.000₽\n"
            "➡️ https://clck.ru/3NsA8o\n\n"
            "**Ваш кредит** - Первый займ до 30.000₽\n"
            "➡️ https://clck.ru/3NsAAC\n\n"
            "**Свои люди** - Первый займ до 30.000₽\n"
            "➡️ https://clck.ru/3NsAAj\n\n"
            "**ЗАЁМ.РУ** - Первый займ до 30.000₽\n"
            "➡️ https://clck.ru/3NsA84\n\n"
            "**ДеньгиСразу** - Первый займ до 30.000₽\n"
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
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

if __name__ == "__main__":
    main()

# --- КОНЕЦ КОДА ---