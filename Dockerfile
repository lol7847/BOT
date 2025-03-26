# Используем официальный Python образ
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы из текущей директории в рабочую директорию контейнера
COPY . /app

# Устанавливаем зависимости из файла requirements.txt (если он есть)
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска основного файла проекта (если это Python-скрипт, например, main.py или другой файл)
CMD ["python", "TRAFFIC.py"]
