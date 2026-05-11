from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pytz # For timezone aware datetimes
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
try:
    load_dotenv("baza.env")
except:
    pass
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "lyunny_marafon_2026_super_secret_key")

# Database URL - use PostgreSQL in production, SQLite in development
database_url = os.environ.get("DATABASE_URL", "")
if database_url and database_url.startswith("postgresql://"):
    # Fix psycopg2 URL for SQLAlchemy
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///marathon.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Environment variables with defaults for Railway deployment
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = os.environ.get("SMTP_PORT", "587")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
VK_TOKEN = os.environ.get("VK_TOKEN", "")

# Define timezone for consistency
MOSCOW_TZ = pytz.timezone("Europe/Moscow")

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    vk_id = db.Column(db.Text)
    rays_balance = db.Column(db.Integer, default=0)
    gold_dust = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)


# Новая модель Марафона
class Marathon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    goal = db.Column(db.Text)
    calendar_type = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    regularity = db.Column(db.String(50))
    is_published = db.Column(db.Boolean, default=False)
    min_rays = db.Column(db.Integer, default=0)
    order_number = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(MOSCOW_TZ))
    tasks = db.relationship('DailyTask', backref='marathon', lazy=True)

# Обновленная модель задания, привязанная к марафону
class DailyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.Text)
    marathon_id = db.Column(db.Integer, db.ForeignKey('marathon.id'), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    marathon_id = db.Column(db.Integer, db.ForeignKey("marathon.id"), nullable=True)
    report_text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now(MOSCOW_TZ))

    user = db.relationship("User", backref="reports")
    marathon = db.relationship("Marathon", backref="reports")

class MarathonEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    marathon_id = db.Column(db.Integer, db.ForeignKey("marathon.id"), nullable=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(MOSCOW_TZ))
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship("User", backref="enrollments")
    marathon = db.relationship("Marathon", backref="enrollments")

class NotificationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    email_notifications = db.Column(db.Boolean, default=False)
    vk_notifications = db.Column(db.Boolean, default=False)
    vk_user_id = db.Column(db.String(50), default='')
    notification_time = db.Column(db.String(10), default='09:00')

    user = db.relationship("User", backref="notification_settings")

class AdminMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    email_subject = db.Column(db.String(200))
    email_body = db.Column(db.Text)
    vk_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(MOSCOW_TZ))
    sent_at = db.Column(db.DateTime, nullable=True)
    recipient_count = db.Column(db.Integer, default=0)

# We'll create tables explicitly in the __main__ block or with a separate script
# @app.before_request
# def create_tables():
#     db.create_all()

# --- Notification Functions ---

def send_email(to_email, subject, body):
    try:
        smtp_host = os.environ.get("SMTP_HOST")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_password = os.environ.get("SMTP_PASSWORD")

        if not all([smtp_host, smtp_user, smtp_password]):
            print(f"SMTP config missing")
            return False

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def send_vk_message(vk_user_id, message):
    try:
        vk_token = os.environ.get("VK_TOKEN")
        if not vk_token or not vk_user_id:
            return False

        url = "https://api.vk.com/method/messages.send"
        params = {
            "user_id": vk_user_id,
            "message": message,
            "access_token": vk_token,
            "v": "5.131"
        }

        response = requests.post(url, params=params)
        data = response.json()

        return "response" in data
    except Exception as e:
        print(f"VK message sending error: {e}")
        return False

# --- Core Logic ---

def get_current_lunar_day():
    # This is a placeholder for actual lunar cycle calculation.
    # In a real application, you'd use an astronomical library or API.
    # For now, let's simulate a 28-day cycle starting from a fixed date.
    
    # For demonstration, let's assume a full moon on 2026-05-01
    last_full_moon = datetime(2026, 5, 1, 0, 0, 0, tzinfo=MOSCOW_TZ)
    now = datetime.now(MOSCOW_TZ)

    delta = now - last_full_moon
    current_day = (delta.days % 28) + 1
    return current_day

# --- Initialize Database ---
def init_db():
    print("[DB] Starting database initialization...")
    try:
        with app.app_context():
            print("[DB] Creating tables...")
            db.create_all()
            print("[DB] Tables created successfully")
            print("[DB] Calling import_initial_data...")
            import_initial_data()
            print("[DB] import_initial_data completed")
    except Exception as e:
        print(f"[DB] Error in init_db: {e}")
        import traceback
        traceback.print_exc()

