import os
from dotenv import load_dotenv
from yandex_tracker_client import TrackerClient
import json
from datetime import datetime

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение начальной метки времени
start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Функция для логирования без метки времени
def log_message(message):
    print(message)  # Вывод в консоль
    with open('app.log', 'a', encoding='utf-8') as log_file:
        log_file.write(message + '\n')

# Запись начальной строки с временем выполнения
time_entry = f"Время выполнения [{start_timestamp}] \n"
print(time_entry)  # Вывод в консоль
with open('app.log', 'a', encoding='utf-8') as log_file:
    log_file.write(time_entry + '\n')

# Получение токенов и параметров из .env
token = os.getenv('YANDEX_TRACKER_TOKEN')
org_id = os.getenv('YA_TRACKER_ORG_ID')
filter_query = os.getenv('FILTER_QUERY')
names_str = os.getenv('names')

# Парсинг массива names из строки JSON
names = json.loads(names_str)

# Инициализация клиента Yandex Tracker
client = TrackerClient(token=token, org_id=org_id)

# Получение списка задач по фильтру
issues = client.issues.find(filter_query)

# Функция для нормализации имени (Имя + Фамилия)
def normalize_name(full_name):
    parts = full_name.split()
    if len(parts) >= 3:
        return f"{parts[0]} {parts[2]}"  # Имя + Фамилия
    else:
        return full_name

# Сбор исполнителей из задач
assignees = []
for issue in issues:
    if issue.assignee:
        assignees.append(issue.assignee.display)

# Группировка исполнителей и подсчет количества с нормализацией
assignee_counts = {}
for assignee in assignees:
    normalized = normalize_name(assignee)
    assignee_counts[normalized] = assignee_counts.get(normalized, 0) + 1

# Подсчет задач без исполнителя
unassigned_count = sum(1 for issue in issues if not issue.assignee)

# Вывод сгруппированных исполнителей
log_message("Фиксы за сутки сделали:")
for assignee, count in assignee_counts.items():
    log_message(f"{assignee} = {count}")

# Вывод общего количества задач
log_message(f"\nОбщее количество задач: {len(assignees)}")

# Вывод задач без исполнителя
log_message(f"\nЗакрыто без исполнителя (дубликаты, не воспроизводится): {unassigned_count}")

# Поиск по массиву names и вывод результатов, отсортированных по убыванию count
log_message("\nОбщий список всех исполнителей:")
results = [(name, assignee_counts.get(name, 0)) for name in names]
results.sort(key=lambda x: x[1], reverse=True)
for i, (name, count) in enumerate(results, 1):
    log_message(f"{i}. {name}: {count}")
log_message(60*"*")