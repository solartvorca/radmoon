from app import app, db, DailyTask

# Примеры видео ВК в формате video_ext.php
# Формат: https://vk.com/video_ext.php?oid={owner_id}&id={video_id}&hash={hash}
vk_videos = [
    "https://vk.com/video_ext.php?oid=-186690269&id=456239332&hash=f593881523457a41",  # День 1
    "https://vk.com/video_ext.php?oid=-186690269&id=456239333&hash=f593881523457a42",  # День 2
    "https://vk.com/video_ext.php?oid=-186690269&id=456239334&hash=f593881523457a43",  # День 3
]

with app.app_context():
    tasks = DailyTask.query.all()
    for i, task in enumerate(tasks[:3]):
        if i < len(vk_videos):
            task.video_url = vk_videos[i]
            print(f"Updated Day {task.day_number} with VK video")

    db.session.commit()
    print("VK videos added successfully!")

    # Показываем видео для остальных дней
    print("\nTo add more VK videos, use this format:")
    print("https://vk.com/video_ext.php?oid={owner_id}&id={video_id}&hash={hash}")
