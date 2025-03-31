from ultralytics import YOLO

# Загрузка предобученной модели YOLOv8 (можно выбрать nano, small, medium, large, xlarge)
# model = YOLO("yolov8n.pt")  # yolov8n.pt, yolov8s.pt и т.д.

# # Обучение модели
# results = model.train(
#     data="data.yaml",  # путь к файлу конфигурации YAML
#     epochs=100,               # количество эпох
#     batch=16,                # размер батча (зависит от GPU)
#     imgsz=640,               # размер изображения
#     device="0",              # "0" для GPU, "cpu" для CPU
#     name="yolov8_train",     # название эксперимента
#     optimizer="auto",        # автоматический выбор (Adam/SGD)
#     lr0=0.01,                # начальный learning rate
#     lrf=0.01,                # конечный learning rate
#     weight_decay=0.0005,     # вес decay
#     dropout=0.0,             # dropout (только для больших моделей)
#     patience=50,             # ранняя остановка, если нет улучшений
# )

# # Экспорт модели в нужный формат (опционально)
# model.export(format="onnx")  # можно выбрать torchscript, tensorrt и др.


# Загрузка обученной модели
model = YOLO("/home/serv1/CURSACH/detect_people/dataset/runs/detect/yolov8_train4/weights/best.pt")  # путь к вашим весам

# Предсказание на изображении
results = model.predict(
    source="test2.mp4",       # путь к изображению
    conf=0.5,               # порог уверенности
    save=True,              # сохранить результат
    show=True,              # показать результат
    show_labels=True,       # показать метки
    show_conf=True          # показать уверенность
)