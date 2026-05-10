# 📦 Развертывание на Railway

## ✅ Все готово для развертывания!

Твое приложение уже настроено для Railway. Вот пошаговая инструкция:

## Шаг 1: GitHub репозиторий

### На локальной машине:

```bash
cd "d:\Soft\Rad moon"

# Инициализируй Git
git init
git add .
git commit -m "Initial commit: Lunar Marathon application"
git branch -M main
```

### На GitHub:

1. Перейди на https://github.com/new
2. Создай новый репозиторий `rad-moon`
3. **НЕ** инициализируй с README

### Продолжи на локальной машине:

```bash
git remote add origin https://github.com/YOUR_USERNAME/rad-moon.git
git push -u origin main
```

## Шаг 2: Railway развертывание

### 1. Создай аккаунт (если нет)
- Перейди на https://railway.app
- Нажми "Sign Up"
- Авторизируй через GitHub

### 2. Создай новый проект
- Нажми "Start a New Project"
- Выбери "Deploy from GitHub"
- Авторизируй GitHub
- Выбери репозиторий `rad-moon`

### 3. Railway автоматически:
- Обнаружит `Procfile`
- Обнаружит `requirements.txt`
- Запустит приложение

## Шаг 3: Добавь базу данных PostgreSQL

### В Railway dashboard:

1. Перейди в свой проект
2. Нажми "Add" (или "+" кнопка)
3. Выбери "Add Service"
4. Выбери "Postgres"
5. Railway автоматически создаст `DATABASE_URL`

## Шаг 4: Переменные окружения

### В Railway dashboard:

1. Перейди в свой проект
2. Нажми на сервис Python
3. Вкладка "Variables"
4. Добавь переменные:

```
SECRET_KEY=generate_random_string_here
VK_TOKEN=ваш_vk_токен_здесь
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ваша_почта@gmail.com
SMTP_PASSWORD=app_password_от_gmail
```

### Как получить эти значения:

**SECRET_KEY:** Любая длинная случайная строка
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**VK_TOKEN:** Из baza.env (уже есть)

**SMTP для Gmail:**
1. Включи 2FA: https://myaccount.google.com/security
2. Создай App Password: https://myaccount.google.com/apppasswords
3. Выбери "Mail" и "Windows Computer"
4. Скопируй пароль в SMTP_PASSWORD

## Шаг 5: Запуск

В Railway dashboard нажми "Deploy"

Готово! Твое приложение работает! 🎉

URL приложения будет в Railway dashboard.

## Проверка статуса

### Логи:
- Railway dashboard → Deployments → последний → Logs

### Если ошибка:
1. Проверь логи в Railway
2. Убедись что DATABASE_URL правильно установлена
3. Проверь SMTP переменные
4. Нажми "Redeploy"

## Обновления

Для обновления приложения просто:

```bash
git add .
git commit -m "Update: description"
git push
```

Railway автоматически переразвернет приложение!

## Администратор

После развертывания создай администратора:

1. Откройся приложение на Railway URL
2. Используй эндпоинт `/create-admin` или запусти локально:
```bash
python create_admin.py
```

Логин: `admin`
Пароль: `admin123`

## Помощь

### Если Database не работает
- Убедись что PostgreSQL плагин добавлен
- Проверь что DATABASE_URL создана автоматически
- Перезагрузи deployment

### Если Email не отправляется
- Используй App Password для Gmail, не обычный пароль
- Убедись что почта включена в SMTP_USER
- Проверь SMTP_HOST и SMTP_PORT

### Если приложение медленно запускается
- В первый раз может быть медленно
- Railway кеширует Docker образы
- Следующий запуск будет быстрее

## Что дальше?

Твое приложение полностью готово к использованию!

- 🌙 Создавай марафоны в админ-панели
- 💰 Управляй лучиками и пользователями
- 📧 Отправляй уведомления
- 🎯 Добавляй новые функции

Удачи! 🚀
