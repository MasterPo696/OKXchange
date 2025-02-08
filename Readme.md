# Order Book Updater

Этот проект подписывается на торговые пары OKX, обновляет стаканы ордеров и кеширует данные в Memcached.

## Структура проекта

```
├── app/                # Основная логика приложения
|    ├── config.py      # Настройки проекта
|    ├── api.py         # API для получения данных
|    ├── main.py        # Точка входа в приложение
|    ├── server.py      # endpoints для сервера
├── requirements.txt    # Список зависимостей
├── docker-compose.yml  # Конфигурация Docker Compose
├── Dockerfile          # Docker-образ
├── .env                # Файл с переменными окружения
└── README.md           # Документация
```

## Настройка окружения

### Установка зависимостей

1. **Создайте виртуальное окружение:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   venv\Scripts\activate  # Для Windows
   ```

2. **Установите зависимости:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Создайте `.env` файл** (пример структуры):
   ```ini
   MEMCACHE_HOST=memcached
   MEMCACHE_PORT=11211
   ```

## Запуск проекта

### Локальный запуск

```sh
python main.py
```

### Проверка работоспособности

- В логе должны появиться строки о подписке на торговые пары.
- Для проверки кеша можно использовать `telnet`:
  ```sh
  telnet localhost 11211
  get <inst_id>
  ```

## Запуск в Docker

### 1. Сборка и запуск контейнеров

```sh
docker-compose up --build
```

### 2. Остановка контейнеров

```sh
docker-compose down
```

## Dockerfile

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: order_book_updater
    depends_on:
      - memcached
    env_file:
      - .env
    ports:
      - "8000:8000"

  memcached:
    image: memcached:latest
    container_name: memcached
    ports:
      - "11211:11211"
```


## Для тестов запустить

```sh
curl http://localhost:8000/orderbooks/ZIL-USDT
curl http://localhost:8000/pretty/ZIL-USDT
curl http://localhost:8000/clear
```


