# reset.py

from app import app, db, Marathon, DailyTask

with app.app_context():
    # Удаляем все старые таблицы
    db.drop_all()
    # Создаем новые таблицы с актуальной структурой
    db.create_all()

    # Пример создания первого марафона и его дней
    marathon = Marathon(
        name="Лунный марафон",
        description="Марафон осознанности по лунному календарю.",
        goal="Развить привычку ежедневных практик.",
        calendar_type="lunar",
        regularity="daily"
    )
    db.session.add(marathon)
    db.session.commit()

    for i in range(1, 29):
        new_task = DailyTask(
            day_number=i,
            title=f"Day {i} Task",
            content=f"This is the task for lunar day {i}. Complete it to earn rays!",
            video_url=f"https://vk.com/video_example_{i}",
            marathon_id=marathon.id
        )
        db.session.add(new_task)
    db.session.commit()
    print("База данных и первый марафон успешно созданы!")