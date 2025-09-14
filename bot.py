# Импортируем нужные инструменты
import os
from telegram import Update, ReplyKeyboardMarkup, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Безопасность: получаем секреты из хранилища Render ---
TOKEN = os.environ.get('BOT_TOKEN')
# НОВОЕ: Получаем ваш личный CHAT_ID, куда будут приходить уведомления
ADMIN_CHAT_ID = os.environ.get('CHAT_ID') 

# --- Приветственное сообщение для команды /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [["Рассчитать стоимость (оставить заявку)"], ["Задать вопрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        f'Здравствуйте, {user_name}!\n\n'
        f'Я бот-помощник сайта ratio-legis.ru. Чем могу помочь?',
        reply_markup=reply_markup
    )

# --- НОВАЯ, УЛУЧШЕННАЯ ФУНКЦИЯ-ОБРАБОТЧИК ---
# Теперь она не только отвечает клиенту, но и пересылает сообщение вам.
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.effective_user
    
    # 1. ГОТОВИМ ОТВЕТ ДЛЯ КЛИЕНТА
    if user_message == "Рассчитать стоимость (оставить заявку)":
        response_to_client = 'Отлично! Чтобы рассчитать стоимость и оформить заявку, пожалуйста, напишите в одном сообщении:\n\n1. Номер дела и название суда.\n2. Ваш контактный телефон или email.'
    elif user_message == "Задать вопрос":
        response_to_client = 'Конечно, задавайте ваш вопрос. Специалист ответит вам в ближайшее время.'
    else:
        response_to_client = 'Спасибо, ваше сообщение принято! Мы скоро с вами свяжемся.'
        
    # 2. ГОТОВИМ УВЕДОМЛЕНИЕ ДЛЯ ВАС (АДМИНИСТРАТОРА)
    user_info = f"{user.first_name}"
    if user.last_name:
        user_info += f" {user.last_name}"
    if user.username:
        user_info += f" (@{user.username})"
        
    notification_to_admin = (
        f"📬 **Новое сообщение от клиента через бота!**\n\n"
        f"👤 **От:** {user_info}\n"
        f"✉️ **Сообщение:**\n`{user_message}`"
    )
    
    # 3. ОТПРАВЛЯЕМ СООБЩЕНИЯ
    try:
        # Сначала отправляем уведомление ВАМ
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID, 
                text=notification_to_admin,
                parse_mode=constants.ParseMode.MARKDOWN_V2 # Используем форматирование
            )
        else:
            print("Переменная CHAT_ID не установлена!")
            
        # Затем отвечаем КЛИЕНТУ
        await update.message.reply_text(response_to_client)
        
    except Exception as e:
        print(f"Произошла ошибка при отправке сообщения: {e}")
        # Если что-то пошло не так, сообщаем об этом клиенту
        await update.message.reply_text("Произошла техническая ошибка. Пожалуйста, попробуйте связаться с нами позже.")


# --- Основная часть, которая запускает бота (без изменений) ---
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот успешно запущен и готов к работе!")
    application.run_polling()

if __name__ == '__main__':
    main()
