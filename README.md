# Habit Tracker Backend

Django REST API для трекера привычек с интеграцией Kafka и ClickHouse.

## Требования

- Python 3.13
- Docker и Docker Compose
- uv (менеджер пакетов)

## Быстрый старт

### 1. Запуск инфраструктуры (Kafka, ClickHouse, Zookeeper)

```bash
docker compose -f docker-compose.infra.yml up -d
```

Проверка статуса контейнеров:

```bash
docker compose -f docker-compose.infra.yml ps
```

### 2. Установка зависимостей

```bash
uv sync
```

### 3. Применение миграций

```bash
uv run python manage.py migrate
```

### 4. Запуск Kafka consumer (в отдельном терминале)

```bash
uv run python manage.py consume_kafka
```

### 5. Запуск Django сервера

```bash
uv run python manage.py runserver
```

Сервер доступен по адресу: http://localhost:8000

## API Документация

Swagger UI: http://localhost:8000/api-v1/docs/swagger/

Schema: http://localhost:8000/api-v1/schema/

## Основные эндпоинты

### Привычки

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /api-v1/habit/ | Список привычек |
| POST | /api-v1/habit/ | Создание привычки |
| POST | /api-v1/habit/{id}/checkin/ | Отметка выполнения |

### Аутентификация

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api-v1/auth/token/ | Получение токена |
| POST | /api-v1/auth/token/refresh/ | Обновление токена |

## Проверка функциональности

### 1. Создание привычки

```bash
curl -X POST http://localhost:8000/api-v1/habit/ \
  -H "Content-Type: application/vnd.api+json" \
  -H "Accept: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "habit",
      "attributes": {
        "name": "Почистить зубы",
        "description": "Утренняя привычка",
        "targetStreak": 21
      }
    }
  }'
```

### 2. Отметка выполнения (checkin)

```bash
curl -X POST http://localhost:8000/api-v1/habit/1/checkin/ \
  -H "Content-Type: application/vnd.api+json" \
  -H "Accept: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "habitViewSet",
      "attributes": {
        "note": "Выполнено",
        "mood": "good"
      }
    }
  }'
```

### 3. Проверка данных в ClickHouse

Просмотр событий:

```bash
docker exec clickhouse clickhouse-client --query \
  "SELECT * FROM habit_tracker.habit_events ORDER BY timestamp DESC LIMIT 10" \
  --password "your_password"
```

Количество событий:

```bash
docker exec clickhouse clickhouse-client --query \
  "SELECT COUNT(*) FROM habit_tracker.habit_events" \
  --password "your_password"
```

События по пользователям:

```bash
docker exec clickhouse clickhouse-client --query \
  "SELECT user_id, COUNT(*) as events FROM habit_tracker.habit_events GROUP BY user_id" \
  --password "your_password"
```

### 4. Проверка топиков Kafka

```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

Просмотр сообщений в топике:

```bash
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic habit.completed --from-beginning --timeout-ms 5000
```

## Веб-интерфейсы

| Сервис | URL | Логин/Пароль |
|--------|-----|--------------|
| Swagger UI | http://localhost:8000/api-v1/docs/swagger/ | - |
| ClickHouse UI | http://localhost:8978/ | admin / admin |

## Остановка инфраструктуры

```bash
docker compose -f docker-compose.infra.yml down
```

Остановка с удалением данных:

```bash
docker compose -f docker-compose.infra.yml down -v
```

## Структура проекта

```
backend/
├── account/          # Приложение пользователей и аутентификации
├── analytics/        # Kafka consumer и ClickHouse интеграция
├── habit/            # Приложение привычек
├── config/           # Настройки Django
├── docker-compose.infra.yml
└── manage.py
```

## Переменные окружения

Основные переменные в `.env`:

```
SECRET_KEY=...
DEBUG=True
ALLOWED_HOSTS=

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_URL=redis://localhost:6379/0

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DATABASE=habit_tracker

# Email
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

## Поток данных

1. Пользователь отправляет POST запрос на `/api-v1/habit/{id}/checkin/`
2. Django создаёт запись в HabitLog и обновляет статистику привычки
3. Событие отправляется в Kafka топик `habit.completed`
4. Kafka consumer (`consume_kafka`) получает сообщение
5. Consumer преобразует данные и вставляет в ClickHouse таблицу `habit_events`
6. Данные доступны для аналитики через ClickHouse
