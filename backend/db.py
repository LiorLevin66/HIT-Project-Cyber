"""
All the SQL of the project is in this file.
Every query uses parameters (?) and not string concatenation.
"""
import sqlite3
import time

import config

USE_MYSQL = config.DB_BACKEND == "mysql"


def get_connection():
    if USE_MYSQL:
        import pymysql
        return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, charset="utf8mb4", **config.MYSQL)
    conn = sqlite3.connect(config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def execute(sql, params=(), fetch=None):
    if USE_MYSQL:
        sql = sql.replace("?", "%s")   # pymysql uses %s instead of ?
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        if fetch == "one":
            row = cur.fetchone()
            result = dict(row) if row else None
        elif fetch == "all":
            result = [dict(r) for r in cur.fetchall()]
        else:
            result = cur.lastrowid
        conn.commit()
        return result
    finally:
        conn.close()


def init_db():
    pk = "INT AUTO_INCREMENT PRIMARY KEY" if USE_MYSQL else "INTEGER PRIMARY KEY AUTOINCREMENT"
    execute(f"""CREATE TABLE IF NOT EXISTS users (
        id {pk},
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(120) NOT NULL UNIQUE,
        password_hash VARCHAR(64) NOT NULL,
        salt VARCHAR(32) NOT NULL,
        failed_attempts INT NOT NULL DEFAULT 0,
        locked_until BIGINT NOT NULL DEFAULT 0
    )""")
    execute(f"""CREATE TABLE IF NOT EXISTS password_history (
        id {pk},
        user_id INT NOT NULL,
        password_hash VARCHAR(64) NOT NULL,
        salt VARCHAR(32) NOT NULL
    )""")
    execute(f"""CREATE TABLE IF NOT EXISTS reset_codes (
        id {pk},
        user_id INT NOT NULL,
        code VARCHAR(40) NOT NULL,
        used INT NOT NULL DEFAULT 0
    )""")
    execute(f"""CREATE TABLE IF NOT EXISTS customers (
        id {pk},
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120),
        phone VARCHAR(30),
        address VARCHAR(200)
    )""")


# ---------- users ----------
def create_user(username, email, password_hash, salt):
    user_id = execute(
        "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, salt),
    )
    add_password_history(user_id, password_hash, salt)


def get_user_by_username(username):
    return execute("SELECT * FROM users WHERE username = ?", (username,), "one")


def get_user_by_email(email):
    return execute("SELECT * FROM users WHERE email = ?", (email,), "one")


def get_user_by_id(user_id):
    return execute("SELECT * FROM users WHERE id = ?", (user_id,), "one")


def update_login_attempts(user_id, failed_attempts, locked_until):
    execute(
        "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?",
        (failed_attempts, locked_until, user_id),
    )


# ---------- passwords ----------
def add_password_history(user_id, password_hash, salt):
    execute(
        "INSERT INTO password_history (user_id, password_hash, salt) VALUES (?, ?, ?)",
        (user_id, password_hash, salt),
    )


def get_password_history(user_id, limit):
    return execute(
        "SELECT password_hash, salt FROM password_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
        "all",
    )


def update_password(user_id, password_hash, salt):
    execute(
        "UPDATE users SET password_hash = ?, salt = ?, failed_attempts = 0, locked_until = 0 WHERE id = ?",
        (password_hash, salt, user_id),
    )
    add_password_history(user_id, password_hash, salt)


# ---------- reset codes ----------
def save_reset_code(user_id, code):
    execute("INSERT INTO reset_codes (user_id, code) VALUES (?, ?)", (user_id, code))


def find_reset_code(user_id, code):
    return execute(
        "SELECT * FROM reset_codes WHERE user_id = ? AND code = ? AND used = 0",
        (user_id, code),
        "one",
    )


def mark_reset_code_used(code_id):
    execute("UPDATE reset_codes SET used = 1 WHERE id = ?", (code_id,))


# ---------- customers ----------
def add_customer(name, email, phone, address):
    execute(
        "INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)",
        (name, email, phone, address),
    )


def get_customers():
    return execute("SELECT * FROM customers ORDER BY id DESC", (), "all")
