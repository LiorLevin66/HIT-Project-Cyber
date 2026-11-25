# Comunication_LTD – הסבר מלא על הקוד (חלק א׳)

## סקירה כללית

המערכת היא אתר ווב ב-Python עם Flask, מחולקת לשתי תיקיות: **backend** מריץ את הלוגיקה ואת מסד הנתונים, ו-**frontend** מכיל את מה שהמשתמש רואה בדפדפן.

```
HIT-Project-Cyber/
├── README.md
├── backend/
│   ├── app.py                  נתיבים (routes) של כל המסכים
│   ├── config.py               קובץ הקונפיגורציה
│   ├── security.py             HMAC + Salt, מדיניות סיסמה, קוד SHA-1
│   ├── db.py                   כל שאילתות ה-SQL
│   ├── mailer.py               שליחת מייל
│   ├── forbidden_passwords.txt מילון סיסמאות אסורות
│   └── requirements.txt        ספריות להתקנה
└── frontend/
    ├── templates/              דפי HTML
    └── static/                 style.css, password.js
```

**איך החלקים מתחברים:**

1. הדפדפן שולח בקשה לכתובת, למשל `/login`.
2. הפונקציה המתאימה ב-`app.py` מקבלת את הבקשה.
3. היא משתמשת ב-`security.py` לבדיקות הסיסמה, ב-`db.py` לקריאה וכתיבה למסד הנתונים וב-`config.py` להגדרות.
4. בסוף היא מחזירה דף HTML מ-`frontend/templates`, והדפדפן טוען את העיצוב והסקריפט מ-`frontend/static`.

**הרצה:**

```bash
cd backend
pip install -r requirements.txt
python app.py
```

אחר כך פותחים בדפדפן את http://localhost:5000.

## backend/config.py – קובץ הקונפיגורציה

**מה הקובץ:** כל ההגדרות של המערכת מרוכזות כאן: מדיניות הסיסמה, מסד הנתונים והמייל. זה קובץ הקונפיגורציה שהעבודה דורשת, ומנהל המערכת יכול לשנות בו ערכים בלי לגעת בשאר הקוד. בקובץ אין פונקציות, רק משתנים.

**Imports:**

- `import os` – משמש לבניית נתיבי קבצים (`os.path`) ולקריאת משתני סביבה (`os.environ`).

**`BASE_DIR`** – הנתיב של התיקייה `backend`. כל שאר הנתיבים נבנים ממנו, כך שהקבצים נמצאים גם כשמריצים מתיקייה אחרת.

**מדיניות סיסמה:**

| משתנה | ערך | משמעות |
| --- | --- | --- |
| `PASSWORD_MIN_LENGTH` | 10 | אורך מינימלי של סיסמה |
| `PASSWORD_REQUIRE_UPPER` | True | חובה אות גדולה |
| `PASSWORD_REQUIRE_LOWER` | True | חובה אות קטנה |
| `PASSWORD_REQUIRE_DIGIT` | True | חובה ספרה |
| `PASSWORD_REQUIRE_SPECIAL` | True | חובה תו מיוחד |
| `PASSWORD_HISTORY` | 3 | כמה סיסמאות אחרונות אסור למחזר |
| `DICTIONARY_FILE` | forbidden_passwords.txt | קובץ המילון |
| `MAX_LOGIN_ATTEMPTS` | 3 | ניסיונות התחברות לפני נעילה |
| `LOCKOUT_MINUTES` | 15 | לכמה זמן המשתמש ננעל |

**מסד נתונים:**

- `DB_BACKEND` – ברירת המחדל היא `"sqlite"`. אם מגדירים משתנה סביבה `DB_BACKEND=mysql`, המערכת עובדת עם MySQL.
- `SQLITE_PATH` – מיקום קובץ ה-SQLite (`backend/comunication.db`).
- `MYSQL` – מילון עם פרטי החיבור ל-MySQL (host, user, password, database), שנקראים ממשתני סביבה.

