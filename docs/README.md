# 📚 Технічна документація проєкту

Цей каталог містить усю технічну, архітектурну та експлуатаційну документацію для системи  
**"Веб-платформа дистанційного навчання з підсистемою формування персоналізованих рекомендацій для подальшого навчання" (Smart-Study)**.

---

## 🔖 Структура документації

### `01_architecture/` (Архітектура системи)

- **[system_design.md](01_architecture/system_design.md)** — Загальна архітектура системи, взаємодія клієнт-сервер (React ↔ Nginx ↔ Django), використання Celery та Redis для фонових задач.
- **[frontend_fsd.md](01_architecture/frontend_fsd.md)** — Опис архітектури клієнтської частини за методологією Feature-Sliced Design (FSD), розподіл на шари та модулі.
- **[backend_services.md](01_architecture/backend_services.md)** — Структура Django-додатка, сервісний шар (`services/`), логіка розділення на apps (`courses`, `users`, `notifications`, `users_calendar`).

### `02_database-design/` (Проєктування баз даних)

- **[hybrid_storage.md](02_database-design/hybrid_storage.md)** — Обґрунтування використання гібридного підходу (PostgreSQL для реляційних даних + MongoDB для гнучких структур курсів та тестів).
- **[postgresql_schema.md](02_database-design/postgresql_schema.md)** — ER-діаграма реляційної БД та опис ключових доменних моделей (користувачі, курси, підписки).
- **[mongodb_schema.md](02_database-design/mongodb_schema.md)** — Структура NoSQL колекцій для збереження ієрархії навчальних модулів та гнучких структур тестів.
- **[cache_and_blob_storage.md](02_database-design/cache_and_blob_storage.md)** — Організація In-Memory кешування (Redis) та хмарного файлового сховища (Supabase).

### `03_ml_recommender/` (Підсистема рекомендацій)

- **[recommendation_engine.md](03_ml_recommender/recommendation_engine.md)** — Теоретичне обґрунтування алгоритму Content-Based Filtering (контентна фільтрація).
- **[ml_pipeline.md](03_ml_recommender/ml_pipeline.md)** — Процес обробки даних: використання `stopwords_ua.txt`, TF-IDF векторизація, обчислення косинусної схожості (`course_recommender.py`).
- **[adaptive_logic.md](03_ml_recommender/adaptive_logic.md)** — Логіка адаптації навчального шляху на основі статусу проходження курсу (Passed/Failed).
- **[model_lifecycle_and_integration.md](03_ml_recommender/model_lifecycle_and_integration.md)** - Життєвий цикл моделі: оркестрація процесу тренування, використання Singleton-патерну для кешування в пам'яті (lazy loading) та інтеграція з REST API платформи.

### `04_api_reference/` (API та Інтеграція)

- **[rest_api_specs.md](04_api_reference/rest_api_specs.md)** — Опис ключових REST API ендпоінтів, форматів запитів та відповідей.
- **[auth_flow.md](04_api_reference/auth_flow.md)** — Механізм авторизації та автентифікації (включно із Social Auth та верифікацією email).
- **[pull_notifications.md](04_api_reference/pull_notifications.md)** — Опис механізму отримання сповіщень через Pull-модель (polling). Обґрунтування вибору архітектури замість WebSockets, інтеграція з Redis-кешем та життєвий цикл сповіщення.

### `05_infrastructure/` (Інфраструктура та Розгортання)

- **[deployment_guide.md](05_infrastructure/deployment_guide.md)** — Інструкція з розгортання проєкту на Microsoft Azure Virtual Machines.
- **[docker_orchestration.md](05_infrastructure/docker_orchestration.md)** — Опис конфігурації `docker-compose.yml`, взаємодія контейнерів.
- **[nginx_ssl.md](05_infrastructure/nginx_ssl.md)** — Налаштування Reverse Proxy та SSL сертифікатів.

---

## 🧭 Навігація

Повернутися до [головного README.md](../README.md) проєкту.
