# Импортируем нужные инструменты
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Безопасность: получаем токен из секретного хранилища Render ---
# Мы не будем писать токен прямо в коде. Render подставит его сюда при запуске.
TOKEN = os.environ.get('BOT_TOKEN')


# --- Приветственное сообщение для команды /start ---
# Эта функция сработает, когда пользователь нажмет "Start" в первый раз.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name

    # Создаем кастомную клавиатуру для удобства
    keyboard = [["Рассчитать стоимость (оставить заявку)"], ["Задать вопрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        f'Здравствуйте, {user_name}!\n\n'
        f'Я бот-помощник сайта ratio-legis.ru. Чем могу помочь?',
        reply_markup=reply_markup
    )


# --- Функция-обработчик для текстовых сообщений ---
# Она будет реагировать на любой текст, который напишет пользователь.
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Простое ветвление логики на основе кнопок
    if text == "Рассчитать стоимость (оставить заявку)":
        response_text = 'Отлично! Чтобы рассчитать стоимость и оформить заявку, пожалуйста, напишите в одном сообщении:\n\n1. Номер дела и название суда.\n2. Ваш контактный телефон или email.'
    elif text == "Задать вопрос":
        response_text = 'Конечно, задавайте ваш вопрос. Специалист ответит вам в ближайшее время.'
    else:
        # Ответ на любое другое сообщение (номер дела, вопрос и т.д.)
        response_text = 'Спасибо, ваше сообщение принято! Мы скоро с вами свяжемся.'

    await update.message.reply_text(response_text)


# --- Основная часть, которая запускает бота ---
def main():
    # Создаем "приложение" бота
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики: один для команды /start, второй для всех текстовых сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота. Он будет непрерывно работать и "слушать" сообщения.
    print("Бот успешно запущен!")
    application.run_polling()


# Эта строка гарантирует, что функция main() запустится, когда мы запустим файл
if __name__ == '__main__':
    main()