**מייל:**

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SENDER` – פרטי שרת המייל. כש-`SMTP_HOST` ריק, המייל נכתב לקובץ במקום להישלח.
- `OUTBOX_PATH` – הקובץ שאליו נכתב המייל במקרה הזה (`backend/outbox.log`).

**`SECRET_KEY`** – המפתח ש-Flask משתמש בו כדי לחתום את עוגיית ה-session, כך שמשתמש לא יוכל לזייף אותה. בסביבת אמת מגדירים אותו במשתנה סביבה ולא משאירים את ערך ברירת המחדל.

## backend/security.py – אבטחת סיסמאות

**מה הקובץ:** כל הפעולות הקריפטוגרפיות של המערכת: יצירת Salt, גיבוב סיסמה ב-HMAC, בדיקת מדיניות הסיסמה ויצירת קוד איפוס ב-SHA-1. הקובץ מממש את סעיפים 1ב, 1ג ו-5ג בעבודה.

**Imports:**

- `import hashlib` – פונקציות Hash: משתמשים ב-`sha256` בתוך ה-HMAC וב-`sha1` לקוד האיפוס.
- `import hmac` – מחשב HMAC: Hash שמשתמש גם במפתח סודי.
- `import os` – `os.urandom` מייצר בתים אקראיים ברמה קריפטוגרפית.
- `import string` – `string.punctuation` מכיל את כל התווים המיוחדים, כמו `!@#$`.
- `import config` – קובץ הקונפיגורציה של הפרויקט, שממנו נקראים כללי הסיסמה.

### `new_salt()`

מחזירה Salt אקראי חדש: 16 בתים מ-`os.urandom`, כמחרוזת Hex של 32 תווים. לכל משתמש נוצר Salt משלו, ולכן אותה סיסמה אצל שני משתמשים נותנת Hash שונה, וטבלאות Hash מוכנות מראש (Rainbow Tables) לא עוזרות לתוקף.

### `hash_password(password, salt)`

מחזירה את ה-HMAC-SHA256 של הסיסמה. ה-Salt משמש כמפתח, והסיסמה היא ההודעה:

```python
hmac.new(bytes.fromhex(salt), password.encode("utf-8"), hashlib.sha256).hexdigest()
```

- `bytes.fromhex(salt)` – ממיר את מחרוזת ה-Hex חזרה לבתים.
- `password.encode("utf-8")` – ממיר את הסיסמה לבתים.
- `hexdigest()` – מחזיר את התוצאה כמחרוזת של 64 תווים, וזה מה שנשמר במסד הנתונים.

### `check_password(password, salt, stored_hash)`

מחשבת שוב את ה-HMAC עם אותו Salt ומחזירה True אם התוצאה זהה ל-Hash השמור. ככה המערכת מאמתת סיסמה בלי לשמור אותה. משמשת ב-Login, בשינוי סיסמה ובבדיקת ההיסטוריה.

### `load_dictionary()`

קוראת את קובץ המילון (`config.DICTIONARY_FILE`) ומחזירה רשימה של הסיסמאות האסורות באותיות קטנות, בלי שורות ריקות. אם הקובץ לא קיים (`FileNotFoundError`) היא מחזירה רשימה ריקה במקום לקרוס.

### `check_policy(password)`

בודקת את הסיסמה מול כל ההגדרות ב-`config.py` ומחזירה רשימת שגיאות. רשימה ריקה אומרת שהסיסמה תקינה. הבדיקות:

1. אורך לפחות `PASSWORD_MIN_LENGTH`.
2. אות גדולה (`c.isupper()`), אות קטנה (`c.islower()`) וספרה (`c.isdigit()`), כל אחת רק אם היא מופעלת בקונפיגורציה.
3. תו מיוחד מתוך `string.punctuation`.
4. הסיסמה לא מופיעה במילון. ההשוואה מתעלמת מגודל אותיות.

