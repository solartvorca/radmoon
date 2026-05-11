#!/usr/bin/env python
"""
Import data from export.json to the database
Run this on Railway after deployment
"""
import json
from app import app, db, User, Marathon, DailyTask, Report, MarathonEnrollment, NotificationSettings, AdminMessage
from datetime import datetime
import pytz

MOSCOW_TZ = pytz.timezone("Europe/Moscow")

def import_data():
    try:
        with open("export.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] export.json not found")
        return

    print("[*] Importing data...")

    with app.app_context():
        # Import users
        if "user" in data:
            for user_data in data["user"]:
                existing = User.query.get(user_data["id"])
                if not existing:
                    user = User(
                        id=user_data["id"],
                        username=user_data["username"],
                        email=user_data["email"],
                        password=user_data["password"],
                        vk_id=user_data.get("vk_id"),
                        rays_balance=user_data.get("rays_balance", 0),
                        gold_dust=user_data.get("gold_dust", 0),
                        is_active=user_data.get("is_active", True),
                        is_admin=user_data.get("is_admin", False)
                    )
                    db.session.add(user)
            db.session.commit()
            print(f"[OK] Imported {len(data['user'])} users")

        # Import marathons
        if "marathon" in data:
            for m_data in data["marathon"]:
                existing = Marathon.query.get(m_data["id"])
                if not existing:
                    marathon = Marathon(
                        id=m_data["id"],
                        name=m_data["name"],
                        description=m_data.get("description"),
                        goal=m_data.get("goal"),
                        calendar_type=m_data.get("calendar_type"),
                        is_published=m_data.get("is_published", False),
                        min_rays=m_data.get("min_rays", 0),
                        order_number=m_data.get("order_number", 0)
                    )
                    db.session.add(marathon)
            db.session.commit()
            print(f"[OK] Imported {len(data['marathon'])} marathons")

        # Import daily tasks
        if "daily_task" in data:
            for task_data in data["daily_task"]:
                existing = DailyTask.query.get(task_data["id"])
                if not existing:
                    task = DailyTask(
                        id=task_data["id"],
                        day_number=task_data["day_number"],
                        title=task_data["title"],
                        content=task_data["content"],
                        video_url=task_data.get("video_url"),
                        marathon_id=task_data["marathon_id"]
                    )
                    db.session.add(task)
            db.session.commit()
            print(f"[OK] Imported {len(data['daily_task'])} daily tasks")

        # Import admin messages
        if "admin_message" in data:
            for msg_data in data["admin_message"]:
                existing = AdminMessage.query.get(msg_data["id"])
                if not existing:
                    msg = AdminMessage(
                        id=msg_data["id"],
                        title=msg_data["title"],
                        email_subject=msg_data.get("email_subject"),
                        email_body=msg_data.get("email_body"),
                        vk_message=msg_data.get("vk_message")
                    )
                    db.session.add(msg)
            db.session.commit()
            print(f"[OK] Imported {len(data['admin_message'])} admin messages")

        print("[DONE] Data import complete!")

if __name__ == "__main__":
    import_data()
