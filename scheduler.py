from datetime import datetime, timedelta
import pytz
from app import app, db, User, Report, DailyTask, MOSCOW_TZ, get_current_lunar_day

# Placeholder for email notification function
def send_email_notification(user_email, subject, body):
    print(f"Sending email to {user_email}: {subject} - {body}")
    # In a real application, use smtplib or a mail library

# Placeholder for VK notification function
def send_vk_notification(vk_id, message):
    print(f"Sending VK message to {vk_id}: {message}")
    # In a real application, use vk_api

def daily_check_and_notifications():
    with app.app_context():
        now = datetime.now(MOSCOW_TZ)
        current_lunar_day = get_current_lunar_day()
        previous_lunar_day = (current_lunar_day - 2 + 28) % 28 + 1 # Day before current

        # Check for dropped out users
        all_active_users = User.query.filter_by(is_active=True).all()
        for user in all_active_users:
            # Check if they submitted a report for the previous lunar day
            report_for_previous_day = Report.query.filter_by(user_id=user.id, day_number=previous_lunar_day).first()
            
            if not report_for_previous_day:
                user.is_active = False
                db.session.add(user)
                db.session.commit()
                print(f"User {user.username} dropped out for not submitting report on day {previous_lunar_day}")
                # Send notification about dropping out
                send_email_notification(user.email, "Lunar Marathon Update", "You have been dropped out for not submitting your report.")
                if user.vk_id:
                    send_vk_notification(user.vk_id, "You have been dropped out from the Lunar Marathon.")

        # Send deadline reminders (e.g., 2 hours before 00:00 of the next day)
        # This logic needs to be more precise based on the marathon start time and current lunar day
        # For simplicity, let's assume we remind for the current day's task
        reminder_time = now.replace(hour=22, minute=0, second=0, microsecond=0) # 22:00 (10 PM) for 00:00 deadline
        if now.hour == reminder_time.hour and now.minute == reminder_time.minute:
            task_for_today = DailyTask.query.get(current_lunar_day)
            if task_for_today:
                for user in all_active_users:
                    report_submitted_today = Report.query.filter_by(user_id=user.id, day_number=current_lunar_day).first()
                    if not report_submitted_today:
                        send_email_notification(user.email, "Reminder: Lunar Marathon Report Due!", f"Don\'t forget to submit your report for Day {current_lunar_day}: {task_for_today.title}")
                        if user.vk_id:
                            send_vk_notification(user.vk_id, f"Reminder: Submit your report for Day {current_lunar_day}: {task_for_today.title}")

# For testing purposes, you can call this function directly
if __name__ == "__main__":
    with app.app_context():
        # Simulate running the daily check
        print("Running daily check and notifications...")
        daily_check_and_notifications()
        print("Daily check completed.")