הפונקציה משמשת בהרשמה, בשינוי סיסמה ובאיפוס סיסמה.

### `generate_reset_code()`

מייצרת קוד איפוס: 32 בתים אקראיים שעוברים SHA-1, כמו שסעיף 5ג דורש. התוצאה היא מחרוזת של 40 תווים.

```python
hashlib.sha1(os.urandom(32)).hexdigest()
```

## backend/db.py – מסד הנתונים

**מה הקובץ:** זה הקובץ היחיד שמדבר עם מסד הנתונים, וכל שאילתות ה-SQL נמצאות בו. כל השאילתות משתמשות בפרמטרים (`?`) ולא בשרשור מחרוזות. כך קלט של משתמש נשלח למסד הנתונים כערך בלבד ולא כחלק מהפקודה, וזו ההגנה מפני SQL Injection.

**Imports:**

- `import sqlite3` – הספרייה המובנית של Python לעבודה עם SQLite.
- `import config` – ממנו נקראים סוג מסד הנתונים ופרטי החיבור.
- `import pymysql` – נטען רק בתוך `get_connection()`, ורק כשעובדים עם MySQL. כך אפשר להריץ עם SQLite בלי להתקין את הספרייה.

**`USE_MYSQL`** – True כש-`config.DB_BACKEND` שווה ל-`"mysql"`.

### פונקציות תשתית

**`get_connection()`** – פותחת חיבור למסד הנתונים. ב-MySQL היא משתמשת ב-`DictCursor`, וב-SQLite ב-`sqlite3.Row`. בשני המקרים אפשר לקרוא עמודה לפי שם, למשל `user["email"]`.

**`execute(sql, params=(), fetch=None)`** – כל השאילתות עוברות דרכה. היא פותחת חיבור, מריצה את השאילתה עם הפרמטרים, שומרת (`commit`) וסוגרת את החיבור ב-`finally`, כך שהוא נסגר גם אם יש שגיאה. ב-MySQL היא מחליפה את `?` ב-`%s`, כי זה הפורמט ש-pymysql מצפה לו. הפרמטר `fetch` קובע מה מוחזר:

- `"one"` – שורה אחת כמילון, או None אם לא נמצאה.
- `"all"` – רשימה של כל השורות.
- בלי ערך – ה-id של השורה שנוספה (`lastrowid`).

**`init_db()`** – יוצרת את הטבלאות עם `CREATE TABLE IF NOT EXISTS`, כך שאפשר להריץ אותה בכל הפעלה. סוג המפתח הראשי משתנה לפי מסד הנתונים (`AUTO_INCREMENT` ב-MySQL, `AUTOINCREMENT` ב-SQLite).

| טבלה | עמודות | שימוש |
| --- | --- | --- |
| users | id, username, email, password_hash, salt, failed_attempts, locked_until | משתמשי המערכת |
| password_history | id, user_id, password_hash, salt | כל הסיסמאות שכל משתמש השתמש בהן |
| reset_codes | id, user_id, code, used | קודי איפוס סיסמה |
| customers | id, name, email, phone, address | לקוחות החברה |

### משתמשים

- **`create_user(username, email, password_hash, salt)`** – מוסיפה משתמש לטבלה `users`, ומוסיפה את הסיסמה הראשונה שלו להיסטוריה.
- **`get_user_by_username(username)`**, **`get_user_by_email(email)`**, **`get_user_by_id(user_id)`** – מחזירות משתמש אחד לפי שם, מייל או מזהה, או None אם הוא לא קיים.
- **`update_login_attempts(user_id, failed_attempts, locked_until)`** – מעדכנת את מונה הניסיונות הכושלים ואת זמן סיום הנעילה. הזמן נשמר כ-Unix time, כלומר מספר השניות מאז 1970.

### סיסמאות

