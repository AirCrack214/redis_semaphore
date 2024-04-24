# DistributedSemaphore

#### Установка
Установка redis на ubuntu 
```sh
sudo apt update
sudo apt install redis-server
sudo nano /etc/redis/redis.conf
```

Внутри конфига требуется определить следующую строку 
```sh
supervised systemd
```
После чего перезагрузить redis с новыми настройками
```sh
sudo systemctl restart redis.service
```

Библиотеки Python >=3.11
```sh
pip install asyncio redis requests pytest
```

Запуск тестов
```sh
pytest tests.py
```

Запуск приложения
```sh
python semaphore_app.py
```

#### Приложение (semaphore_app.py)
Скрипт имитирует асинхронную обработку потока запросов к API для, например, параллельной записи ответов в файл/таблицу. Конфигурация:
- api_requests - количество отправляемых запросов к API
- semaphore_limit - ограничение на количество параллельных задач в семафоре
- url - адрес отправки запросов

В зависимости от соотношения кол-ва запросов и ограничения параллельности семафоре будет получено разное время исполнения
```sh
(.venv) global_user@bots:~/redis_db$ python semaphore_app.py
2024-04-24 17:54:05 INFO: DistributedSemaphore API requests process started
2024-04-24 17:54:06 INFO: Handled api request №4 with status code 200
2024-04-24 17:54:06 INFO: Handled api request №1 with status code 200
2024-04-24 17:54:06 INFO: Handled api request №2 with status code 200
2024-04-24 17:54:06 INFO: Handled api request №3 with status code 200
2024-04-24 17:54:06 INFO: Handled api request №5 with status code 200
2024-04-24 17:54:06 INFO: DistributedSemaphore takes ~0.5687 seconds to handle 5 with 1 bounded limit
```
```sh
(.venv) global_user@bots:~/redis_db$ python semaphore_app.py
2024-04-24 17:54:12 INFO: DistributedSemaphore API requests process started
2024-04-24 17:54:12 INFO: Handled api request №1 with status code 200
2024-04-24 17:54:12 INFO: Handled api request №3 with status code 200
2024-04-24 17:54:12 INFO: Handled api request №4 with status code 200
2024-04-24 17:54:12 INFO: Handled api request №2 with status code 200
2024-04-24 17:54:12 INFO: Handled api request №5 with status code 200
2024-04-24 17:54:12 INFO: DistributedSemaphore takes ~0.2214 seconds to handle 5 with 5 bounded limit
```

#### Тесты (tests.py)
- test_successful_redis_connection - проверка соединения с redis
- test_lock - проверка acquire метода семафора
- test_with - проверка исполнения функции с помощью семафора 
- test_create_with_existing - проверка запуска семафора при наличии уже запущенного
- test_acquire_without_connection - проверка работы при сбое соединения