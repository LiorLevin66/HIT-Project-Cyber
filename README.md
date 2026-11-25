# Comunication_LTD - Part A (secure version)

Full explanation of every file and function (in Hebrew): [CODE_EXPLANATION.md](CODE_EXPLANATION.md)

## Project structure

```
HIT-Project-Cyber/
├── backend/                     Server side (Python + Flask)
│   ├── app.py                   Routes of all the screens
│   ├── config.py                Configuration file (password policy, DB, mail)
│   ├── security.py              HMAC + Salt, password policy check, SHA-1 reset code
│   ├── db.py                    All the SQL queries (with parameters)
│   ├── mailer.py                Sending the reset code by email
│   ├── forbidden_passwords.txt  Dictionary of forbidden passwords
│   └── requirements.txt
└── frontend/                    Client side
    ├── templates/               HTML pages
    │   ├── base.html
    │   ├── register.html        1. Register
    │   ├── change_password.html 2. Change password
    │   ├── login.html           3. Login
    │   ├── system.html          4. System screen (customers)
    │   ├── forgot.html          5. Forgot password
    │   ├── forgot_verify.html   5. Enter the code from the email
    │   └── password_rules.html  Password requirements list (used in 1 + 2)
    └── static/
        ├── style.css
        └── password.js          Live check of the password requirements
```

## How to run

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

By default the database is SQLite (`backend/comunication.db`), created on the first run.

## Running with MySQL

```sql
CREATE DATABASE comunication_ltd CHARACTER SET utf8mb4;
```

```bash
set DB_BACKEND=mysql
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
python app.py
```

## Sending the email

Without SMTP settings the reset code is written to `backend/outbox.log`.
To really send it (for example with Gmail and an App Password):

```bash
set SMTP_HOST=smtp.gmail.com
set SMTP_USER=your_mail@gmail.com
set SMTP_PASSWORD=your_app_password
set SMTP_SENDER=your_mail@gmail.com
```

## Configuration file (backend/config.py)

| Setting | Value |
|---|---|
| Password length | `PASSWORD_MIN_LENGTH = 10` |
| Complex password | `PASSWORD_REQUIRE_UPPER / LOWER / DIGIT / SPECIAL = True` |
| History | `PASSWORD_HISTORY = 3` |
| Dictionary | `forbidden_passwords.txt` |
| Login attempts | `MAX_LOGIN_ATTEMPTS = 3` |
