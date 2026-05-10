from app import app, db, User

with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        admin.password = "123"
        db.session.commit()
        print("New password set to: 123")
    else:
        print("Admin not found")
