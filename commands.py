# commands.py

from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для распознавания лиц и контроля доступа в дом.Это тествоая бесплатная версия\n\n"
        "📹 Я умею принимать видео, добавлять людей в базу, и следить за безопасностью.\n\n"
        "📋 Доступные команды:\n"
        "/start — начать работу\n"
        "/help — помощь\n"
        "/bd — добавить себя в базу\n"
        "/check — проверка открытия дверей\n"
        "/cancel — отменить текущую операцию\n"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Помощь:\n"
        "- /start — начать работу\n"
        "- /help — вывести список команд\n"
        "- /bd — добавить себя в базу\n"
        "- /check — проверка открытия дверей\n"
        "- /cancel — отменить текущую операцию\n\n"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Я использую дообученную модель YOLOv11 для классификации видео и распознавания лиц.\n"
        "🛡️ Постоянно обучаюсь, чтобы обеспечивать лучшую безопасность!"
    )

async def bd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 Отправь мне видео (10-60 секунд), где хорошо видно твоё лицо.\n"
        "Через 3-5 минут ты получишь доступ!"
    )

async def train(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Дообучение модели запущено! Пожалуйста, подожди несколько минут..."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Операция отменена. Можешь начать заново."
    )
