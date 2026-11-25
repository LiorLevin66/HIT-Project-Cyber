"""
Comunication_LTD - Part A
Flask server. The HTML pages are in ../frontend
"""
import os
import time

from flask import Flask, redirect, render_template, request, session, url_for

import config
import db
import mailer
import security

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
    static_folder=os.path.join(FRONTEND_DIR, "static"),
)
app.secret_key = config.SECRET_KEY
app.jinja_env.globals["settings"] = config   # lets the HTML show the password rules


def is_password_in_history(user_id, password):
    """Checks if the password is one of the last PASSWORD_HISTORY passwords."""
    for old in db.get_password_history(user_id, config.PASSWORD_HISTORY):
        if security.check_password(password, old["salt"], old["password_hash"]):
            return True
    return False


def validate_new_password(user_id, password, confirm):
    errors = security.check_policy(password)
    if is_password_in_history(user_id, password):
        errors.append(f"For security reasons, you cannot reuse any of your last {config.PASSWORD_HISTORY} passwords.")
    if password != confirm:
        errors.append("The password confirmation does not match.")
    return errors


def save_new_password(user_id, password):
    salt = security.new_salt()
    db.update_password(user_id, security.hash_password(password, salt), salt)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("system"))
    return redirect(url_for("login"))


# ---------- 1. Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    username = email = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm = request.form["confirm"]

        if not username:
            errors.append("Please enter a username.")
        elif db.get_user_by_username(username):
            errors.append("This username is already taken. Please choose a different one.")
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email address.")
        elif db.get_user_by_email(email):
            errors.append("An account with this email address already exists.")
        errors += security.check_policy(password)
        if password != confirm:
            errors.append("The password confirmation does not match.")

        if not errors:
            salt = security.new_salt()
            db.create_user(username, email, security.hash_password(password, salt), salt)
            return render_template("login.html", message="Your account has been created successfully. Please log in.")
    return render_template("register.html", errors=errors, username=username, email=email)


# ---------- 3. Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = db.get_user_by_username(username)
        now = int(time.time())

        if not user:
            error = "No account was found with this username."
        elif user["locked_until"] > now:
            error = "This account is temporarily locked due to multiple failed login attempts. Please try again later."
        elif security.check_password(password, user["salt"], user["password_hash"]):
            db.update_login_attempts(user["id"], 0, 0)
            session["user_id"] = user["id"]
            return redirect(url_for("system"))
        else:
            attempts = user["failed_attempts"] + 1
            if attempts >= config.MAX_LOGIN_ATTEMPTS:
                db.update_login_attempts(user["id"], 0, now + config.LOCKOUT_MINUTES * 60)
                error = f"Too many failed login attempts. Your account has been locked for {config.LOCKOUT_MINUTES} minutes."
            else:
                db.update_login_attempts(user["id"], attempts, 0)
                left = config.MAX_LOGIN_ATTEMPTS - attempts
                error = f"Incorrect password. You have {left} attempt{'s' if left != 1 else ''} remaining."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- 4. System screen ----------
@app.route("/system", methods=["GET", "POST"])
def system():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = db.get_user_by_id(session["user_id"])
    message = None
    error = None
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        address = request.form["address"].strip()
        if not name:
            error = "Please enter the customer's name."
        else:
            db.add_customer(name, email, phone, address)
            message = f"Customer \"{name}\" was added successfully."
    return render_template("system.html", user=user, message=message, error=error,
                           customers=db.get_customers())


# ---------- 2. Change password ----------
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = db.get_user_by_id(session["user_id"])
    errors = []
    if request.method == "POST":
        current = request.form["current"]
        new = request.form["password"]
        confirm = request.form["confirm"]
        if not security.check_password(current, user["salt"], user["password_hash"]):
            errors.append("The current password you entered is incorrect.")
        errors += validate_new_password(user["id"], new, confirm)
        if not errors:
            save_new_password(user["id"], new)
            return render_template("change_password.html", user=user, reset=False,
                                   errors=[], message="Your password has been changed successfully.")
    return render_template("change_password.html", user=user, reset=False, errors=errors)


# ---------- 5. Forgot password ----------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    error = None
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = db.get_user_by_email(email)
        if not user:
            error = "No account is associated with this email address."
        else:
            code = security.generate_reset_code()
            db.save_reset_code(user["id"], code)
            mailer.send_mail(email, "Comunication_LTD - Password reset code",
                             f"Hello {user['username']},\n\nYour password reset code is: {code}\n\n"
                             "If you did not request a password reset, please ignore this email.\n")
            session["reset_user_id"] = user["id"]
            return redirect(url_for("forgot_verify"))
    return render_template("forgot.html", error=error)


@app.route("/forgot/verify", methods=["GET", "POST"])
def forgot_verify():
    user_id = session.get("reset_user_id")
    if not user_id:
        return redirect(url_for("forgot"))
    error = None
    if request.method == "POST":
        code = request.form["code"].strip().lower()
        record = db.find_reset_code(user_id, code)
        if record:
            db.mark_reset_code_used(record["id"])
            session["reset_verified"] = True
            return redirect(url_for("reset_password"))
        error = "The verification code is invalid or has already been used."
    return render_template("forgot_verify.html", error=error)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    user_id = session.get("reset_user_id")
    if not user_id or not session.get("reset_verified"):
        return redirect(url_for("forgot"))
    errors = []
    if request.method == "POST":
        new = request.form["password"]
        confirm = request.form["confirm"]
        errors = validate_new_password(user_id, new, confirm)
        if not errors:
            save_new_password(user_id, new)
            session.clear()
            return render_template("login.html", message="Your password has been reset successfully. Please log in with your new password.")
    return render_template("change_password.html", reset=True, errors=errors)


if __name__ == "__main__":
    db.init_db()
    app.run(port=5000)
