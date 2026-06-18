# Первоначальная настройка проекта TeamFinder

## 1. Виртуальное окружение

Перед началом работы необходимо создать и активировать виртуальное окружение Python.  


1. **Создайте виртуальное окружение (в папке проекта):**
   ```bash
   python3 -m venv venv
   ```

   После этого появится папка `venv`, где будут храниться зависимости проекта.

2. **Активируйте окружение:**

    - **Windows (PowerShell):**
      ```bash
      venv\Scripts\Activate.ps1
      ```
    - **Windows (cmd):**
      ```bash
      venv\Scripts\activate
      ```
    - **Linux/Mac:**
      ```bash
      source venv/bin/activate
      ```

3. **Установите зависимости из `requirements.txt`:**
   ```bash
   pip install -r requirements.txt
   ```

   После установки в окружении будут доступны все нужные библиотеки Django-проекта.

## 2. Создание `.env`

Файл `.env` содержит конфиденциальные настройки проекта — ключ Django, параметры БД и другие переменные.  

Особое внимание обратите на строчку `TASK_VERSION=`. 
Добавьте число, которое соответствует вашему варианту задания. 
Этот параметр определяет, какие шаблоны использовать для сайта (из папок `templates_var1`/`templates_var2`/`templates_var3`).
Лишние две папки не из вашего варианта можно удалить.

В репозитории есть пример `.env_example`, который нужно скопировать и заполнить:

```bash
cp .env_example .env
```

После этого откройте `.env` и укажите свои значения.  

| Переменная            | Назначение                                                                                                                                                 |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DJANGO_SECRET_KEY** | Секретный ключ Django, используемый для подписи cookie и токенов. Можно сгенерировать при помощи `get_random_secret_key` из `django.core.management.utils` |
| **DJANGO_DEBUG**      | Режим отладки. Установите `True` во время разработки.                                                                                                      |
| **POSTGRES_DB**       | Имя базы данных PostgreSQL, которую будет использовать Django.                                                                                             |
| **POSTGRES_USER**     | Имя пользователя PostgreSQL.                                                                                                                               |
| **POSTGRES_PASSWORD** | Пароль пользователя PostgreSQL.                                                                                                                            |
| **POSTGRES_HOST**     | Адрес сервера БД. В случае локальной разработки localhost.                                                                                                 |
| **POSTGRES_PORT**     | Порт подключения к БД (по умолчанию `5432`).                                                                                                               |
| **TASK_VERSION**      | Номер варианта вашего задания. Используется для определения набора HTML-шаблонов.                                                                          |

---

## 3. Запуск PostgreSQL

Для работы приложения **TeamFinder** используется база данных **PostgreSQL**.
По условию задания база данных должна запускаться в контейнере Docker.

В проекте уже есть пример файла `docker-compose.yml`. 
Используйте готовый или измените под свои нужды, а дальше запускайте:

```bash
docker compose up -d
```

`-d` значит `detach`, то есть контейнер продолжит работать в фоне. Чтобы его остановить, надо будет ввести

```bash
docker compose down
```

Если возникает ошибка "permission denied while trying to connect to the Docker daemon socket", то может потребоваться добавить `sudo` перед командой.

---

После этого база данных будет доступна по адресу `localhost:5432`.  
Нужно будет использовать эти же параметры в файле `.env`.

> Если на компьютере уже развёрнут сервер БД на порте 5432, и вы не хотите создавать БД для этого проекта на этом сервере, целесообразнее будет изменить порт на нестандартный.
> Нестандартный порт нужно будет поставить слева в паре портов в docker-compose (`"5433":"5432"`) и в .env.

## 4. Запуск Django

После заполнения `.env` и настройки базы данных можно запустить сервер разработки:

```bash
python manage.py runserver
```

