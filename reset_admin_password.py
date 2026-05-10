from app import app, db, User

with app.app_context():
    # Находим админа
    admin = User.query.filter_by(is_admin=True).first()

    if admin:
        admin.password = "admin123"
        db.session.commit()
        print("Password updated for: " + admin.username)
        print("Password: admin123")
    else:
        print("Admin not found")
