# Используем официальный образ Python 3.12.3 в качестве базового образа
FROM python:3.12.3-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /PhishTest

# Копируем файлы requirements.txt и Dockerfile в рабочую директорию
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Nginx
RUN apt-get update && apt-get install -y nginx

# Копируем остальные файлы проекта в рабочую директорию
COPY . .

# Копируем конфигурационный файл Nginx
COPY nginx.conf /etc/nginx/sites-available/default

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DEBUG=1
ENV DATABASE_URL=postgres://postgres:admin@db:5432/mydatabase
ENV PYTHONPATH="/PhishTest/phishtest"
ENV CSRF_TRUSTED_ORIGINS=http://localhost:8080
# Запускаем сервер разработки Django и Nginx
CMD ["sh", "-c", "gunicorn phishtest.phishtest.wsgi:application --bind 0.0.0.0:8000 & nginx -g 'daemon off;'"]