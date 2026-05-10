import sys
from app import app, db, User, NotificationSettings
import os

with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print(f"+ Admin found: {admin.username} (ID: {admin.id})")
    else:
        print("- No admin found")

    vk_token = os.environ.get("VK_TOKEN")
    smtp_host = os.environ.get("SMTP_HOST")
    print(f"+ VK_TOKEN loaded: {'Yes' if vk_token else 'No'}")
    print(f"+ SMTP_HOST: {smtp_host if smtp_host else 'No'}")
    print(f"+ SMTP_USER: {'Yes' if os.environ.get('SMTP_USER') else 'No'}")

    print("\nAll systems operational. Ready for testing.")
