
# import os
# import cv2
# import asyncio
# import logging
# from telegram import Update, BotCommand
# from telegram.ext import (
#     ApplicationBuilder,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ContextTypes,
# )
# from telegram.request import HTTPXRequest
# from test_model import recognize_image

# # Импортируем функции обработки видео и команд
# import video_handler
# from commands import start, help_command, about, train, cancel
# import train_model

# # Настройка логирования
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )
# logger = logging.getLogger(__name__)

# # Токен бота
# TOKEN = '8184614570:AAHI5UEqPBKIqp-a8zw_bZAazpaioSsJMz4'

# # Создаем приложение с увеличенным таймаутом для загрузки файлов
# request = HTTPXRequest(connect_timeout=10, read_timeout=60)
# app = ApplicationBuilder().token(TOKEN).request(request).build()

# # Хендлер для команды /bd: запускает ожидание видео
# async def bd_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     context.user_data.clear()
#     context.user_data['await_video'] = True
#     await update.message.reply_text(
#         "📥 Отправьте мне видео (MP4), чтобы добавить в базу и дообучить модель."
#     )

# # Хендлер для получения видео и сохранения
# async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not context.user_data.get('await_video'):
#         await update.message.reply_text(
#             "⚠️ Используйте команду /bd, чтобы начать процесс добавления в базу."
#         )
#         return

#     message = update.message
#     user = message.from_user
#     user_id = user.id
#     username = user.username or str(user_id)

#     video_file = message.video or (
#         message.document if message.document and message.document.mime_type == 'video/mp4' else None
#     )
#     if not video_file:
#         await message.reply_text("Пожалуйста, отправьте видео в формате MP4.")
#         return

#     # Скачиваем и сохраняем видео временно
#     file_obj = await video_file.get_file()
#     video_bytes = await file_obj.download_as_bytearray()
#     video_path = video_handler.save_video(video_bytes, user_id)

#     # Сохраняем путь и прекращаем ожидание
#     context.user_data['await_video'] = False
#     context.user_data['video_path'] = video_path
#     context.user_data['username'] = username

#     await update.message.reply_text(
#         "✅ Видео получено и сохранено. Запускаю разбивку на кадры и дообучение модели..."
#     )

#     # Разбивка на кадры
#     frame_count = video_handler.process_video_to_frames(video_path, username)
#     await update.message.reply_text(
#         f"🎞️ Кадров получено: {frame_count}, сохранены в output_frames/train/{username} и output_frames/val/{username}."
#     )

#     # Подготовка data и обучение
#     dataset_yaml = video_handler.prepare_data_split(f"output_frames/{username}") if hasattr(video_handler, 'prepare_data_split') else None
#     train_input = dataset_yaml or os.path.abspath("output_frames")

#     try:
#         metrics = train_model.train_model(train_input)
#         await update.message.reply_text(
#             f"🎉 Обучение завершено! Метрики валидации:\n{metrics}"
#         )
#     except Exception as e:
#         await update.message.reply_text(f"❗ Ошибка при обучении: {e}")

# async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     context.user_data.clear()
#     context.user_data['await_check'] = True
#     await update.message.reply_text(
#         "👁️ Пришлите мне фото или видео, и я скажу, кто на нём изображён."
#     )

# # Обработчик для фото/видео в режиме /check
# async def check_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not context.user_data.get('await_check'):
#         await update.message.reply_text(
#             "⚠️ Сначала вызовите команду /check."
#         )
#         return

#     message = update.message
#     user = message.from_user
#     user_id = user.id

#     # Определяем тип входа: фото или видео
#     is_photo = bool(message.photo)
#     is_video = bool(message.video) or (
#         message.document and message.document.mime_type == 'video/mp4'
#     )

#     if not (is_photo or is_video):
#         await message.reply_text("❓ Пришлите фото или видео (MP4).")
#         return

#     # Скачиваем файл
#     if is_photo:
#         file_obj = await message.photo[-1].get_file()  # берём максимальное разрешение
#     else:
#         video_file = message.video or message.document
#         file_obj = await video_file.get_file()

#     # Сохраняем временно
#     ext = 'jpg' if is_photo else 'mp4'
#     tmp_path = f"temp/{user_id}_check.{ext}"
#     os.makedirs("temp", exist_ok=True)
#     await file_obj.download_to_drive(tmp_path)

#     # Сбрасываем флаг
#     context.user_data['await_check'] = False

