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

Установка компонентов и их запуск:

1. Клонирование репозитория
```bash
git clone https://github.com/Dead0End/foodgram.git

2. Настройка переменных окружения
Создайте файл .env в корне проекта со следующими данными:
DJANGO_SECRET_KEY=Секретный_ключ_Джанго
DB_ENGINE=Движок_базы_данных
POSTGRES_DB=Название_приложения
POSTGRES_USER=Юзер_приложения
POSTGRES_PASSWORD=Пароль_Юзера
DB_HOST=Имя_БД
DB_PORT=5432
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=Домен_вашего_сайта, IP_виртуальной_машины
CSRF_TRUSTED_ORIGINS=Домен_вашего_сайта

3. Сборка и запуск Docker-образов
```bash
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
https://defoodgram.zapto.org/
8. Тестирование
Примеры запросов и тесты доступны и производятся в коллекции Postman: postman_collection/foodgram.postman_collection.json

Автор: Вольф Максим
GitHub: https://github.com/Dead0End