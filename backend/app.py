import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from config import (
    FRONTEND_BASE_URL,
    SECRET_KEY,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME
)
from database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# Allow frontend running on Live Server
CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [
                "http://127.0.0.1:5500",
                "http://localhost:5500"
            ]
        }
    }
)


def admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not session.get("is_admin"):

            return jsonify({
                "success": False,
                "message": "Administrator login required"
            }), 401

        return view_function(*args, **kwargs)

    return wrapped_view


def user_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not session.get("user_id"):

            return jsonify({
                "success": False,
                "message": "User login required"
            }), 401

        return view_function(*args, **kwargs)

    return wrapped_view


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "Career Guidance Backend is Running!"
    }), 200


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        # Get form data

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        education = data.get("education")
        password = data.get("password")


        # Check required fields

        if not name or not email or not password:

            return jsonify({
                "success": False,
                "message": "Name, email and password are required"
            }), 400


        # Connect to database

        connection = get_db_connection()


        if connection is None:

            return jsonify({
                "success": False,
                "message": "Database connection failed"
            }), 500


        cursor = None


        try:

            cursor = connection.cursor(dictionary=True)


            # Check whether email already exists

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )


            existing_user = cursor.fetchone()


            if existing_user:

                return jsonify({
                    "success": False,
                    "message": "Email already registered"
                }), 409


            # Hash password

            hashed_password = generate_password_hash(password)


            # Insert user
            # ADDED phone and education

            cursor.execute(
                """
                INSERT INTO users
                (name, email, phone, education, password)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    name,
                    email,
                    phone,
                    education,
                    hashed_password
                )
            )


            connection.commit()


            # Get newly created user ID

            user_id = cursor.lastrowid


            # Send successful response

            return jsonify({

                "success": True,

                "message": "Registration successful",

                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "education": education
                }

            }), 201


        except Exception as e:

            connection.rollback()

            print("Registration database error:", e)


            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


        finally:

            if cursor:
                cursor.close()

            connection.close()


    except Exception as e:

        print("Registration error:", e)


        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        email = data.get("email")
        password = data.get("password")


        # Validate input

        if not email or not password:

            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400


        # Database connection

        connection = get_db_connection()


        if connection is None:

            return jsonify({
                "success": False,
                "message": "Database connection failed"
            }), 500


        cursor = None


        try:

            cursor = connection.cursor(dictionary=True)


            # Find user

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )


            user = cursor.fetchone()


            # Check password

            if user and check_password_hash(
                user["password"],
                password
            ):

                session.clear()
                session["user_id"] = user["id"]


                return jsonify({

                    "success": True,

                    "message": "Login successful",

                    "user": {

                        "id": user["id"],

                        "name": user["name"],

                        "email": user["email"],

                        # ADDED phone
                        "phone": user["phone"],

                        # ADDED education
                        "education": user["education"]

                    }

                }), 200


            # Invalid login

            return jsonify({

                "success": False,

                "message": "Invalid email or password"

            }), 401


        except Exception as e:

            print("Login database error:", e)


            return jsonify({

                "success": False,

                "message": str(e)

            }), 500


        finally:

            if cursor:
                cursor.close()

            connection.close()


    except Exception as e:

        print("Login error:", e)


        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# =========================================================
# RUN SERVER
# =========================================================

@app.route("/password-reset/request", methods=["POST"])
def request_password_reset():

    data = request.get_json(silent=True)
    email = data.get("email", "").strip() if isinstance(data, dict) else ""

    if not email:

        return jsonify({
            "success": False,
            "message": "Enter your account email address"
        }), 400

    if not (SMTP_HOST and SMTP_FROM):

        return jsonify({
            "success": False,
            "message": "Password reset email is not configured on the server. Set SMTP_HOST and SMTP_FROM."
        }), 503

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:

            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
            cursor.execute(
                "DELETE FROM password_reset_tokens WHERE user_id = %s",
                (user["id"],)
            )
            expires_at = datetime.now() + timedelta(minutes=30)
            cursor.execute(
                """
                INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
                VALUES (%s, %s, %s)
                """,
                (user["id"], token_hash, expires_at)
            )
            connection.commit()

            reset_link = (
                f"{FRONTEND_BASE_URL}/reset-password.html?token={token}"
            )
            email_message = EmailMessage()
            email_message["Subject"] = "Reset your CareerGuide password"
            email_message["From"] = SMTP_FROM
            email_message["To"] = user["email"]
            email_message.set_content(
                "Use this link to reset your CareerGuide password. "
                "It expires in 30 minutes and can only be used once:\n\n"
                f"{reset_link}\n\n"
                "If you did not request a password reset, ignore this email."
            )

            try:

                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
                    smtp.starttls()

                    if SMTP_USERNAME:
                        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)

                    smtp.send_message(email_message)

            except Exception:

                cursor.execute(
                    "DELETE FROM password_reset_tokens WHERE token_hash = %s",
                    (token_hash,)
                )
                connection.commit()
                app.logger.exception("Could not send password reset email")

                return jsonify({
                    "success": False,
                    "message": "Could not send the reset email. Check the server SMTP settings."
                }), 502

        return jsonify({
            "success": True,
            "message": "If an account exists for that email, a password reset link has been sent."
        }), 200

    except Exception:

        connection.rollback()
        app.logger.exception("Could not process password reset request")

        return jsonify({
            "success": False,
            "message": "Could not process the password reset request"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/password-reset/confirm", methods=["POST"])
def confirm_password_reset():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        data = {}

    token = data.get("token")
    password = data.get("password")

    if not isinstance(token, str) or not token:

        return jsonify({
            "success": False,
            "message": "The reset link is invalid or expired"
        }), 400

    if not isinstance(password, str) or len(password) < 8:

        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters"
        }), 400

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, user_id, expires_at
            FROM password_reset_tokens
            WHERE token_hash = %s
            """,
            (token_hash,)
        )
        reset_token = cursor.fetchone()

        expires_at = reset_token["expires_at"] if reset_token else None
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                expires_at = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")

        if not reset_token or expires_at <= datetime.now():

            if reset_token:
                cursor.execute(
                    "DELETE FROM password_reset_tokens WHERE token_hash = %s",
                    (token_hash,)
                )
                connection.commit()

            return jsonify({
                "success": False,
                "message": "The reset link is invalid or expired"
            }), 400

        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (generate_password_hash(password), reset_token["user_id"])
        )
        cursor.execute(
            "DELETE FROM password_reset_tokens WHERE user_id = %s",
            (reset_token["user_id"],)
        )
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Password updated. You can now sign in."
        }), 200

    except Exception:

        connection.rollback()
        app.logger.exception("Could not reset account password")

        return jsonify({
            "success": False,
            "message": "Could not update the password"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        data = {}

    email = data.get("email")
    password = data.get("password")

    if (
        not isinstance(email, str)
        or not isinstance(password, str)
        or not email.strip()
        or not password
    ):

        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    email = email.strip()

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, email, password
            FROM admins
            WHERE email = %s
            """,
            (email,)
        )
        admin = cursor.fetchone()

        if not admin or not check_password_hash(admin["password"], password):

            return jsonify({
                "success": False,
                "message": "Invalid administrator email or password"
            }), 401

        session.clear()
        session["is_admin"] = True
        session["admin_id"] = admin["id"]
        session["admin_name"] = admin["name"]
        session["admin_email"] = admin["email"]

        return jsonify({
            "success": True,
            "message": "Admin login successful",
            "admin": {
                "name": admin["name"],
                "email": admin["email"]
            }
        }), 200

    except Exception:

        app.logger.exception("Admin login failed while querying the database")

        return jsonify({
            "success": False,
            "message": "Could not verify administrator credentials"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/admin/session", methods=["GET"])
@admin_required
def admin_session():

    return jsonify({
        "success": True,
        "admin": {
            "id": session.get("admin_id"),
            "name": session.get("admin_name", ""),
            "email": session.get("admin_email", "")
        }
    }), 200


@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():

    session.clear()

    return jsonify({"success": True}), 200


@app.route("/admin/dashboard-data", methods=["GET"])
@admin_required
def admin_dashboard_data():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total_users = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT realistic_score, investigative_score, artistic_score,
                   social_score, enterprising_score, conventional_score
            FROM assessment_results
            """
        )
        assessment_rows = cursor.fetchall()
        riasec_counts = {
            score_type: 0
            for score_type in ("R", "I", "A", "S", "E", "C")
        }

        for row in assessment_rows:

            row_scores = {
                "R": row["realistic_score"],
                "I": row["investigative_score"],
                "A": row["artistic_score"],
                "S": row["social_score"],
                "E": row["enterprising_score"],
                "C": row["conventional_score"]
            }
            highest_score = max(row_scores.values())

            for score_type, score in row_scores.items():
                if score == highest_score:
                    riasec_counts[score_type] += 1

        return jsonify({
            "success": True,
            "totalUsers": total_users,
            "totalAssessments": len(assessment_rows),
            "riasecCounts": riasec_counts,
            "admin": {
                "name": session.get("admin_name", "Administrator"),
                "email": session.get("admin_email", "")
            }
        }), 200

    except Exception:

        app.logger.exception("Could not load admin dashboard data")

        return jsonify({
            "success": False,
            "message": "Could not load dashboard data"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/logout", methods=["POST"])
@user_required
def logout():

    session.pop("user_id", None)

    return jsonify({"success": True}), 200


@app.route("/profile", methods=["GET", "PUT"])
@user_required
def profile():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        if request.method == "GET":

            cursor.execute(
                """
                SELECT id, name, email, phone, education
                FROM users
                WHERE id = %s
                """,
                (session["user_id"],)
            )
            user = cursor.fetchone()

            if not user:

                session.pop("user_id", None)

                return jsonify({
                    "success": False,
                    "message": "User account was not found"
                }), 404

            return jsonify({"success": True, "user": user}), 200

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            data = {}

        name = data.get("name")
        phone = data.get("phone", "")
        education = data.get("education", "")

        if (
            not isinstance(name, str)
            or not name.strip()
            or not isinstance(phone, str)
            or not isinstance(education, str)
        ):

            return jsonify({
                "success": False,
                "message": "Name, phone and education must be valid text"
            }), 400

        cursor.execute(
            """
            UPDATE users
            SET name = %s, phone = %s, education = %s
            WHERE id = %s
            """,
            (name.strip(), phone.strip(), education.strip(), session["user_id"])
        )
        connection.commit()

        cursor.execute(
            """
            SELECT id, name, email, phone, education
            FROM users
            WHERE id = %s
            """,
            (session["user_id"],)
        )

        return jsonify({
            "success": True,
            "user": cursor.fetchone()
        }), 200

    except Exception:

        connection.rollback()
        app.logger.exception("Could not load or update the user profile")

        return jsonify({
            "success": False,
            "message": "Could not save profile data"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/assessment", methods=["POST"])
@user_required
def save_assessment():

    data = request.get_json(silent=True)
    score_types = ("R", "I", "A", "S", "E", "C")

    if not isinstance(data, dict) or not isinstance(data.get("scores"), dict):

        return jsonify({
            "success": False,
            "message": "Assessment scores are required"
        }), 400

    scores = data["scores"]

    if any(
        type(scores.get(score_type)) is not int
        or scores[score_type] < 0
        or scores[score_type] > 20
        for score_type in score_types
    ):

        return jsonify({
            "success": False,
            "message": "Each RIASEC score must be between 0 and 20"
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO assessment_results
                (user_id, realistic_score, investigative_score,
                 artistic_score, social_score, enterprising_score,
                 conventional_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session["user_id"], scores["R"], scores["I"],
                scores["A"], scores["S"], scores["E"], scores["C"]
            )
        )
        connection.commit()

        return jsonify({"success": True, "scores": scores}), 201

    except Exception:

        connection.rollback()
        app.logger.exception("Could not save assessment results")

        return jsonify({
            "success": False,
            "message": "Could not save assessment results"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/assessment/latest", methods=["GET"])
@user_required
def latest_assessment():

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT realistic_score, investigative_score, artistic_score,
                   social_score, enterprising_score, conventional_score,
                   created_at
            FROM assessment_results
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": True, "assessment": None}), 200

        return jsonify({
            "success": True,
            "assessment": {
                "scores": {
                    "R": row["realistic_score"],
                    "I": row["investigative_score"],
                    "A": row["artistic_score"],
                    "S": row["social_score"],
                    "E": row["enterprising_score"],
                    "C": row["conventional_score"]
                },
                "completedAt": row["created_at"].isoformat()
            }
        }), 200

    except Exception:

        app.logger.exception("Could not load assessment results")

        return jsonify({
            "success": False,
            "message": "Could not load assessment results"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/courses", methods=["GET"])
def course_catalog():

    riasec_type = request.args.get("type", "").upper()

    if riasec_type not in ("R", "I", "A", "S", "E", "C"):

        return jsonify({
            "success": False,
            "message": "A valid RIASEC type is required"
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT riasec_type, category_name, category_description,
                   name, icon, level, duration, description
            FROM course_catalog
            WHERE riasec_type = %s
            ORDER BY display_order, name
            """,
            (riasec_type,)
        )
        rows = cursor.fetchall()

        return jsonify({
            "success": True,
            "riasecType": riasec_type,
            "categoryName": rows[0]["category_name"] if rows else "",
            "categoryDescription": rows[0]["category_description"] if rows else "",
            "courses": [
                {
                    "name": row["name"],
                    "icon": row["icon"],
                    "level": row["level"],
                    "duration": row["duration"],
                    "description": row["description"]
                }
                for row in rows
            ]
        }), 200

    except Exception:

        app.logger.exception("Could not load the course catalog")

        return jsonify({
            "success": False,
            "message": "Could not load courses from the database"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


@app.route("/contact", methods=["POST"])
def submit_contact_message():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        data = {}

    fields = ("name", "email", "subject", "message")

    if any(
        not isinstance(data.get(field), str) or not data[field].strip()
        for field in fields
    ):

        return jsonify({
            "success": False,
            "message": "Name, email, subject and message are required"
        }), 400

    connection = get_db_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
            """,
            tuple(data[field].strip() for field in fields)
        )
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Your message has been received"
        }), 201

    except Exception:

        connection.rollback()
        app.logger.exception("Could not save contact message")

        return jsonify({
            "success": False,
            "message": "Could not save your message"
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )