# TeamFinder

TeamFinder — Django-приложение для поиска проектов и участников. Пользователь может зарегистрироваться, заполнить профиль, указать GitHub, создать проект, присоединиться к чужому проекту и добавить проекту необходимые навыки.

## Автор

Владислав — [grayscalestocks@gmail.com](https://github.com/crucifiedshepherd)

## Техно-стек

- Python 3
- Django
- PostgreSQL
- Docker Compose
- HTML, CSS, JavaScript
- pytest
- flake8

## Что реализовано

- регистрация и вход по email;
- профиль пользователя с телефоном, GitHub-ссылкой и аватаром;
- список участников с пагинацией;
- создание, редактирование и завершение проектов;
- список проектов с пагинацией и фильтром по навыку;
- добавление и удаление навыков проекта через AJAX;
- демонстрационные данные через management-команду `populate_demo`.

## Запуск проекта

1. Клонировать репозиторий:

   ```bash
   git clone <ссылка-на-репозиторий>
   ```

2. Перейти в папку проекта:

   ```bash
   cd team-finder-ad-main
   ```

3. Создать и активировать виртуальное окружение:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   Для Windows PowerShell:

   ```bash
   venv\Scripts\Activate.ps1
   ```

4. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. Создать `.env` из примера:

   ```bash
   cp .env_example .env
   ```

6. Проверить значения в `.env`:

   ```env
   DJANGO_SECRET_KEY=change_for_safety
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]

   POSTGRES_DB=team_finder
   POSTGRES_USER=team_finder
   POSTGRES_PASSWORD=team_finder
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5436
   ```

7. Запустить PostgreSQL в Docker:

   ```bash
   docker compose up -d
   ```

8. Применить миграции:

   ```bash
   python manage.py migrate
   ```

9. Создать администратора:

   ```bash
   python manage.py createsuperuser
   ```

10. Заполнить базу демонстрационными данными:

    ```bash
    python manage.py populate_demo
    ```

11. Запустить сервер разработки:

    ```bash
    python manage.py runserver
    ```

После запуска сайт доступен на главной странице: [http://localhost:8000/](http://localhost:8000/).

Админка доступна по адресу: [http://localhost:8000/admin/](http://localhost:8000/admin/). Для входа используйте данные суперпользователя, созданного командой `createsuperuser`.

Чтобы остановить контейнер с PostgreSQL:

```bash
docker compose down
```

## Переменные окружения

| Переменная | Назначение |
|---|---|
| `DJANGO_SECRET_KEY` | Секретный ключ Django. Для локального запуска есть значение по умолчанию, но для реального окружения нужен свой ключ. |
| `DJANGO_DEBUG` | Режим отладки: `True` для разработки, `False` для продакшена. |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты через запятую. По умолчанию: `localhost,127.0.0.1,[::1]`. |
| `POSTGRES_DB` | Имя базы данных PostgreSQL. |
| `POSTGRES_USER` | Пользователь PostgreSQL. |
| `POSTGRES_PASSWORD` | Пароль пользователя PostgreSQL. |
| `POSTGRES_HOST` | Хост базы данных. Для локального запуска обычно `localhost`. |
| `POSTGRES_PORT` | Порт PostgreSQL. В `docker-compose.yml` используется `5436`. |

## Тестовые аккаунты

После выполнения команды `populate_demo` доступны пользователи с паролем `password123`:

| Email | Пользователь | Проект |
|---|---|---|
| `anna.volkova@example.com` | Анна Волкова | TeamFinder API |
| `igor.semenov@example.com` | Игорь Семенов | Conference Planner |
| `marina.li@example.com` | Марина Ли | Recipe Garden |
| `pavel.gusev@example.com` | Павел Гусев | Deploy Toolkit |
| `elena.bondareva@example.com` | Елена Бондарева | Habit Tracker Analytics |

## Проверка

```bash
pytest
flake8
```

## Примечания для ревьюера

- Используется фиксированная папка шаблонов `templates_var3`.
- Папки `media/`, `.claude/`, `.pytest_cache/`, `__pycache__/` и локальное окружение `venv/` не должны попадать в репозиторий.
- Поле `phone` у пользователя необязательное: при заполнении номер нормализуется к формату `+7XXXXXXXXXX` и проверяется на уникальность.
- Значения статуса проекта в базе оставлены `open` и `closed`, а пользовательские подписи переведены на русский.
