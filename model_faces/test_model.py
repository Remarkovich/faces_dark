import os
from ultralytics import YOLO

# Загрузка дообученной модели
MODEL_PATH = 'res_cls/best.pt'
model = YOLO(MODEL_PATH)

def recognize_image(image_path: str, imgsz: int = 224) -> str:
    """
    Классифицирует изображение и возвращает имя класса с наивысшей вероятностью и уверенность.
    """
    results = model.predict(source=image_path, imgsz=imgsz)[0]

    # У индекса топ-1 хранится атрибут top1, уверенность — top1conf
    idx = int(results.probs.top1)           # индекс класса
    conf = float(results.probs.top1conf)    # уверенность
    name = results.names[idx]               # имя класса
    if conf > 0.99:
        return f"Доступ открыт для пользователя {name}"
    else:
        return "Доступ закрыт. Пользователя нет в базе"