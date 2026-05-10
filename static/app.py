from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pytz # For timezone aware datetimes
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "lyunny_marafon_2026_super_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///marathon.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define timezone for consistency
MOSCOW_TZ = pytz.timezone("Europe/Moscow")

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False) # Added password field
    vk_id = db.Column(db.Text)
    rays_balance = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)


# Новая модель Марафона
class Marathon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    goal = db.Column(db.Text)
    calendar_type = db.Column(db.String(50))  # lunar, human_design, mayan, solar, etc.
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    regularity = db.Column(db.String(50))  # daily, weekly, custom
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
    report_text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now(MOSCOW_TZ))

    user = db.relationship("User", backref="reports")

# We'll create tables explicitly in the __main__ block or with a separate script
# @app.before_request
# def create_tables():
#     db.create_all()

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
        
        new_user = User(username=username, email=email, password=password, vk_id=vk_id) # Added password
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Placeholder for login logic - A real app would have proper authentication
    # For now, let's assume successful login for any user that exists
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password: # Basic password check
            flash(f"Logged in as {user.username} (ID: {user.id})")
            # Store user ID in session
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
    task = DailyTask.query.get_or_404(day_num)
    
    # ЛОГИКА: Если у пользователя еще нет отчетов, значит это первый заход
    is_first_time = len(user.reports) == 0
    
    report_submitted = Report.query.filter_by(user_id=user.id, day_number=day_num).first() is not None
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
    
    now = datetime.now(MOSCOW_TZ)
    current_lunar_day = get_current_lunar_day()
    
    if day_num != current_lunar_day:
        flash("You can only submit reports for the current lunar day.")
        return redirect(url_for("daily_task", day_num=day_num))

    # Check deadline: before 00:00 of the next day
    # This assumes that a day in the marathon ends at 00:00 Moscow time
    # Need to calculate the specific deadline for the current lunar day
    # For simplicity, let's assume report can be submitted anytime on the current lunar day
    # A more robust solution would track the start of the current lunar day

    existing_report = Report.query.filter_by(user_id=user_id, day_number=day_num).first()
    if existing_report:
        flash("You have already submitted a report for this day.")
        return redirect(url_for("daily_task", day_num=day_num))

    new_report = Report(user_id=user_id, day_number=day_num, report_text=report_text, submitted_at=now)
    db.session.add(new_report)
    
    user = User.query.get(user_id)
    if user:
        user.rays_balance += 1

    db.session.commit()
    flash("Report submitted successfully! You earned 1 Ray!")
    return redirect(url_for("daily_task", day_num=day_num))

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
