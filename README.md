# 🎓 Smart-Study: Веб-платформа дистанційного навчання з підсистемою формування персоналізованих рекомендацій для подальшого навчання

**Smart-Study** — це сучасна LMS (Learning Management System), розроблена для оптимізації навчального процесу за допомогою інтелектуальних рекомендацій та зручного інтерфейсу.

## 🚀 Live Demo

Проєкт задеплоєно на Azure: [https://smart-study.me](https://smart-study.me)

---

## 🔧 Стек технологій

- **Backend:** Python 3.12, Django, Django REST Framework (DRF), Celery
- **Frontend:** React, TailwindCSS, Axios, TypeScript, Vite
- **Бази даних:**
  - **PostgreSQL:** Основна реляційна БД (користувачі, курси, прогрес).
  - **MongoDB:** NoSQL сховище для гнучких структур курсів та даних тестів.
  - **Redis:** Кешування та брокер повідомлень для Celery.
  - **Supabase:** blob storage для зберігання медіафайлів та документів.
  - **ML & Data Science:** Scikit-learn (TF-IDF векторизація, Косинусна схожість), Pandas, TensorFlow.
- **Infrastructure:** Nginx (Reverse Proxy), Docker Compose, Let's Encrypt (SSL).
- **Cloud:** Microsoft Azure (Virtual Machines).

---

## 📂 Структура проєкту

Проєкт організований за наступним принципом:

- `/backend` — Django сервіс (API, бізнес-логіка, ML-моделі).
- `/frontend` — SPA додаток на React.
- `/nginx` — Конфігураційні файли веб-сервера.
- `/docs` — Розширена технічна документація.
- `docker-compose.yml` — Оркестрація всіх сервісів.

---

## ⚙️ Швидкий запуск (Local Development)

Для запуску проєкту локально необхідно мати встановлений **Docker**.

1. Клонуйте репозиторій:
   ```bash
   git clone https://github.com/WeeWeektor/SmartS-tudy.git
   cd Smart-Study
   ```
2. Створіть конфігураційні файли на основі прикладів:
   - Скопіюйте [backend/.env.example](backend/.env.example) та збережіть як backend/.env
   - Скопіюйте [frontend/.env.example](frontend/.env.example) та збережіть як frontend/.env
3. Запустіть контейнери:
   ```bash
   docker-compose up -d --build
   ```
4. Виконайте міграції бази даних:
   ```bash
   docker exec -it smartStudy_backend python manage.py migrate
   ```
5. Додаток буде доступний за адресою: http://localhost.

---

## 🧠 Ключові особливості

- **Інтелектуальна персоналізація:** Власна рекомендаційна система (Content-Based Filtering), що аналізує текстовий опис курсів та рівень складності для формування індивідуальної траєкторії навчання.
- **Адаптивна логіка:** Система автоматично пропонує складніші курси при успішному проходженні (Passed) або допоміжні матеріали при невдачі (Failed).
- **Гібридне сховище даних:** Оптимальне поєднання PostgreSQL (для ACID транзакцій) та MongoDB (для складних JSON-структур навчальних планів).
- **Безпека:** Налаштований HTTPS, захищені з'єднання з базами даних.
- **Аналітика:** Викладачам надається можливість відстеження прогресу студентів та ефективність курсів.

---

## 📝 Автори

Віктор — Student at Igor Sikorsky KPI.

- [GitHub Profile](https://github.com/WeeWeektor)
- [LinkedIn Profile](https://www.linkedin.com/in/viktor-duplyka-6bb607300/)

---

## 📖 Документація

Детальний опис архітектури, бази даних та ML-моделей доступний у розділі [Documentation.](docs/README.md)
