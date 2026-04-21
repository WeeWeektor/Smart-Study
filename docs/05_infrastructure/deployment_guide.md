# Інструкція з розгортання проєкту (Azure Deployment Guide)

Цей документ описує процес ручного розгортання платформи **Smart-Study** на хмарній інфраструктурі Microsoft Azure.

## 1. Специфікація інфраструктури

- **Провайдер:** Microsoft Azure (підписка Azure for Students).
- **Тип ресурсу:** Virtual Machine (VM).
- **Розмір машини:** Standard B2ms (2 vCPUs, 8 GiB RAM).
- **Операційна система:** Ubuntu 22.04 LTS (Canonical).
- **Мережа:** Публічна IP-адреса з відкритими портами `80` (HTTP), `443` (HTTPS) та `22` (SSH).

## 2. Підготовка сервера (First-time setup)

Після створення віртуальної машини необхідно підключитися до неї через SSH та встановити базові залежності (Docker та
Git).

```bash
# Підключення до сервера
ssh username@<your_azure_public_ip>

# Оновлення пакетів
sudo apt update && sudo apt upgrade -y

# Встановлення Git
sudo apt install git -y

# Встановлення Docker та Docker Compose
sudo apt install docker.io docker-compose -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

_(Після додавання користувача до групи `docker`, необхідно перезайти на сервер)._

## 3. Отримання коду та налаштування оточення

Код доставляється на сервер шляхом клонування репозиторію.

```bash
# Клонування проєкту
git clone <repository_url> smartstudy
cd smartstudy

# Створення файлу змінних оточення
nano .env
```

У файлі `.env` необхідно вказати всі секретні ключі, паролі до баз даних, налаштування Redis та ключі доступу до
зовнішніх сервісів (Google/Facebook OAuth, Supabase). Приклади вмісту `.env` знаходяться у файлах
`backend/.env.example` та `frontend/.env.example`.

## 4. Налаштування SSL-сертифікатів (Let's Encrypt)

Сертифікати генеруються на хост-машині за допомогою Certbot і монтуються безпосередньо у контейнер `nginx` через
конфігурацію `volumes`.

```bash
# Встановлення Certbot
sudo apt install certbot -y

# Генерація сертифіката (потребує зупиненого порту 80)
sudo certbot certonly --standalone -d smart-study.me -d www.smart-study.me
```

## 5. Запуск платформи

Система повністю контейнеризована. Всі мікросервіси (Django, PostgreSQL, MongoDB, Redis, Celery, Nginx та Frontend)
піднімаються однією командою.

```bash
# Побудова та запуск усіх контейнерів у фоновому режимі
docker-compose up -d --build
```

## 6. Пост-інсталяційні кроки (Міграції та Статика)

Після успішного запуску контейнерів необхідно застосувати міграції бази даних та зібрати статичні файли для бекенду:

```bash
# Застосування міграцій PostgreSQL
docker-compose exec backend python manage.py migrate

# Збір статичних файлів (для адмін-панелі та бекенд-сервісів)
docker-compose exec backend python manage.py collectstatic --noinput

# (Опціонально) Створення суперкористувача
docker-compose exec backend python manage.py createsuperuser
```

## 7. Оновлення коду (Deployment Workflow)

При виході нових оновлень процес деплою виглядає так:

```bash
cd smartstudy
git pull origin main
docker-compose up -d --build
```

_(У випадку зміни моделей бази даних необхідно повторно виконати команду міграції)._
