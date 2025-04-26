# commands.py

from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот, который поможет следить за безопасностью дома.\n\n"
        "Я могу управлять датчиками света, отправлять сигналы о нарушителях порядка, и следить за открыванием дверей\n\n"
        "Ты можешь протесстировать все мои функции прямо сейчас, отправив мне видео, или загрузив себя в базу\n\n"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Помощь:\n"
        "- /start — начать работу\n"
        "- /help — вывести помощь\n\n"
        "- /bd — добавить себя в базу данных для доступа в дом\n\n"
        "Просто отправь видео, я всё сделаю!"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Я использую обученную модель YOLOv11 для классификации видео.🚀"
    )

async def bd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Отправь 30-60 секундное видео, где четко видно твое лицо, в течение часа, твое лицо будет добавлено"
    )
