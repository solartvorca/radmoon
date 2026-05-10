from app import app, db, DailyTask

# YouTube видео для примера (замени на реальные)
sample_videos = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # День 1
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # День 2
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # День 3
]

with app.app_context():
    tasks = DailyTask.query.all()
    for i, task in enumerate(tasks[:3]):  # Первые 3 дня
        if i < len(sample_videos):
            task.video_url = sample_videos[i]
    db.session.commit()
    print("Videos updated!")