def import_initial_data():
    import json
    import os
    from marathon_data import MARATHON_DATA, TASKS_DATA

    print("[DB] Checking for initial data import...")

    try:
        # Check if database already has marathon
        existing_marathon = Marathon.query.first()
        if existing_marathon is not None:
            print("[DB] Marathon already exists, skipping import")
            return

        print("[DB] Importing built-in lunar marathon...")

        # Create marathon
        marathon = Marathon(
            name=MARATHON_DATA["name"],
            description=MARATHON_DATA["description"],
            goal=MARATHON_DATA["goal"],
            calendar_type=MARATHON_DATA.get("calendar_type"),
            is_published=MARATHON_DATA.get("is_published", True),
            min_rays=MARATHON_DATA.get("min_rays", 0),
            order_number=MARATHON_DATA.get("order_number", 1)
        )
        db.session.add(marathon)
        db.session.flush()  # Get the marathon ID

        print(f"[DB] Created marathon: {marathon.name}")

        # Import tasks
        if TASKS_DATA:
            for task_data in TASKS_DATA:
                task = DailyTask(
                    day_number=task_data["day_number"],
                    title=task_data["title"],
                    content=task_data["content"],
                    video_url=task_data.get("video_url"),
                    marathon_id=marathon.id
                )
                db.session.add(task)
            db.session.commit()
            print(f"[DB] Imported {len(TASKS_DATA)} tasks")

        # Try to load users from export.json if it exists
        if os.path.exists("export.json"):
            with open("export.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # Import users
            if "user" in data:
                for user_data in data["user"]:
                    is_admin = user_data.get("is_admin", False)
                    # Convert SQLite 1/0 to boolean
                    if isinstance(is_admin, int):
                        is_admin = bool(is_admin)

                    user = User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password=user_data["password"],
                        vk_id=user_data.get("vk_id"),
                        rays_balance=user_data.get("rays_balance", 0),
                        is_admin=is_admin
                    )
                    db.session.add(user)
                db.session.commit()
                print(f"[DB] Imported {len(data['user'])} users")

        # Import marathons
        if "marathon" in data:
            for m_data in data["marathon"]:
                marathon = Marathon(
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
            print(f"[DB] Imported {len(data['marathon'])} marathons")

        # Import daily tasks
        if "daily_task" in data:
            for task_data in data["daily_task"]:
                task = DailyTask(
                    day_number=task_data["day_number"],
                    title=task_data["title"],
                    content=task_data["content"],
                    video_url=task_data.get("video_url"),
                    marathon_id=task_data["marathon_id"]
                )
                db.session.add(task)
            db.session.commit()
            print(f"[DB] Imported {len(data['daily_task'])} tasks")

        print("[DB] Initial data import complete")
    except Exception as e:
        print(f"[DB] Error importing data: {e}")

init_db()

# --- Routes ---

@app.route("/")
def index():
    current_lunar_day = get_current_lunar_day()
    return render_template("index.html", current_lunar_day=current_lunar_day)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        vk_id = request.form.get("vk_id")

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, vk_id=vk_id)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash(f"Logged in as {user.username} (ID: {user.id})")
            session["user_id"] = user.id
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/task/<int:day_num>")
def daily_task(day_num):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    # Get marathon_id from session or use first available
    marathon_id = session.get("marathon_id")
    if not marathon_id:
        first_marathon = Marathon.query.first()
        if not first_marathon:
            flash("No marathons available")
            return redirect(url_for("index"))
        marathon_id = first_marathon.id
        session["marathon_id"] = marathon_id

    task = DailyTask.query.filter_by(day_number=day_num, marathon_id=marathon_id).first_or_404()

    # ЛОГИКА: Если у пользователя еще нет отчетов, значит это первый заход
    is_first_time = len(user.reports) == 0

    report_submitted = Report.query.filter_by(user_id=user.id, day_number=day_num, marathon_id=marathon_id).first() is not None
    return render_template("task.html", task=task, is_first_time=is_first_time, report_submitted=report_submitted, user_id=user.id, user_rays=user.rays_balance)

@app.route("/solfeggio")
def solfeggio():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    return render_template("solfeggio.html", user_id=user.id, user_rays=user.rays_balance)

@app.route("/neurogenesis")
def neurogenesis():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("neurogenesis.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы.")
    return redirect(url_for("index"))

