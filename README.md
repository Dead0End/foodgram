Foodgram — Сайт для публикации и распространения рецептов

Задействовано:
Python 3.10,
Django,
DRF (Django Rest Framework),
PostgreSQL
Docker,
Docker Compose,
Nginx,
Djoser,
Установка компонентов и их запуск
1. Клонирование репозитория
git clone https://github.com/Dead0End/foodgram.git

2. Настройка переменных окружения
Создайте файл .env в корне проекта со следующими данными:
DJANGO_SECRET_KEY=123
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_user_password
DB_HOST=db
DB_PORT=5432
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=deadendfoodgram.zapto.org, 51.250.98.7, localhost, 127.0.0.1
CSRF_TRUSTED_ORIGINS=http://deadendfoodgram.zapto.org

3. Сборка и запуск Docker-образов
docker-compose down && docker-compose up --build
4. Выполните миграции,
docker-compose exec backend python manage.py migrate
5. Загрузите ингредиенты, и теги
docker-compose exec backend python manage.py import_ingredients
docker-compose exec backend python manage.py import_tags
6.соберите статику и создайте суперпользователя
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py createsuperuser
7. Приложения:
https://deadendfoodgram.zapto.org/
8. Тестирование
Примеры запросов и тесты доступны и производятся в коллекции Postman: postman_collection/foodgram.postman_collection.json