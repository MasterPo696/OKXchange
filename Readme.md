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

## Для тестов запустить

```sh
curl http://localhost:8000/orderbooks/ZIL-USDT
curl http://localhost:8000/pretty/ZIL-USDT
curl http://localhost:8000/clear
```


