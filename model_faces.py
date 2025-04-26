import torch
import torchvision.transforms as transforms
import cv2
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Загрузка твоей классификационной модели YOLOv11
model = torch.load('best.pt')
model.eval()

# Трансформации, такие как использовались при обучении
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Классы
classes = [alena, igor, egor]  # замените на свои классы

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    video_path = "temp_video.mp4"
    await file.download_to_drive(video_path)

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    results_counter = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % 9 == 0:
            input_tensor = transform(frame).unsqueeze(0)
            with torch.no_grad():
                outputs = model(input_tensor)
                _, predicted = torch.max(outputs, 1)
                label = classes[predicted.item()]
                results_counter[label] = results_counter.get(label, 0) + 1
        frame_count += 1

    cap.release()
    os.remove(video_path)

    if results_counter:
        sorted_results = sorted(results_counter.items(), key=lambda x: x[1], reverse=True)
        response = "На видео чаще всего встречались:\n"
        for label, count in sorted_results[:3]:
            response += f"— {label} ({count} раз)\n"
    else:
        response = "Не удалось определить объекты на видео."

    await update.message.reply_text(response)

# Запуск бота
app = ApplicationBuilder().token("8184614570:AAHI5UEqPBKIqp-a8zw_bZAazpaioSsJMz4").build()
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.run_polling()