Теперь проект доступен по адресу [http://localhost:8000](http://localhost:8000). 
Если видите ракету с надписью "The install worked successfully! Congratulations!", то запуск прошёл успешно, Django работает!
Осталось всего ничего: реализовать весь проект!

Если в процессе разработки способ развертывания приложения поменяется, обновите `readme.md` с пометкой ревьюеру, как запускать и проверять приложение.

---

## 5. Итоговая инструкция по запуску (Вариант 3)

Реализован **Вариант 3**: каждый проект имеет список необходимых навыков
(`Skill`), список проектов можно фильтровать по навыку, владелец проекта может
добавлять и удалять навыки через AJAX.

1. Создать и активировать виртуальное окружение, установить зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt   # для тестов и линтера
   ```

2. Скопировать `.env_example` в `.env` и заполнить значения. Обязательно
   `TASK_VERSION=3`. Для локального запуска подходит, например:
   ```
   DJANGO_SECRET_KEY=<сгенерированный ключ>
   DJANGO_DEBUG=True
   POSTGRES_DB=team_finder
   POSTGRES_USER=team_finder
   POSTGRES_PASSWORD=team_finder
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5436
   TASK_VERSION=3
   ```
   Порт `5436` указан в `docker-compose.yml` (проброшен на стандартный порт
   PostgreSQL `5432` внутри контейнера) — если он у вас занят, поменяйте
   значение и в `.env`, и в `docker-compose.yml`.

3. Поднять PostgreSQL (через Docker — см. п. 3 выше, либо локально без
   Docker — см. раздел «Запуск без Docker» ниже):
   ```bash
   docker compose up -d
   ```

4. Применить миграции и создать суперпользователя:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Заполнить базу демонстрационными данными (пользователи и проекты с
   навыками):
   ```bash
   python manage.py populate_demo
   ```

6. Запустить сервер разработки:
   ```bash
   python manage.py runserver
   ```
   Приложение доступно на [http://localhost:8000/projects/list/](http://localhost:8000/projects/list/).

### Запуск без Docker (локальный PostgreSQL)

Если Docker не используется, нужно установить и запустить PostgreSQL локально
и создать базу/пользователя самостоятельно.

1. Установить PostgreSQL (если не установлен):
   - **macOS (Homebrew):**
     ```bash
     brew install postgresql@16
     brew services start postgresql@16
     ```
   - **Ubuntu/Debian:**
     ```bash
     sudo apt update
     sudo apt install postgresql postgresql-contrib
     sudo systemctl start postgresql
     ```
   - **Windows:** скачать и установить с
     [postgresql.org/download](https://www.postgresql.org/download/windows/),
     служба PostgreSQL запускается автоматически.

2. Создать базу данных и пользователя (от имени системного пользователя
   `postgres`):
   ```bash
   psql -U postgres -c "CREATE USER team_finder WITH PASSWORD 'team_finder';"
   psql -U postgres -c "CREATE DATABASE team_finder OWNER team_finder;"
   ```
   На macOS с Homebrew роль `postgres` обычно не нужна — можно выполнить эти
   команды от своего пользователя:
   ```bash
   psql postgres -c "CREATE USER team_finder WITH PASSWORD 'team_finder';"
   psql postgres -c "CREATE DATABASE team_finder OWNER team_finder;"
   ```

3. В `.env` указать стандартный порт PostgreSQL (`5432`, если он не занят):
   ```
   POSTGRES_DB=team_finder
   POSTGRES_USER=team_finder
   POSTGRES_PASSWORD=team_finder
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   TASK_VERSION=3
   ```

4. Дальше — как в основной инструкции, без шага с `docker compose up -d`:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py populate_demo
   python manage.py runserver
   ```

### Тестовые аккаунты

После выполнения `populate_demo` доступны пользователи (пароль у всех
`password123`):

| Email                       | Имя               | Проект (с навыками)                                  |
|-----------------------------|-------------------|-------------------------------------------------------|
| anna.volkova@example.com    | Анна Волкова      | TeamFinder API — Python, Django, PostgreSQL            |
| igor.semenov@example.com    | Игорь Семенов     | Conference Planner — React, TypeScript, Figma          |
| marina.li@example.com       | Марина Ли         | Recipe Garden (закрыт) — Figma, UX Research            |
| pavel.gusev@example.com      | Павел Гусев       | Deploy Toolkit — Docker, CI/CD, Python                  |
| elena.bondareva@example.com  | Елена Бондарева   | Habit Tracker Analytics — Python, SQL, Pandas           |

### Автотесты и линтер

```bash
pytest          # автотесты (users/tests.py, projects/tests.py)
flake8          # проверка PEP8 (max-line-length=100, см. .flake8)
```

### Отклонения от ТЗ

- Папки `templates_var1/` и `templates_var2/` удалены — используется только
  `templates_var3` (`TASK_VERSION=3`).
- Поле `phone` модели `User` сделано необязательным (`blank=True, null=True`):
  форма регистрации по ТЗ собирает только имя, фамилию, email и пароль, а
  телефон указывается позже в профиле. При указании телефона он нормализуется
  к формату `+7XXXXXXXXXX` (принимаются форматы `8XXXXXXXXXX` и
  `+7XXXXXXXXXX`) и проверяется на уникальность.
- Подписи статусов проекта (`STATUS_CHOICES`) переведены на русский язык
  («Открыт» / «Закрыт») для отображения в выпадающем списке, значения в базе
  (`open` / `closed`) оставлены без изменений.
- Эндпоинт добавления навыка к проекту (`/projects/<id>/skills/add/`)
  дополнительно возвращает поля `id` и `name` (помимо `skill_id`, `created`,
  `added` из ТЗ) — это нужно готовому фронтенду `static/js/skills.js` для
  отрисовки добавленного навыка без перезагрузки страницы.
- В шаблоны `project_list.html` и `participants.html` добавлена пагинация
  (12 элементов на страницу) через общий include `includes/pagination.html`,
  которого не было в исходной заготовке.
- Исправлены баги исходной заготовки: неразрешённый конфликт слияния в
  `participants.html`, обращение к несуществующему полю `project.title`
  (заменено на `project.name`), использование удалённого в Pillow 10+ метода
  `draw.textsize` при генерации аватара (заменено на `draw.textbbox`), а также
  сравнение объекта `Skill` со строкой в фильтре по навыкам на странице
  проектов.
