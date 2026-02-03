FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости для работы с Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt


# По умолчанию запускаем приложение, но compose переопределит это для тестов
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]