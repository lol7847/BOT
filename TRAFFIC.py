import logging
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import Forbidden, ChatNotFound
from flask import Flask

# Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "7974108077:AAHlziI44egQWkn4k9t1ZWWw7SJbrHqfdUk"
CHANNELS = {
    -1002538168053: "https://t.me/TESTIK1P",
    -1002598779320: "https://t.me/TESTIK2P"
}
MAIN_CHANNEL_LINK = "https://t.me/+S-9mdBW05zVkMWMy"

# Flask app для health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=8000)

# Функции бота
def get_channels_keyboard():
    keyboard = []
    for url in CHANNELS.values():
        keyboard.append([InlineKeyboardButton("🔔 Подписаться", url=url)])
    keyboard.append([InlineKeyboardButton("✅ Проверить подписку", callback_data="check")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Подпишитесь на каналы и нажмите проверку:",
        reply_markup=get_channels_keyboard()
    )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    unsubscribed = []

    for channel_id in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel_id, user_id)
            logger.info(f"Проверка канала {channel_id}. Статус: {member.status}")
            
            if member.status not in {"member", "administrator", "creator"}:
                unsubscribed.append(channel_id)
                logger.warning(f"Пользователь {user_id} не подписан на {channel_id}")
                
        except (Forbidden, ChatNotFound) as e:
            logger.error(f"Ошибка доступа к каналу {channel_id}: {str(e)}")
            unsubscribed.append(channel_id)
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {str(e)}")
            unsubscribed.append(channel_id)

    if unsubscribed:
        await query.answer("❌ Вы подписаны не на все каналы!", show_alert=True)
    else:
        keyboard = [[InlineKeyboardButton("🔥 Войти в главный канал", url=MAIN_CHANNEL_LINK)]]
        await query.message.reply_text(
            "✅ Вы успешно подписаны на все каналы!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

if __name__ == "__main__":
    # Запуск Flask сервера в фоне
    Thread(target=run_flask, daemon=True).start()
    
    # Инициализация бота
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="^check$"))
    
    logger.info("Бот запущен...")
    application.run_polling()
