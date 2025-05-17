import os
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from typing import List, Tuple, Dict

class ThermalProcessor:
    def __init__(self):
        # Пути и параметры модели
        self.model_path = str(Path(__file__).parent / "best_thermal.pt")
        self.MIN_CONFIDENCE = 0.4  # Порог уверенности (50%)
        self.MIN_DETECTION_TIME = 1.00  # Минимальное время детекции (сек)
        
        # Классы объектов   
        self.class_names = {
            0: 'car',
            1: 'animals', 
            2: 'people'
        }
        
        # Цвета для разных классов (BGR)
        self.class_colors = {
            0: (0, 255, 0),    # Человек - зеленый
            1: (0, 0, 255),    # Животное - красный
            2: (255, 0, 0)     # Машина - синий
        }
        
        # Загрузка модели
        self._verify_model_file()
        self.model = YOLO(self.model_path)
    
    def _verify_model_file(self):
        """Проверяет наличие файла модели"""
        if not os.path.exists(self.model_path):
            available_files = "\n".join(os.listdir(Path(__file__).parent))
            raise FileNotFoundError(
                f"Файл модели не найден по пути: {self.model_path}\n"
                f"Доступные файлы:\n{available_files}"
            )

    async def process_video(self, video_path: str) -> List[List[Tuple[int, float, Tuple[int, int, int, int]]]]:
        """Обрабатывает видео и возвращает детекции по кадрам"""
        cap = cv2.VideoCapture(video_path)
        detections = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Детекция объектов
            results = self.model(frame, verbose=False)
            frame_dets = []
            
            for box in results[0].boxes:
                if box.conf.item() < self.MIN_CONFIDENCE:
                    continue
                    
                cls_id = int(box.cls.item())
                bbox = [
                    int(box.xyxy[0][0].item()),
                    int(box.xyxy[0][1].item()),
                    int(box.xyxy[0][2].item()),
                    int(box.xyxy[0][3].item())
                ]
                frame_dets.append((cls_id, box.conf.item(), bbox))
            
            detections.append(frame_dets)
        
        cap.release()
        return detections
    
    async def process_and_visualize_video(self, input_path: str, output_path: str) -> str:
        """
        Обрабатывает видео, рисует bounding boxes и сохраняет результат
        Возвращает путь к обработанному видео
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Не удалось открыть видеофайл: {input_path}")
        
        # Получаем параметры видео
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Создаем VideoWriter для сохранения результата
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Детекция объектов
            results = self.model(frame, verbose=False)
            
            # Отрисовка bounding boxes
            for box in results[0].boxes:
                if box.conf.item() < self.MIN_CONFIDENCE:
                    continue
                    
                cls_id = int(box.cls.item())
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                color = self.class_colors.get(cls_id, (255, 255, 255))
                
                # Рисуем прямоугольник
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                
                # Добавляем текст с классом и уверенностью
                label = f"{self.class_names.get(cls_id, 'unknown')} {box.conf.item():.2f}"
                cv2.putText(frame, label, (bbox[0], bbox[1]-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            out.write(frame)
            frame_count += 1
        
        cap.release()
        out.release()
        
        # Проверяем, что видео было сохранено
        if frame_count == 0:
            raise ValueError("Не удалось обработать ни одного кадра")
            
        return output_path
    
    def analyze_detections(self, detections: list, fps: float) -> dict:
        """Анализирует и группирует детекции"""
        objects = {}
        min_frames = self.MIN_DETECTION_TIME * fps
        
        for frame_idx, frame_dets in enumerate(detections):
            for det in frame_dets:
                cls_id, conf, bbox = det
                
                # Поиск совпадений с предыдущими объектами
                matched = False
                for obj_id, obj in objects.items():
                    if self._check_overlap(bbox, obj['last_bbox']):
                        obj['last_bbox'] = bbox
                        obj['frames'].append(frame_idx)
                        matched = True
                        break
                
                if not matched:
                    obj_id = len(objects) + 1
                    objects[obj_id] = {
                        'class': cls_id,
                        'first_frame': frame_idx,
                        'last_bbox': bbox,
                        'frames': [frame_idx]
                    }
        
        # Фильтрация по минимальному времени
        return {k: v for k, v in objects.items() 
                if len(v['frames']) >= min_frames}
    
    def _check_overlap(self, box1: list, box2: list, threshold: float = 0.5) -> bool:
        """Проверяет перекрытие bounding box'ов"""
        # Расчет площади пересечения
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])
        
        if x_right < x_left or y_bottom < y_top:
            return False
            
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        return intersection / min(area1, area2) >= threshold
    
    def generate_report(self, objects: dict, fps: float) -> str:
        """Генерирует текстовый отчет по обнаруженным объектам"""
        if not objects:
            return "🔍 Объекты не обнаружены или время детекции слишком короткое."
        
        # Группировка по классам
        stats = {}
        for obj_id, obj in objects.items():
            cls_name = self.class_names.get(obj['class'], 'неизвестный')
            if cls_name not in stats:
                stats[cls_name] = []
                
            duration = len(obj['frames']) / fps
            start_time = obj['frames'][0] / fps
            end_time = obj['frames'][-1] / fps
            stats[cls_name].append((start_time, end_time, duration))
        
        # Формирование отчета
        report = ["📊 Результаты анализа тепловизионного видео:"]
        
        for cls_name, items in stats.items():
            report.append(f"\n🔹 {cls_name.capitalize()}: {len(items)} объектов")
            total_time = sum(item[2] for item in items)
            report.append(f"   Общее время в кадре: {total_time:.1f} сек")
            
            for i, (start, end, dur) in enumerate(items, 1):
                report.append(f"   {i}. с {start:.1f} до {end:.1f} сек ({dur:.1f} сек)")
        
        return "\n".join(report)