- **`add_password_history(user_id, password_hash, salt)`** – שומרת סיסמה בטבלת ההיסטוריה.
- **`get_password_history(user_id, limit)`** – מחזירה את `limit` הסיסמאות האחרונות, מהחדשה לישנה (`ORDER BY id DESC`).
- **`update_password(user_id, password_hash, salt)`** – מחליפה את הסיסמה של המשתמש, מאפסת את הנעילה ומוסיפה את הסיסמה החדשה להיסטוריה.

### קודי איפוס

- **`save_reset_code(user_id, code)`** – שומרת קוד איפוס חדש.
- **`find_reset_code(user_id, code)`** – מחפשת קוד ששייך למשתמש ועוד לא נוצל (`used = 0`).
- **`mark_reset_code_used(code_id)`** – מסמנת קוד כמנוצל, כך שכל קוד עובד פעם אחת בלבד.

### לקוחות

- **`add_customer(name, email, phone, address)`** – מוסיפה לקוח לטבלה `customers`.
- **`get_customers()`** – מחזירה את כל הלקוחות, החדש ביותר ראשון.

## backend/mailer.py – שליחת מייל

**מה הקובץ:** שולח את קוד איפוס הסיסמה למייל של המשתמש (סעיף 5ב). כשלא מוגדר שרת SMTP, המייל נכתב לקובץ `outbox.log`, כדי שאפשר יהיה לבדוק את המערכת גם בלי שרת מייל.

**Imports:**

- `import smtplib` – הספרייה המובנית של Python לשליחת מייל בפרוטוקול SMTP.
- `from email.message import EmailMessage` – מחלקה שבונה הודעת מייל עם שולח, נמען, נושא ותוכן.
- `import config` – ממנו נקראים פרטי שרת המייל.

### `send_mail(to, subject, body)`

מקבלת נמען, נושא ותוכן, ועובדת באחת משתי דרכים:

- **בלי SMTP** (`config.SMTP_HOST` ריק) – כותבת את המייל לסוף הקובץ `outbox.log` (מצב `"a"`, הוספה) ומדפיסה הודעה לטרמינל.
- **עם SMTP** – בונה `EmailMessage`, מתחברת לשרת, מפעילה הצפנה עם `starttls()`, מתחברת עם שם המשתמש והסיסמה של שרת המייל ושולחת. הבלוק `with` סוגר את החיבור בסוף.

## backend/app.py – השרת והמסכים

**מה הקובץ:** זה הקובץ שמריצים (`python app.py`). הוא יוצר את אפליקציית Flask ומגדיר נתיב (route) לכל מסך. כל route הוא פונקציה שמקבלת את הבקשה מהדפדפן, משתמשת בשאר קבצי ה-backend ומחזירה דף HTML.

**Imports:**

- `import os` – לבניית הנתיב לתיקיית frontend.
- `import time` – `time.time()` מחזיר את הזמן הנוכחי, ומשמש לנעילת משתמש אחרי ניסיונות כושלים.
- `from flask import ...` – הכלים של Flask:
    - `Flask` – יצירת האפליקציה.
    - `render_template` – החזרת דף HTML מתיקיית ה-templates, עם משתנים.
    - `request` – גישה לנתונים שהמשתמש שלח בטופס (`request.form`) ולסוג הבקשה (`request.method`).
    - `session` – שמירת מידע בין בקשות, למשל מי מחובר. המידע נשמר בעוגייה חתומה.
    - `redirect`, `url_for` – העברה למסך אחר לפי שם הפונקציה שלו.
- `import config`, `import db`, `import mailer`, `import security` – שאר קבצי ה-backend.

### הגדרת האפליקציה