@app.route("/notification-settings", methods=["GET", "POST"])
def notification_settings():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "GET":
        settings = NotificationSettings.query.filter_by(user_id=user.id).first()
        if not settings:
            settings = NotificationSettings(user_id=user.id)
            db.session.add(settings)
            db.session.commit()

        current_lunar_day = get_current_lunar_day()
        return render_template("notification_settings.html",
                             user_email=user.email,
                             current_lunar_day=current_lunar_day,
                             settings={
                                 'email_notifications': settings.email_notifications,
                                 'vk_notifications': settings.vk_notifications,
                                 'vk_user_id': settings.vk_user_id,
                                 'notification_time': settings.notification_time
                             })

    if request.method == "POST":
        data = request.get_json()
        settings = NotificationSettings.query.filter_by(user_id=user.id).first()
        if not settings:
            settings = NotificationSettings(user_id=user.id)

        settings.email_notifications = data.get('email_notifications', False)
        settings.vk_notifications = data.get('vk_notifications', False)
        settings.vk_user_id = data.get('vk_user_id', '')
        settings.notification_time = data.get('notification_time', '09:00')

        db.session.add(settings)
        db.session.commit()

        return jsonify({"success": True})

@app.route("/test-notification", methods=["POST"])
def test_notification():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])
    settings = NotificationSettings.query.filter_by(user_id=user.id).first()

    results = {"email": False, "vk": False}

    if settings and settings.email_notifications:
        subject = "🔔 Тестовое уведомление марафона"
        body = f"<p>Привет, {user.username}!</p><p>Это тестовое письмо для проверки работы уведомлений марафона.</p>"
        results["email"] = send_email(user.email, subject, body)

    if settings and settings.vk_notifications and settings.vk_user_id:
        message = f"🔔 Тестовое уведомление от марафона. Система напоминаний работает!"
        results["vk"] = send_vk_message(settings.vk_user_id, message)

    return jsonify({"success": True, "results": results})

@app.route("/api/marathons")
def api_marathons():
    marathons = Marathon.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'description': m.description,
        'goal': m.goal,
        'is_published': m.is_published,
        'min_rays': m.min_rays
    } for m in marathons])

@app.route("/marathons")
def marathons_list():
    marathons = Marathon.query.filter_by(is_published=True).all()
    if "user_id" not in session:
        return render_template("marathons.html", marathons=marathons, user_id=None, user_rays=0)

    user = User.query.get(session["user_id"])
    user_enrollments = MarathonEnrollment.query.filter_by(user_id=user.id).all()
    enrolled_marathon_ids = [e.marathon_id for e in user_enrollments]

    return render_template("marathons.html",
                          marathons=marathons,
                          user_id=user.id,
                          user_rays=user.rays_balance,
                          enrolled_marathon_ids=enrolled_marathon_ids)

@app.route("/marathons/<int:marathon_id>/join", methods=["POST"])
def join_marathon(marathon_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])
    marathon = Marathon.query.get(marathon_id)

    if not marathon:
        return jsonify({"error": "Marathon not found"}), 404

    if not marathon.is_published:
        return jsonify({"error": "Marathon not published"}), 403

    existing = MarathonEnrollment.query.filter_by(user_id=user.id, marathon_id=marathon_id).first()
    if existing and existing.is_active:
        return jsonify({"error": "Already enrolled"}), 409

    if marathon.min_rays > 0 and user.rays_balance < marathon.min_rays:
        return jsonify({"error": f"Need {marathon.min_rays} rays, have {user.rays_balance}"}), 402

    if existing:
        existing.is_active = True
        if marathon.min_rays > 0:
            user.rays_balance -= marathon.min_rays
    else:
        enrollment = MarathonEnrollment(user_id=user.id, marathon_id=marathon_id, is_active=True)
        db.session.add(enrollment)
        if marathon.min_rays > 0:
            user.rays_balance -= marathon.min_rays

    db.session.commit()
    return jsonify({"success": True, "rays_charged": marathon.min_rays})

@app.route("/marathons/<int:marathon_id>/task/<int:day_num>")
def marathon_task(marathon_id, day_num):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    marathon = Marathon.query.get(marathon_id)
    if not marathon or not marathon.is_published:
        return "Marathon not found", 404

    enrollment = MarathonEnrollment.query.filter_by(user_id=user.id, marathon_id=marathon_id, is_active=True).first()
    if not enrollment:
        return "Not enrolled", 403

    task = DailyTask.query.filter_by(day_number=day_num, marathon_id=marathon_id).first()
    if not task:
        return "Task not found", 404

    current_lunar_day = get_current_lunar_day()
    is_first_time = len(user.reports) == 0
    report_submitted = Report.query.filter_by(user_id=user.id, day_number=day_num, marathon_id=marathon_id).first() is not None

    return render_template("task.html",
                          task=task,
                          is_first_time=is_first_time,
                          report_submitted=report_submitted,
                          user_id=user.id,
                          user_rays=user.rays_balance,
                          marathon_id=marathon_id)

