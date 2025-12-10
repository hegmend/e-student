from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "somesecretkey"

# --- CREATE DB ---
def init_db():
    # Змінюємо 'database.db' на 'students.db' для коректності з вашим файлом у VS Code
    with sqlite3.connect("students.db") as conn: 
        c = conn.cursor()
        # Примітка: Ваша таблиця називається 'users', і це співпадає з вашим .db файлом
        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            group_name TEXT
        )
        """)
        conn.commit()

init_db()

# --- Helper для підключення ---
def get_connection():
    # Змінюємо 'database.db' на 'students.db'
    return sqlite3.connect("students.db", timeout=10)

# --- ROUTES ---

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        group_name = request.form["group"]

        try:
            with get_connection() as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (name, email, password, group_name) VALUES (?, ?, ?, ?)",
                    (name, email, password, group_name)
                )
                conn.commit()
            return redirect("/login")
        except sqlite3.OperationalError as e:
            return f"Помилка бази даних: {e}"
        except sqlite3.IntegrityError:
            return "Користувач з таким email вже існує"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = c.fetchone()

        if user:
            # Тут user - це кортеж: (id, name, email, password, group_name)
            session["user"] = user 
            return redirect("/dashboard")
        else:
            return "Неправильний логін або пароль"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    return render_template("dashboard.html", user=user)

# ======================================================
# НОВІ МАРШРУТИ ДЛЯ ПРОФІЛЮ ТА НОВИН
# ======================================================

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")
    
    # Інформація про користувача потрібна для заповнення profile.html
    user = session["user"]
    return render_template("profile.html", user=user)

@app.route("/news")
def news():
    if "user" not in session:
        return redirect("/login")
        
    # Інформація про користувача потрібна для навігації в news.html
    user = session["user"]
    return render_template("news.html", user=user)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# --- RUN APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)