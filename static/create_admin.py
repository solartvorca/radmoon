from app import app, db, User

with app.app_context():
    # Проверяем, есть ли уже админ
    admin = User.query.filter_by(is_admin=True).first()

    if admin:
        print(f"Админ уже существует: {admin.username}")
    else:
        # Создаем админ пользователя
        new_admin = User(
            username="admin",
            email="admin@example.com",
            password="admin123",  # В реальности использовать хеширование!
            is_admin=True,
            is_active=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Админ пользователь создан!")
        print("Логин: admin")
        print("Пароль: admin123")