- `FRONTEND_DIR` – הנתיב לתיקיית `frontend`, שנמצאת ליד `backend`.
- `app = Flask(...)` – יצירת האפליקציה. `template_folder` ו-`static_folder` מפנים את Flask ל-`frontend/templates` ול-`frontend/static`, וזה מה שמחבר בין שתי התיקיות.
- `app.secret_key` – המפתח לחתימת עוגיית ה-session, מ-`config.SECRET_KEY`.
- `app.jinja_env.globals["settings"] = config` – מאפשר לדפי ה-HTML לקרוא ערכים מקובץ הקונפיגורציה, למשל את אורך הסיסמה המינימלי.

### פונקציות עזר

**`is_password_in_history(user_id, password)`** – שולפת את הסיסמאות האחרונות של המשתמש (לפי `PASSWORD_HISTORY`) ובודקת עם `check_password()` אם הסיסמה החדשה זהה לאחת מהן. מכיוון שלכל סיסמה ישנה יש Salt משלה, ה-HMAC מחושב מחדש עם ה-Salt של כל אחת.

**`validate_new_password(user_id, password, confirm)`** – מחזירה רשימת שגיאות של סיסמה חדשה: מדיניות (`check_policy`), היסטוריה (`is_password_in_history`) והתאמה לאימות. משמשת בשינוי סיסמה ובאיפוס סיסמה.

**`save_new_password(user_id, password)`** – יוצרת Salt חדש, מחשבת HMAC ושומרת עם `db.update_password()`.

### Routes

כל route מקבל שני סוגי בקשות. בקשת **GET** מציגה את המסך, ובקשת **POST** מגיעה כשהמשתמש שולח טופס.

**`index()` – `/`**
מעבירה משתמש מחובר למסך המערכת, ומשתמש שלא מחובר ל-Login.

**`register()` – `/register` (סעיף 1)**
קוראת מהטופס שם משתמש, מייל, סיסמה ואימות. היא בודקת ששם המשתמש והמייל לא תפוסים, שהמייל תקין, שהסיסמה עומדת במדיניות ושהאימות זהה. אם אין שגיאות, היא יוצרת Salt, מחשבת HMAC, שומרת את המשתמש ומציגה את מסך ה-Login. אם יש שגיאות, היא מחזירה את הטופס עם השגיאות, ושם המשתמש והמייל נשארים ממולאים.

**`login()` – `/login` (סעיף 3)**
שולפת את המשתמש לפי השם ובודקת לפי הסדר הזה:

1. המשתמש לא קיים – מוצגת הודעה שלא נמצא חשבון.
2. המשתמש נעול (`locked_until` גדול מהזמן הנוכחי) – מוצגת הודעת נעילה.
3. סיסמה נכונה – מונה הניסיונות מתאפס, `session["user_id"]` נשמר והמשתמש מועבר למסך המערכת.
4. סיסמה שגויה – מונה הניסיונות עולה ב-1. כשהוא מגיע ל-`MAX_LOGIN_ATTEMPTS`, המשתמש ננעל ל-`LOCKOUT_MINUTES` דקות. אחרת מוצג כמה ניסיונות נשארו.

**`logout()` – `/logout`**
מנקה את ה-session ומחזירה ל-Login.

**`system()` – `/system` (סעיף 4)**
משתמש שלא מחובר מועבר ל-Login. בשליחת טופס היא בודקת ששם הלקוח לא ריק, שומרת אותו עם `db.add_customer()` ומציגה הודעה עם שם הלקוח. בכל מקרה היא מעבירה לדף את רשימת הלקוחות מ-`db.get_customers()`.

**`change_password()` – `/change-password` (סעיף 2)**
זמינה רק למשתמש מחובר. היא בודקת את הסיסמה הקיימת עם `check_password()`, ואת החדשה עם `validate_new_password()`. אם הכל תקין, הסיסמה נשמרת עם `save_new_password()`.

**`forgot()` – `/forgot` (סעיף 5)**
מחפשת משתמש לפי המייל. אם הוא נמצא, היא מייצרת קוד עם `generate_reset_code()`, שומרת אותו, שולחת אותו עם `send_mail()`, שומרת את מזהה המשתמש ב-`session["reset_user_id"]` ומעבירה למסך הזנת הקוד.

