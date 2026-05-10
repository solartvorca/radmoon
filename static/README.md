# Lunar Marathon Web Application

This project aims to create a web application for conducting 28-day lunar marathons, incorporating a backend with Python (Flask/FastAPI), a SQLite database, a frontend with HTML5, CSS3, JavaScript, and a task queue for automation.

## Technology Stack

*   **Backend:** Python (Flask or FastAPI)
*   **Database:** SQLite (Tables: Users, Marathons, DailyTasks, Reports, Rewards)
*   **Frontend:** HTML5, CSS3 (Modern Dark Mystic Style), JavaScript
*   **Task Queue:** Celery or APScheduler

## Functional Requirements

*   **Cyclicality:** Marathon tied to the lunar cycle (full moon to full moon).
*   **Daily Content:** Each of 28 days includes a title, text assignment, and embedded VK video.
*   **Reporting System:** Text input for reports, "Send" button active until 00:00.
*   **Economy (Rays):** +1 Ray for timely reports; 50% discount if balance >= base_item_price; `only_for_rays` flag for exclusive items.
*   **Elimination Mechanic:** Daily 00:01 check for reports; no report -> `dropped_out` status, access blocked until next full moon.
*   **Notifications:** Email (SMTP) and VK (API) reminders 2 hours before deadline.

## Visual Style

*   **Color Palette:** Deep blue (#0B1026), bluish-black, silver accent, neon purple.
*   **Elements:** Interactive moon phase on the main page, showing marathon progress.

## Database Structure (SQLite)

```sql
-- Таблица пользователей
CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    vk_id TEXT,
    rays_balance INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE -- статус участия в текущем марафоне
);

-- Таблица заданий (28 строк)
CREATE TABLE DailyTasks (
    day_number INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    video_url TEXT
);

-- Таблица отчетов
CREATE TABLE Reports (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    day_number INTEGER,
    report_text TEXT,
    submitted_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES Users(id)
);
```

## Development Start Points

*   **Core Backend:** Script to determine "current lunar day" based on the last full moon.
*   **Video Integration:** Use standard VK iframe for embedding videos.
*   **Automation:** `smtplib` for Email, `vk_api` for VK notifications.
