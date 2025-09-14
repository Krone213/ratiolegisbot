import os
import re
from telegram import Update, ReplyKeyboardMarkup, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Секретные ключи из хранилища Render ---
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('CHAT_ID') 

# --- Функция "Обезвреживатель" Markdown (она нам еще пригодится) ---
def escape_markdown(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# --- ИСПРАВЛЕННАЯ ФУНКЦИЯ /start ---
# Мы просто убрали требование использовать parse_mode, так как форматирование здесь не нужно.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [["Рассчитать стоимость (оставить заявку)"], ["Задать вопрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    # ТЕПЕРЬ ЭТА СТРОКА БЕЗОПАСНА И НЕ БУДЕТ ВЫЗЫВАТЬ ОШИБКУ
    await update.message.reply_text(
        f'Здравствуйте, {user_name}!\n\n'
        f'Я бот-помощник сайта ratio-legis.ru. Чем могу помочь?',
        reply_markup=reply_markup
    )

# --- Улучшенный обработчик сообщений (без изменений) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.effective_user
    
    if user_message == "Рассчитать стоимость (оставить заявку)":
        response_to_client = 'Отлично! Чтобы рассчитать стоимость и оформить заявку, пожалуйста, напишите в одном сообщении:\n\n1. Номер дела и название суда.\n2. Ваш контактный телефон или email.'
    elif user_message == "Задать вопрос":
        response_to_client = 'Конечно, задавайте ваш вопрос. Специалист ответит вам в ближайшее время.'
    else:
        response_to_client = 'Спасибо, ваше сообщение принято! Мы скоро с вами свяжемся.'
        
    user_info = f"{user.first_name}"
    if user.last_name:
        user_info += f" {user.last_name}"
    if user.username:
        user_info += f" (@{user.username})"
    
    escaped_user_info = escape_markdown(user_info)
    escaped_user_message = escape_markdown(user_message)
        
    notification_to_admin = (
        f"📬 *Новое сообщение от клиента через бота\\!* \n\n"
        f"👤 *От:* {escaped_user_info}\n"
        f"✉️ *Сообщение:*\n`{escaped_user_message}`"
    )
    
    try:
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID, 
                text=notification_to_admin,
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
        else:
            print("Переменная CHAT_ID не установлена!")
            
        await update.message.reply_text(response_to_client)
        
    except Exception as e:
        print(f"!!! ПРОИЗОШЛА ОШИБКА ПРИ ОТПРАВКЕ УВЕДОМЛЕНИЯ АДМИНИСТРАТОРУ !!!")
        print(f"Ошибка: {e}")
        print(f"Текст, который не удалось отправить: {notification_to_admin}")
        await update.message.reply_text("Произошла техническая ошибка. Пожалуйста, попробуйте связаться с нами позже.")

# --- Основная часть (без изменений) ---
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот успешно запущен и готов к работе!")
    application.run_polling()

if __name__ == '__main__':
    main()
