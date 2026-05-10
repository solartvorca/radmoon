from app import app, db, User

with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print("Username: " + admin.username)
        print("Password in DB: [" + str(admin.password) + "]")
        print("Password length: " + str(len(admin.password)))
    else:
        print("Admin not found")
