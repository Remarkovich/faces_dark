from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from commands import start, help_command, about, bd
# from video_handler import handle_video

app = ApplicationBuilder().token("8184614570:AAHI5UEqPBKIqp-a8zw_bZAazpaioSsJMz4").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("about", about))
app.add_handler(CommandHandler("bd", bd))
# app.add_handler(MessageHandler(filters.VIDEO, handle_video))

# Устанавливаем команды
async def setup_commands():
    await app.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Помощь"),
        # BotCommand("about", "О проекте"),
        BotCommand("bd", "База данных"),
    ])

# Просто запускаем бота
if __name__ == "__main__":
    app.run_polling()