#     # Если фото — сразу классифицируем
#     if is_photo:
#         result = recognize_image(tmp_path)
#         await message.reply_text(result)
#         os.remove(tmp_path)
#         return

#     # Если видео — разбиваем на кадры и классифицируем несколько
#     cap = cv2.VideoCapture(tmp_path)
#     frame_results = {}
#     frame_idx = 0
#     sample_rate = 5  # каждый 10-й кадр
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         if frame_idx % sample_rate == 0:
#             frame_path = f"temp/{user_id}_frame_{frame_idx:04d}.jpg"
#             cv2.imwrite(frame_path, frame)
#             # вызываем классификатор
#             cls = recognize_image(frame_path)
#             frame_results.setdefault(cls, 0)
#             frame_results[cls] += 1
#             os.remove(frame_path)
#         frame_idx += 1
#     cap.release()
#     os.remove(tmp_path)

#     # Находим наиболее частый результат
#     if frame_results:
#         best = max(frame_results.items(), key=lambda x: x[1])[0]
#         await message.reply_text(f"🔍 В видео чаще всего: {best}")
#     else:
#         await message.reply_text("⚠️ Не удалось извлечь кадры из видео.")



# # Регистрируем хендлеры команд
# app.add_handler(CommandHandler("start", start))
# app.add_handler(CommandHandler("help", help_command))
# app.add_handler(CommandHandler("about", about))
# app.add_handler(CommandHandler("train", train))
# app.add_handler(CommandHandler("cancel", cancel))
# # Локальный хендлер для /bd
# app.add_handler(CommandHandler("bd", bd_command))
# app.add_handler(CommandHandler("check", check_command))


# # Регистрируем хендлер для видео
# video_filter = (
#     filters.VIDEO
#     | (
#         filters.Document.FileExtension("mp4")
#         & filters.Document.MimeType("video/mp4")
#     )
# )
# app.add_handler(MessageHandler(video_filter, handle_video))
# app.add_handler(MessageHandler(filters.PHOTO | video_filter, check_handle))


# # Функция установки команд в меню
# async def setup_commands() -> None:
#     await app.bot.set_my_commands([
#         BotCommand("start", "Запустить бота"),
#         BotCommand("help", "Помощь"),
#         BotCommand("about", "О боте"),
#         BotCommand("bd", "Добавить в базу"),
#         BotCommand("train", "Дообучить модель"),
#         BotCommand("cancel", "Отменить действие"),
#     ])

# # Асинхронная точка входа
# async def main() -> None:
#     await app.initialize()
#     try:
#         await setup_commands()
#         logger.info("Команды установлены")
#     except Exception as e:
#         logger.error(f"Не удалось установить команды: {e}")

#     await app.start()
#     await app.updater.start_polling()
#     logger.info("Бот запущен и принимает обновления")

#     stop_event = asyncio.Event()
#     try:
#         await stop_event.wait()
#     except (KeyboardInterrupt, SystemExit):
#         logger.info("Получен сигнал остановки")

#     await app.updater.stop_polling()
#     await app.stop()
#     logger.info("Бот остановлен")

# if __name__ == "__main__":
#     asyncio.run(main())


import os
import cv2
import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.request import HTTPXRequest

from model_faces.commands import start, help_command, about, cancel
import model_faces.video_handler as video_handler
import model_faces.train_model as train_model
from model_faces.test_model import recognize_image  

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = '8184614570:AAHI5UEqPBKIqp-a8zw_bZAazpaioSsJMz4'

request = HTTPXRequest(connect_timeout=10, read_timeout=60)
app = ApplicationBuilder().token(TOKEN).request(request).build()


# /bd — начинаем процесс добавления видео в базу
async def bd_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data['await_video'] = True
    await update.message.reply_text(
        "Отправь мне видео (10-60 секунд, MP4), где хорошо видно твоё лицо.\n"
        "Через 3-10 минут ты получишь доступ!"
    )


# /check — начинаем процесс распознавания на медиа
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data['await_check'] = True
    await update.message.reply_text(
        "Пришлите мне фото или видео (MP4), и я открою доступ пользователям, если они есть в базе"
    )