@app.route("/add_rays/<int:user_id>/<action>", methods=["POST"])
def add_rays(user_id, action):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    rays_amount = {
        "repost": 1,
        "comment": 1,
        "story": 1,
        "share": 1,
        "donate": 1,
        "topic": 2,
        "mining": 5,  # Майнинг золотой пыльцы = 5 лучиков
        "note": 0.00000000000000001  # Микро-пыльца за каждую ноту = 10^-17
    }

    if action not in rays_amount:
        return jsonify({"error": "Invalid action"}), 400

    rays = rays_amount[action]
    user.rays_balance += rays
    db.session.commit()

    return jsonify({
        "success": True,
        "rays_added": rays,
        "new_balance": user.rays_balance,
        "message": f"Добавлено {rays} лучиков!" if action != "mining" else "🔮 Золотая пыльца добыта! +5 лучиков!"
    })

@app.route("/submit_report/<int:user_id>/<int:day_num>", methods=["POST"])
def submit_report(user_id, day_num):
    report_text = request.form["report_text"]
    marathon_id = request.form.get("marathon_id", None)
    if marathon_id:
        marathon_id = int(marathon_id)

    now = datetime.now(MOSCOW_TZ)
    current_lunar_day = get_current_lunar_day()

    if day_num != current_lunar_day:
        flash("You can only submit reports for the current lunar day.")
        if marathon_id:
            return redirect(url_for("marathon_task", marathon_id=marathon_id, day_num=day_num))
        return redirect(url_for("daily_task", day_num=day_num))

    query_filter = {"user_id": user_id, "day_number": day_num}
    if marathon_id:
        query_filter["marathon_id"] = marathon_id

    existing_report = Report.query.filter_by(**query_filter).first()
    if existing_report:
        flash("You have already submitted a report for this day.")
        if marathon_id:
            return redirect(url_for("marathon_task", marathon_id=marathon_id, day_num=day_num))
        return redirect(url_for("daily_task", day_num=day_num))

    new_report = Report(user_id=user_id, day_number=day_num, marathon_id=marathon_id, report_text=report_text, submitted_at=now)
    db.session.add(new_report)

    user = User.query.get(user_id)
    if user:
        user.rays_balance += 1

    db.session.commit()
    flash("Report submitted successfully! You earned 1 Ray!")
    if marathon_id:
        return redirect(url_for("marathon_task", marathon_id=marathon_id, day_num=day_num))
    return redirect(url_for("daily_task", day_num=day_num))

# --- TEMPORARY: Make user admin ---
@app.route("/make-me-admin")
def make_me_admin():
    if "user_id" not in session:
        return "Not logged in", 401

    user = User.query.get(session["user_id"])
    if user and user.username.lower() == "mirdharm":
        user.is_admin = True
        db.session.commit()
        return "You are now admin! Go to /admin-secret-portal"
    return "Only mirdharm can use this", 403

# --- СЕКРЕТНЫЙ ПОРТАЛ АДМИНИСТРАТОРА ---
@app.route("/admin-secret-portal", methods=["GET", "POST"])
def admin_portal():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    # Проверка прав (флаг is_admin)
    if not user or not user.is_admin:
        return "У вас нет доступа к этому порталу", 403

    if request.method == "POST":
        day_to_update = int(request.form.get("day_number"))
        task_to_update = DailyTask.query.filter_by(day_number=day_to_update).first()
        if task_to_update:
            task_to_update.title = request.form.get("title")
            task_to_update.content = request.form.get("content")
            task_to_update.video_url = request.form.get("video_url")
            db.session.commit()
            flash(f"День {day_to_update} успешно обновлен!")
            return jsonify(success=True) # Return JSON for AJAX
        return jsonify(success=False), 404

    return render_template("admin_portal.html")

@app.route("/admin-secret-portal/task/<int:day_num>")
def get_task_details(day_num):
    task = DailyTask.query.filter_by(day_number=day_num).first()
    if task:
        return jsonify({"title": task.title, "content": task.content, "video_url": task.video_url})
    return jsonify({"error": "Task not found"}), 404

