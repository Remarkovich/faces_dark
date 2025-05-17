import os
import cv2
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from thermal_processor import ThermalProcessor

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ThermalBot:
    def __init__(self, token: str):
        self.token = token
        self.processor = ThermalProcessor()
        self.commands = [
            ("start", "Начать работу с ботом"),
            ("help", "Показать справку по командам"),
            ("analyze", "Анализ тепловизионного видео"),
            ("settings", "Настройки детекции"),
            ("feedback", "Оставить отзыв")
        ]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start с клавиатурой команд"""
        commands_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in self.commands])
        
        welcome_text = (
            "🔭 *Тепловизионный анализатор* 🔍\n\n"
            "Я могу анализировать видео с тепловизора и обнаруживать:\n"
            "• Людей 👤\n• Животных 🐾\n• Технику 🚗\n\n"
            "*Доступные команды:*\n"
            f"{commands_list}\n\n"
            "Отправьте /analyze для начала анализа видео."
        )
        
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=self._create_keyboard()
        )
    
    def _create_keyboard(self):
        """Создает ReplyKeyboardMarkup с основными командами"""
        from telegram import ReplyKeyboardMarkup
        keyboard = [
            ["/analyze", "/help"],
            ["/settings", "/feedback"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help с подробным описанием"""
        help_text = (
            "📚 *Справка по командам*\n\n"
            "*/start* - Главное меню с кратким описанием\n"
            "*/analyze* - Анализ видео с тепловизора\n"
            "   _Отправьте видео, и вы получите:_\n"
            "   - Видео с выделенными объектами\n"
            "   - Отчет о времени нахождения объектов\n"
            "*/settings* - Настройки параметров детекции\n"
            "   - Порог уверенности\n"
            "   - Минимальное время детекции\n"
            "*/feedback* - Оставить отзыв о работе бота\n\n"
            "Просто отправьте мне видео в ответ на /analyze!"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def analyze_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /analyze"""
        context.user_data['awaiting_video'] = True
        await update.message.reply_text(
            "📹 *Как использовать:*\n\n"
            "1. Снимите видео на тепловизоре (10-60 сек)\n"
            "2. Отправьте его мне в ответ на это сообщение\n"
            "3. Дождитесь обработки (обычно 1-3 минуты)\n\n"
            "Вы получите:\n"
            "✅ Видео с выделенными объектами\n"
            "✅ Подробный отчет по времени\n\n"
            "⚠️ Поддерживаются форматы: MP4, MOV, AVI",
            parse_mode="Markdown"
        )
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка полученного видео"""
        if not context.user_data.get('awaiting_video'):
            await update.message.reply_text(
                "ℹ️ Сначала используйте команду /analyze",
                reply_markup=self._create_keyboard()
            )
            return
            
        # Проверка типа файла
        video_file = update.message.video or update.message.document
        if not video_file:
            await update.message.reply_text(
                "❌ Пожалуйста, отправьте видеофайл",
                reply_markup=self._create_keyboard()
            )
            return
            
        # Создание временных файлов
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        user_id = update.message.from_user.id
        input_path = os.path.join(temp_dir, f"thermal_{user_id}_input.mp4")
        output_path = os.path.join(temp_dir, f"thermal_{user_id}_output.mp4")
        
        # Скачивание файла
        file = await video_file.get_file()
        await file.download_to_drive(input_path)
        
        # Уведомление о начале обработки
        processing_msg = await update.message.reply_text(
            "🔍 *Анализ начат*\n\n"
            "Этапы обработки:\n"
            "1. Детекция объектов...\n"
            "2. Анализ времени...\n"
            "3. Генерация отчета...\n\n"
            "Это займет 1-3 минуты ⏳",
            parse_mode="Markdown"
        )
        
        try:
            # Обработка видео с визуализацией
            processed_path = await self.processor.process_and_visualize_video(input_path, output_path)
            
            # Получение FPS для анализа
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # Текстовый отчет
            detections = await self.processor.process_video(input_path)
            objects = self.processor.analyze_detections(detections, fps)
            report = self.processor.generate_report(objects, fps)
            
            # Отправка результата
            with open(processed_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"📊 *Результаты анализа*\n\n{report}",
                    parse_mode="Markdown",
                    supports_streaming=True,
                    reply_markup=self._create_keyboard()
                )
            
            # Удаление сообщения о процессе
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки видео: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ *Ошибка обработки видео*\n\n"
                "Попробуйте:\n"
                "1. Отправить видео короче 1 минуты\n"
                "2. Проверить формат (MP4 лучше всего)\n"
                "3. Попробовать позже\n\n"
                "Техническая информация:\n"
                f"`{str(e)[:200]}`",
                parse_mode="Markdown",
                reply_markup=self._create_keyboard()
            )
        finally:
            # Очистка временных файлов
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    os.remove(path)
            context.user_data.pop('awaiting_video', None)
    
    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик настроек"""
        current_settings = (
            "⚙️ *Текущие настройки*\n\n"
            f"Порог уверенности: {self.processor.MIN_CONFIDENCE}\n"
            f"Мин. время детекции: {self.processor.MIN_DETECTION_TIME} сек\n\n"
            "Используйте:\n"
            "/set_confidence 0.7\n"
            "/set_min_time 2.5"
        )
        await update.message.reply_text(
            current_settings,
            parse_mode="Markdown",
            reply_markup=self._create_keyboard()
        )
    
    async def feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обратной связи"""
        await update.message.reply_text(
            "💡 *Оставьте отзыв*\n\n"
            "Напишите ваши предложения или сообщите о проблемах. "
            "Разработчик получит ваше сообщение и обязательно ответит!",
            parse_mode="Markdown",
            reply_markup=self._create_keyboard()
        )
    
    async def setup_commands(self, application):
        """Установка команд меню бота"""
        commands = [
            BotCommand(cmd, desc) for cmd, desc in self.commands
        ]
        await application.bot.set_my_commands(commands)
    
    def run(self):
        """Запуск бота"""
        app = ApplicationBuilder().token(self.token).post_init(self.setup_commands).build()
        
        # Регистрация обработчиков
        app.add_handlers([
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            CommandHandler("analyze", self.analyze_video),
            CommandHandler("settings", self.settings),
            CommandHandler("feedback", self.feedback),
            MessageHandler(
                filters.VIDEO | (filters.Document.MimeType("video/mp4")),
                self.handle_video
            )
        ])
        
        # Запуск
        app.run_polling()

if __name__ == "__main__":
    bot = ThermalBot("7163110414:AAFN2tf0ATkeh85uzD3S_6dZQEu41j-kEEs")
    bot.run()