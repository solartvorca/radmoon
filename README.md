# 🌙 Луновой Марафон

Flask приложение для проведения лунных марафонов со встроенной системой управления.

## Быстрый старт на Railway

### 1. Создай GitHub репозиторий

```bash
cd "d:\Soft\Rad moon"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rad-moon.git
git push -u origin main
```

### 2. Развертывание

1. Перейди на https://railway.app
2. Нажми "Start a New Project"
3. Выбери "Deploy from GitHub"
4. Авторизируй GitHub и выбери репозиторий

### 3. Переменные окружения в Railway

Добавь в Variables:
```
SECRET_KEY=your_secret_key
VK_TOKEN=ваш_vk_токен
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ваша_почта@gmail.com
SMTP_PASSWORD=ваш_app_password
```

### 4. База данных

Добавь PostgreSQL плагин в Railway → Plugins

Готово! Railway автоматически разверует приложение.

## Локально

```bash
pip install -r requirements.txt
python app.py
```

Откроется на http://127.0.0.1:5000

## Администратор

```bash
python create_admin.py
```

Логин: admin / Пароль: admin123

## Ключевые функции

- 🌙 Множественные марафоны
- 💰 Система лучиков + золотой пыльцы
- 📧 Email уведомления
- 💬 Solfeggio практика
- 🎯 Админ-панель

## Требования

- Python 3.8+
- PostgreSQL (на Railway)
- Git

## Файлы для развертывания

- `requirements.txt` - Зависимости
- `Procfile` - Команда запуска
- `app.py` - Основное приложение