@app.route("/admin-secret-portal/marathons/new", methods=["GET", "POST"])
def new_marathon():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user or not user.is_admin:
        return "Access denied", 403

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        goal = request.form.get("goal")
        calendar_type = request.form.get("calendar_type")
        min_rays = int(request.form.get("min_rays", 0))

        marathon = Marathon(
            name=name,
            description=description,
            goal=goal,
            calendar_type=calendar_type,
            min_rays=min_rays,
            is_published=False
        )
        db.session.add(marathon)
        db.session.commit()

        flash(f"Marathon '{name}' created! Now add tasks.")
        return redirect(url_for("admin_marathon_tasks", marathon_id=marathon.id))

    return render_template("admin_marathon_form.html", marathon=None)

@app.route("/admin-secret-portal/marathons/<int:marathon_id>/tasks")
def admin_marathon_tasks(marathon_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user or not user.is_admin:
        return "Access denied", 403

    marathon = Marathon.query.get_or_404(marathon_id)
    return render_template("admin_marathon_tasks.html", marathon=marathon)

@app.route("/admin-secret-portal/marathons/<int:marathon_id>/task/<int:day_num>")
def get_marathon_task_details(marathon_id, day_num):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])
    if not user or not user.is_admin:
        return jsonify({"error": "Access denied"}), 403

    task = DailyTask.query.filter_by(day_number=day_num, marathon_id=marathon_id).first()
    if task:
        return jsonify({"title": task.title, "content": task.content, "video_url": task.video_url})
    return jsonify({"error": "Task not found"}), 404

@app.route("/admin-secret-portal/marathons/<int:marathon_id>/task/<int:day_num>", methods=["POST"])
def update_marathon_task(marathon_id, day_num):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])
    if not user or not user.is_admin:
        return jsonify({"error": "Access denied"}), 403

    task = DailyTask.query.filter_by(day_number=day_num, marathon_id=marathon_id).first()

    if task:
        task.title = request.form.get("title")
        task.content = request.form.get("content")
        task.video_url = request.form.get("video_url")
        db.session.commit()
        return jsonify({"success": True})
    else:
        title = request.form.get("title")
        if not title:
            return jsonify({"success": False, "error": "Title required"}), 400

        task = DailyTask(
            day_number=day_num,
            title=title,
            content=request.form.get("content", ""),
            video_url=request.form.get("video_url", ""),
            marathon_id=marathon_id
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({"success": True})

@app.route("/admin-secret-portal/marathons/<int:marathon_id>/publish", methods=["POST"])
def publish_marathon(marathon_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])
    if not user or not user.is_admin:
        return jsonify({"error": "Access denied"}), 403

    marathon = Marathon.query.get_or_404(marathon_id)
    task_count = DailyTask.query.filter_by(marathon_id=marathon_id).count()

    if task_count < 28:
        return jsonify({"error": f"Need 28 tasks, have {task_count}"}), 400

    marathon.is_published = request.get_json().get("publish", True)
    db.session.commit()

    status = "published" if marathon.is_published else "unpublished"
    return jsonify({"success": True, "status": status})

@app.route("/admin-secret-portal/send-broadcast", methods=["POST"])
def send_broadcast():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])
    if not user or not user.is_admin:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    email_subject = data.get('email_subject', '')
    email_body = data.get('email_body', '')
    vk_message = data.get('vk_message', '')

    # Get all users with notification settings enabled
    users_with_email = NotificationSettings.query.filter_by(email_notifications=True).all()
    users_with_vk = NotificationSettings.query.filter_by(vk_notifications=True).all()

    sent_count = 0
    email_count = 0
    vk_count = 0

    # Send emails
    for settings in users_with_email:
        if settings.user and email_subject and email_body:
            if send_email(settings.user.email, email_subject, email_body):
                email_count += 1

    # Send VK messages
    for settings in users_with_vk:
        if settings.vk_user_id and vk_message:
            if send_vk_message(settings.vk_user_id, vk_message):
                vk_count += 1

    sent_count = max(email_count, vk_count)

    # Save to database
    admin_msg = AdminMessage(
        title=data.get('title', 'Broadcast'),
        email_subject=email_subject,
        email_body=email_body,
        vk_message=vk_message,
        sent_at=datetime.now(MOSCOW_TZ),
        recipient_count=sent_count
    )
    db.session.add(admin_msg)
    db.session.commit()

    return jsonify({
        "success": True,
        "sent_count": sent_count,
        "email_count": email_count,
        "vk_count": vk_count
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not DailyTask.query.first():
            for i in range(1, 29):
                new_task = DailyTask(day_number=i, title=f"Day {i} Task", 
                                     content=f"This is the task for lunar day {i}. Complete it to earn rays!",
                                     video_url=f"https://vk.com/video_example_{i}")
                db.session.add(new_task)
            db.session.commit()
    app.run(debug=True)
