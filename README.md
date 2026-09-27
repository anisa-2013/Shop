# Shop API — дипломный проект

Backend интернет-магазина на Django и Django REST Framework. Каталог открыт всем; корзина и заказы доступны по JWT. Товары, категории и статусы заказов управляются через Django Admin.

## Локальный запуск

Требуется Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Создайте переменные окружения по `.env.example` (файл `.env` сам по себе не загружается; экспортируйте значения в оболочку). Для локального запуска достаточно `SECRET_KEY` и `DEBUG=True`; без `DATABASE_URL` используется SQLite.

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Добавьте категории и товары в `/admin/`. Документация: `/api/docs/`, схема: `/api/schema/`.

## Эндпоинты

| Метод | URL | Описание |
| --- | --- | --- |
| POST | /api/auth/register/ | Регистрация: username, email, password |
| POST | /api/auth/login/ | JWT: username, password |
| POST | /api/auth/refresh/ | Обновление access token |
| GET, PUT, PATCH | /api/profile/ | Свой профиль |
| GET | /api/categories/ | Категории |
| GET | /api/products/?search=...&category=1&page=1 | Товары |
| GET | /api/products/1/ | Товар |
| GET | /api/cart/ | Корзина и сумма |
| POST | /api/cart/items/ | Добавить: product, quantity |
| PATCH, DELETE | /api/cart/items/1/ | Изменить количество или удалить |
| GET, POST | /api/orders/ | Свои заказы или оформить корзину |
| GET | /api/orders/1/ | Свой заказ |

Передавайте `Authorization: Bearer <access>` для защищённых методов. POST `/api/orders/` не требует тела. При оформлении остатки уменьшаются, цены фиксируются в заказе, корзина очищается. Пустая корзина и недостаточный остаток дают HTTP 400.

## Render

В корне есть `render.yaml`: создайте Blueprint из GitHub-репозитория. Он создаст веб-сервис и PostgreSQL, сгенерирует `SECRET_KEY`, выполнит миграции. После создания задайте в панели Render переменную `CSRF_TRUSTED_ORIGINS=https://<ваш-домен>.onrender.com`, создайте администратора командой `python manage.py createsuperuser` в shell сервиса и откройте `/api/docs/`.

Локальные загруженные изображения (`ImageField`) не сохраняются постоянно на стандартной файловой системе Render: для постоянной работы изображений понадобится внешнее файловое хранилище. Все остальные функции API работают без изображений.

## Проверка

```bash
python manage.py test
```
