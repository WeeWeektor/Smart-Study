# Специфікація REST API (Архітектурний огляд)

Взаємодія між клієнтським додатком (Frontend) та бекендом платформи **Smart-Study** побудована на принципах RESTful
архітектури. Система розбита на незалежні модулі, що забезпечує легке масштабування та підтримку.

## 1. Базові стандарти API

- **Формат обміну даними:** `application/json`.
- **Автентифікація:** Сесійна (на базі Cookie: `sessionid`) з обов'язковим використанням CSRF-токенів (`csrftoken`) для
  захисту POST, PUT та DELETE запитів.
- **Обробка помилок:** Використовуються стандартизовані HTTP-коди:
  - `200 OK` / `201 Created` — успішне виконання.
  - `400 Bad Request` — помилка валідації вхідних даних.
  - `401 Unauthorized` / `403 Forbidden` — відсутність прав доступу.
  - `404 Not Found` — ресурс не знайдено.
  - `500 Internal Server Error` — внутрішня помилка сервера.
- **Базовий шлях (Base URL):** Всі запити API починаються з префікса `/api/`.

---

## 2. Структура ендпоінтів за бізнес-доменами

Нижче наведено опис ключових просторів імен (namespaces) та основних маршрутів системи.

### 2.1. Авторизація та користувачі (`/api/auth/`, `/api/user/`)

Відповідає за безпеку, управління сесіями та профілями студентів/викладачів.

- **`GET /api/auth/get-csrf-token/`** — Отримання токена безпеки перед формами логіну/реєстрації.
- **`POST /api/auth/register/` та `POST /api/auth/login/`** — Класична реєстрація та вхід.
- **`POST /api/auth/google-oauth/` / `facebook-oauth/`** — Авторизація через сторонні соціальні мережі (OAuth2).
- **`GET /api/user/profile/`** — Отримання даних поточного авторизованого користувача.
- **`GET /api/user/profile/learning-stats/`** — Отримання загальної статистики навчання користувача (кешується в Redis).

### 2.2. Навчальний контент (`/api/course/`, `/api/module/`, `/api/lesson/`)

Управління каталогом та ієрархією навчальних матеріалів (PostgreSQL + MongoDB).

- **`GET /api/course/courses-list/`** — Отримання каталогу всіх опублікованих курсів (з підтримкою пошуку
  `/<str:search_query>/`).
- **`GET /api/course/course/<uuid:course_id>/`** — Детальна інформація про курс, включаючи його структуру (модулі та
  лекції).
- **`POST /api/course/create-course/`** — Створення нового курсу викладачем.
- **`GET /api/course/course-recommendations/<uuid:course_id>/`** — **[ML Підсистема]** Отримання персоналізованих
  рекомендацій на основі алгоритму Content-Based Filtering.
- **`GET /api/lesson/lesson/<uuid:lesson_id>/`** — Отримання контенту конкретної лекції.

### 2.3. Процес навчання та тестування (`/api/enrollment/`, `/api/test/`)

Відстеження прогресу студента, проходження тестів та сертифікація.

- **`POST /api/enrollment/start-course-enrollment/<uuid:course_id>/`** — Початок проходження курсу студентом.
- **`PATCH /api/enrollment/update-enrollment-progress/<uuid:course_id>/`** — Оновлення відсотка проходження курсу.
- **`GET /api/test/course-test/<uuid:test_id>/`** — Завантаження структури тесту.
- **`POST /api/test/start-test-attempt/<uuid:test_id>/`** — Ініціалізація спроби проходження тесту та відправка
  результатів для автоматичної перевірки.
- **`GET /api/course/certificates/verify/<str:certificate_id>/`** — Публічний ендпоінт для перевірки валідності виданого
  сертифіката.

### 2.4. Сповіщення та розклад (`/api/notifications/`, `/api/user-calendar/`)

Система асинхронних сповіщень та планування навчання.

- **`GET /api/notifications/get_notifications/`** — Отримання списку системних сповіщень.
- **`POST /api/notifications/mark_as_read/`** — Відмітка вибраних сповіщень як прочитаних.
- **`POST /api/notifications/post_owner_course_notifications/<str:course_id>/`** — Масова розсилка анонсів від викладача
  всім студентам курсу.
- **`GET /api/user-calendar/personal-events/`** — Отримання особистого розкладу дедлайнів та подій користувача.

### 2.5. Додаткові модулі

- **`/api/course-review/get_reviews/`** — Система відгуків та рейтингування курсів.
- **`/api/wishlist/add-course-to-wishlist/<uuid:course_id>/`** — Додавання курсу до списку "Збережене".
- **`/api/counter/all-published-courses/`** — Отримання загальної статистики платформи (лічильники).

---

## 3. Формати обміну даними (Payload Examples)

_Усі відповіді API мають чітку JSON-структуру._
