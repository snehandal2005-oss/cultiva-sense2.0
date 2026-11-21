
from flask import jsonify
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from pathlib import Path
import sqlite3
import re
import math

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


DATABASE = Path(__file__).parent / "farmers.db"


@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")



@app.route("/login.html", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = sqlite3.connect(DATABASE)
        connection.row_factory = sqlite3.Row

        farmer = connection.execute(
            "SELECT * FROM farmers WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if farmer and check_password_hash(
            farmer["password_hash"], password
        ):
            session.clear()
            session["farmer_id"] = farmer["id"]
            session["farmer_name"] = farmer["name"]

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")



@app.route("/register.html", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        farm_size = request.form.get("farm_size", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([name, email, phone, location,
                    farm_size, password, confirm_password]):
            return render_template(
                "register.html",
                error="Please fill in all fields."
            )

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return render_template(
                "register.html",
                error="Please enter a valid email address."
            )

        if not re.fullmatch(r"[0-9]{10}", phone):
            return render_template(
                "register.html",
                error="Enter a valid 10-digit phone number."
            )

        try:
            farm_size = float(farm_size)

            if not math.isfinite(farm_size) or farm_size <= 0:
                raise ValueError

        except ValueError:
            return render_template(
                "register.html",
                error="Enter a valid farm size."
            )

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must have at least 8 characters."
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        password_hash = generate_password_hash(
    password,
    method="pbkdf2:sha256:600000"
)
        connection = sqlite3.connect(DATABASE)
        try:
            connection.execute("""
                INSERT INTO farmers
                (name, email, phone, location,
                 farm_size, password_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name, email, phone, location,
                farm_size, password_hash
            ))

            connection.commit()

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="This email is already registered."
            )

        finally:
            connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")




@app.route("/dashboard.html")
def dashboard():
    if "farmer_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        farmer_name=session["farmer_name"]
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/weather.html")
def weather():
    if "farmer_id" not in session:
        return redirect(url_for("login"))

    return render_template("weather.html")


@app.route("/analyze-leaf", methods=["POST"])
def analyze_leaf():
    if "farmer_id" not in session:
        return jsonify({"error": "Please log in first."}), 401

    file = request.files.get("leaf")

    if not file:
        return jsonify({"error": "No image uploaded."}), 400

    if len(file.read()) > 5 * 1024 * 1024:
        return jsonify({"error": "Maximum image size is 5 MB."}), 400

    file.seek(0)

    try:
        image = Image.open(BytesIO(file.read()))
        image.verify()
    except Exception:
        return jsonify({"error": "Invalid image."}), 400

    return jsonify({
        "message": "Image received successfully. AI model not connected yet."
    })
if __name__ == "__main__":
    app.run(debug=True, port=5001)
