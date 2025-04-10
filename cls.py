def main():    
    from ultralytics import YOLO

    # Загрузка модели классификации
    model = YOLO('yolo11x-cls.pt')

    # Обучение модели
    model.train(
        data=r'C:\Users\User\faces_dark\dataset_split',  
        epochs=5,                # Кол-во эпох
        imgsz=224,                # Размер изображений
        batch=4,                 # Размер батча
        workers=4,                # Кол-во потоков
        device=0,
        save = True,
        save_period = 1,
        plots = True,
        save_dir = 'res_cls'
    )

    # Валидация на валидационном наборе
    metrics = model.val()

    # Выводим метрики
    print("Результаты валидации:")
    print(metrics)


if __name__ == '__main__':
    main()