# Обработка учебного видео для /bd
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get('await_video'):
        await update.message.reply_text(
            "Используйте команду /bd, чтобы начать процесс добавления в базу."
        )
        return

    user = update.message.from_user
    user_id = user.id
    username = user.username or str(user_id)

    video_file = (
        update.message.video
        or (update.message.document
            if update.message.document and update.message.document.mime_type == 'video/mp4'
            else None)
    )
    if not video_file:
        await update.message.reply_text("Пожалуйста, отправьте видео в формате MP4.")
        return

    # Скачиваем
    file_obj = await video_file.get_file()
    video_bytes = await file_obj.download_as_bytearray()
    video_path = video_handler.save_video(video_bytes, user_id)

    # Сбрасываем флаг
    context.user_data['await_video'] = False

    await update.message.reply_text("Видео получено. Подождите 3-10 минут для добавления в базу")
    frame_count = video_handler.process_video_to_frames(video_path, username)

    await update.message.reply_text("Запускаю дообучение модели…")
    # если есть prepare_data_split, готовим split, иначе используем всю папку
    ds = getattr(video_handler, 'prepare_data_split', lambda d: None)(f"output_frames/{username}")
    train_input = ds or os.path.abspath("output_frames")
    try:
        metrics = train_model.train_model(train_input)
        await update.message.reply_text("Вы добавлены в базу и имеете доступ")
    except Exception as e:
        await update.message.reply_text("Произошла ошибка, пожалуйста, повторите действие.")


# Обработка фото/видео для /check
async def check_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get('await_check'):
        await update.message.reply_text("Сначала вызовите команду /check.")
        return

    user = update.message.from_user
    user_id = user.id

    is_photo = bool(update.message.photo)
    is_video = bool(update.message.video) or (
        update.message.document and update.message.document.mime_type == 'video/mp4'
    )
    if not (is_photo or is_video):
        await update.message.reply_text("Пришлите фото или видео (MP4).")
        return

    # Скачиваем файл
    if is_photo:
        file_obj = await update.message.photo[-1].get_file()
        ext = 'jpg'
    else:
        video_file = update.message.video or update.message.document
        file_obj = await video_file.get_file()
        ext = 'mp4'

    tmp_path = f"temp/{user_id}_check.{ext}"
    os.makedirs("temp", exist_ok=True)
    await file_obj.download_to_drive(tmp_path)

    # Сбрасываем флаг
    context.user_data['await_check'] = False

    # Если фото — одно предсказание
    if is_photo:
        result = recognize_image(tmp_path)
        await update.message.reply_text(result)
        os.remove(tmp_path)
        return

    # Если видео — разбиваем на выборку кадров
    cap = cv2.VideoCapture(tmp_path)
    frame_results = {}
    idx = 0
    sample_rate = 10
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % sample_rate == 0:
            frame_path = f"temp/{user_id}_frame_{idx:04d}.jpg"
            cv2.imwrite(frame_path, frame)
            cls = recognize_image(frame_path)
            frame_results[cls] = frame_results.get(cls, 0) + 1
            os.remove(frame_path)
        idx += 1
    cap.release()
    os.remove(tmp_path)

    if frame_results:
        best = max(frame_results.items(), key=lambda x: x[1])[0]
        await update.message.reply_text(best)
    else:
        await update.message.reply_text("Произошла ошибка, пожалуйста, повторите действие.")


# Внешний маршрутизатор медиа
async def unified_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("await_video"):
        await handle_video(update, context)
    elif context.user_data.get("await_check"):
        await check_handle(update, context)
    else:
        await update.message.reply_text(
            "Сначала используйте команду /bd (добавить в базу) или /check (распознать)."
        )


# Регистрация хендлеров
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("about", about))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CommandHandler("bd", bd_command))
app.add_handler(CommandHandler("check", check_command))

media_filter = (
    filters.PHOTO |
    filters.VIDEO |
    (
        filters.Document.FileExtension("mp4") &
        filters.Document.MimeType("video/mp4")
    )
)
app.add_handler(MessageHandler(media_filter, unified_media_handler))


async def setup_commands() -> None:
    await app.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Помощь"),
        BotCommand("about", "О боте"),
        BotCommand("bd", "Добавить в базу"),
        BotCommand("check", "Распознать на медиа"),
        BotCommand("cancel", "Отменить действие"),
    ])


async def main() -> None:
    await app.initialize()
    try:
        await setup_commands()
        logger.info("Команды установлены")
    except Exception as e:
        logger.error(f"Не удалось установить команды: {e}")

    await app.start()
    await app.updater.start_polling()
    logger.info("Бот запущен и принимает обновления")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Получен сигнал остановки")

    await app.updater.stop_polling()
    await app.stop()
    logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