**`forgot_verify()` – `/forgot/verify` (סעיף 5ד)**
בודקת עם `find_reset_code()` שהקוד שהוזן שייך למשתמש ועוד לא נוצל. אם הוא תקין, היא מסמנת אותו כמנוצל, שומרת `session["reset_verified"] = True` ומעבירה למסך הסיסמה החדשה.

**`reset_password()` – `/reset-password` (סעיף 5ד)**
נפתחת רק אם הקוד אומת, כלומר אם יש ב-session גם `reset_user_id` וגם `reset_verified`. היא מציגה את מסך שינוי הסיסמה בלי שדה הסיסמה הקיימת, בודקת עם `validate_new_password()` ושומרת. בסוף היא מנקה את ה-session ומחזירה ל-Login.

### הפעלה

```python
if __name__ == "__main__":
    db.init_db()
    app.run(port=5000)
```

כשמריצים את הקובץ ישירות, קודם נוצרות הטבלאות ואז השרת עולה על פורט 5000.

## שאר הקבצים ב-backend

**`forbidden_passwords.txt`** – מילון של 46 סיסמאות נפוצות, כמו `password`, `letmein` ו-`admin`, אחת בכל שורה. `load_dictionary()` קוראת אותו, ו-`check_policy()` דוחה סיסמה שמופיעה בו. מנהל המערכת יכול להוסיף מילים לקובץ בלי לשנות קוד.

**`requirements.txt`** – הספריות שצריך להתקין עם `pip install -r requirements.txt`:

- `Flask>=3.0` – הספרייה שמריצה את אתר הווב.
- `PyMySQL>=1.1` – חיבור ל-MySQL. נדרשת רק כשעובדים עם MySQL.

**`.gitignore`** (בשורש הפרויקט) – קבצים ש-git לא מעלה למאגר: קובץ מסד הנתונים (`*.db`), קובץ המיילים (`outbox.log`) וקבצי הקומפילציה של Python (`__pycache__`). כך משתמשים, Hash-ים וקודי איפוס שנוצרו בבדיקות לא מגיעים ל-GitHub.

## frontend/templates – דפי ה-HTML

**מה התיקייה:** כל המסכים שהמשתמש רואה. הדפים כתובים ב-HTML עם מנוע התבניות **Jinja2** של Flask, ו-`render_template` ב-`app.py` ממלא אותם בערכים. שלושה סוגי תחביר חוזרים בכל הדפים:

- `{{ ... }}` – מציג ערך, למשל `{{ user.username }}`. Jinja2 מקודד אוטומטית תווים מיוחדים כמו `<` ו-`>`, ולכן קוד HTML שמשתמש מזין מוצג כטקסט ולא מורץ.
- `{% if %}` / `{% for %}` – תנאים ולולאות, למשל הצגת שגיאה רק אם יש כזו.
- `{% extends "base.html" %}` – הדף יורש את המבנה מ-`base.html` וממלא רק את התוכן.

| קובץ | מסך | מה יש בו |
| --- | --- | --- |
| `base.html` | תבנית לכל הדפים | פס עליון עם השם Comunication_LTD. למשתמש מחובר מוצג גם תפריט: System, Change password, Logout. במרכז הדף יש בלוק `content` שכל דף ממלא |
| `register.html` | 1. Register | שדות שם משתמש, מייל, סיסמה ואימות, רשימת דרישות הסיסמה ורשימת שגיאות. אחרי שגיאה, שם המשתמש והמייל נשארים ממולאים |
| `change_password.html` | 2. שינוי סיסמה, וגם סיסמה חדשה בסעיף 5 | שדה סיסמה קיימת (מוצג רק כש-`reset` הוא False), סיסמה חדשה, אימות ורשימת דרישות |
| `login.html` | 3. Login | שם משתמש וסיסמה, הודעת שגיאה או הצלחה, וקישורים להרשמה ולשכחתי סיסמה |
| `system.html` | 4. מסך מערכת | טופס לקוח חדש (שם, מייל, טלפון, כתובת), הודעת אישור עם שם הלקוח, וטבלת כל הלקוחות שנבנית בלולאת `{% for c in customers %}` |
| `forgot.html` | 5. שכחתי סיסמה | שדה מייל וכפתור שליחת קוד |
| `forgot_verify.html` | 5. הזנת הקוד | שדה לקוד שהתקבל במייל, וקישור לשליחת קוד חדש |
| `password_rules.html` | חלק מסך, לא דף עצמאי | רשימת דרישות הסיסמה. נכלל ב-`register.html` וב-`change_password.html` עם `{% include %}` |

