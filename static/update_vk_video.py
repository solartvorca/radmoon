from app import app, db, DailyTask

# Твое видео ВК с autoplay параметром
vk_video_url = "https://vk.com/video_ext.php?oid=-186690269&id=456239435&autoplay=1"

with app.app_context():
    # Обновляем ВСЕ дни одним видео
    tasks = DailyTask.query.all()
    for task in tasks:
        task.video_url = vk_video_url
        print(f"Updated Day {task.day_number}")

    db.session.commit()
    print(f"\nВсе {len(tasks)} дней обновлены!")
    print(f"Видео: {vk_video_url}")