**איך `password_rules.html` עובד:** הערכים נקראים מ-`settings`, שהוא קובץ הקונפיגורציה. למשל, `{{ settings.PASSWORD_MIN_LENGTH }}` מציג 10, ודרישה מופיעה ברשימה רק אם היא מופעלת בקונפיגורציה. לכל שורה יש תכונה `data-rule`, שלפיה `password.js` יודע איזו בדיקה להריץ. המשתנה `history` קובע אם להציג גם את ההערה על הסיסמאות הקודמות. ההערה מוצגת במסך שינוי הסיסמה ולא בהרשמה.

## frontend/static – עיצוב וסקריפט

**מה התיקייה:** קבצים שהדפדפן טוען כמו שהם, בלי עיבוד בשרת. הדפים מפנים אליהם עם `url_for('static', filename='...')`.

### style.css

העיצוב של כל המסכים:

- `.header` – הפס העליון הכהה, ו-`.menu` – התפריט שבצד ימין.
- `.container` – המסגרת הלבנה ברוחב 600 פיקסלים במרכז הדף.
- `label`, `input`, `button` – שדות הטפסים והכפתורים.
- `.error` באדום ו-`.success` בירוק – הודעות למשתמש.
- `table`, `th`, `td` – טבלת הלקוחות.
- `.rules` – רשימת דרישות הסיסמה. הכלל `li:before` מוסיף ✗ אדום לפני כל דרישה, וכשלשורה יש המחלקה `ok`, הסימן מתחלף ל-✓ ירוק.

### password.js

**מה הקובץ:** מסמן כל דרישת סיסמה ב-✓ תוך כדי הקלדה, במסכי ההרשמה ושינוי הסיסמה. הסימון נועד רק לנוחות המשתמש, כי אפשר לעקוף קוד שרץ בדפדפן. הבדיקה שקובעת היא זו שבשרת, ב-`check_policy()`.

**משתנים:** `list` הוא רשימת הדרישות, ו-`password` ו-`confirmPassword` הם שני שדות הסיסמה. הסקריפט מוצא אותם לפי ה-id.

**`checkRules()`** – רצה בכל הקלדה באחד השדות. היא בודקת שש דרישות:

- `length` – אורך מינימלי, שנקרא מ-`data-min` ברשימה ומגיע מקובץ הקונפיגורציה.
- `upper`, `lower`, `digit` – ביטויים רגולריים `[A-Z]`, `[a-z]`, `[0-9]`.
- `special` – ביטוי רגולרי של כל התווים המיוחדים, אותם תווים שב-`string.punctuation` בשרת.
- `match` – הסיסמה והאימות זהים ולא ריקים.

אחר כך היא עוברת על שורות הרשימה, קוראת את `data-rule` של כל שורה, ומוסיפה את המחלקה `ok` לשורה שעמדה בדרישה או מסירה אותה משורה שלא עמדה.

**הפעלה:** בסוף הקובץ, אם כל הרכיבים קיימים בדף, נרשמים אירועי `input` על שני השדות, וכך `checkRules()` רצה בכל שינוי.
