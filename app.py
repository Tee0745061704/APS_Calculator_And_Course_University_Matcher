import csv
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db_connection

app = Flask(__name__)
# Cryptographic key signing for secure client-side cookie storage
app.secret_key = "super_secret_south_africa_varsity_key_123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'universities.csv')
BURSARY_FILE_PATH = os.path.join(BASE_DIR, 'bursaries.csv')

init_db()

def load_courses_from_csv():
    courses_list = []
    if not os.path.exists(CSV_FILE_PATH):
        return courses_list
    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                courses_list.append({
                    "varsity": row['University'].strip(),
                    "name": row['Course'].strip(),
                    "min_aps": int(row['Min_APS']),
                    "min_avg": int(row['Min_Avg']),
                    "req_math": int(row['Req_Math']),
                    "req_sci": int(row['Req_Science'])
                })
            except (ValueError, KeyError):
                continue
    return courses_list

def load_bursaries_from_csv():
    bursary_list = []
    if not os.path.exists(BURSARY_FILE_PATH):
        return bursary_list
    with open(BURSARY_FILE_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                bursary_list.append({
                    "name": row['Name'].strip(),
                    "provider": row['Provider'].strip(),
                    "min_aps": int(row['Min_APS']),
                    "min_avg": int(row['Min_Avg']),
                    "req_math": int(row['Req_Math']),
                    "amount": row['Amount'].strip(),
                    "field": row['Field'].strip(),
                    "deadline": row['Deadline'].strip(),
                    "covers": row['Covers'].strip()
                })
            except (ValueError, KeyError):
                continue
    return bursary_list

def calculate_aps(mark):
    if mark >= 80: return 7
    if mark >= 70: return 6
    if mark >= 60: return 5
    if mark >= 50: return 4
    if mark >= 40: return 3
    if mark >= 30: return 2
    return 1

def get_user_academic_stats(user_id):
    # Dummy verification block: skips DB loops during open tours to feed high-tier mock metrics
    if user_id == 'demo_guest_account':
        return 7, 100.00, 43, 100, 100

    conn = get_db_connection()
    subjects = conn.execute("SELECT id, subject, mark, level FROM subjects WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    total_marks = sum(row['mark'] for row in subjects)
    count = len(subjects)
    avg_mark = total_marks / count if count > 0 else 0
    total_aps = sum(row['level'] for row in subjects if "life orientation" not in row['subject'].lower())

    math_mark = 0
    sci_mark = 0
    for row in subjects:
        subj_name = row['subject'].lower()
        if "mathematics" in subj_name and "literacy" not in subj_name:
            math_mark = max(math_mark, row['mark'])
        if "physical science" in subj_name or "life science" in subj_name:
            sci_mark = max(sci_mark, row['mark'])
            
    return count, avg_mark, total_aps, math_mark, sci_mark

# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            return "Please fill in all fields", 400
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            session['user_id'] = user['id']
            session['username'] = username
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists! Go back and choose another.", 400
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        # PUBLIC PREVIEW MECHANISM: Catches 'Themba' with any password string immediately
        if username.lower() == 'themba':
            session['user_id'] = 'demo_guest_account'
            session['username'] = 'Themba (Demo Profile)'
            return redirect(url_for('index'))

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('index'))
        return "Invalid credentials! Go back and try again.", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- APP INTERFACE ENDPOINTS ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Inject static demo profiles on active guest sessions
    if session['user_id'] == 'demo_guest_account':
        subjects = [
            {"id": 1, "subject": "Mathematics", "mark": 100, "level": 7},
            {"id": 2, "subject": "Physical Sciences", "mark": 100, "level": 7},
            {"id": 3, "subject": "English Home Language", "mark": 100, "level": 7},
            {"id": 4, "subject": "IsiZulu First Additional Language", "mark": 100, "level": 7},
            {"id": 5, "subject": "Life Orientation", "mark": 100, "level": 0},
            {"id": 6, "subject": "Life Sciences", "mark": 100, "level": 7},
            {"id": 7, "subject": "Geography", "mark": 100, "level": 7}
        ]
        costs = [
            {"course_name": "University of the Witwatersrand - BEng Mechanical Engineering (Demo Matrix Route)", "tuition": 71500, "accommodation": 58000, "books": 11200}
        ]
        wellness_checks = [
            {"check_date": datetime.now().strftime("%Y-%m-%d %H:%M"), "feeling": "Public system tour session active. Real-time criteria matching matrices are responsive."}
        ]
    else:
        conn = get_db_connection()
        subjects = conn.execute("SELECT id, subject, mark, level FROM subjects WHERE user_id = ?", (session['user_id'],)).fetchall()
        costs = conn.execute("SELECT id, course_name, tuition, books, accommodation FROM costs WHERE user_id = ?", (session['user_id'],)).fetchall()
        wellness_checks = conn.execute("SELECT id, check_date, feeling FROM wellness_checks WHERE user_id = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
        conn.close()

    count, avg_mark, total_aps, math_mark, sci_mark = get_user_academic_stats(session['user_id'])

    result_text = (
        f"📊 Profile Stats ({session['username']}):\n"
        f"• Total Registered NSC Subjects: {count} / 7 Recommended\n"
        f"• Group Academic Average: {avg_mark:.2f}%\n"
        f"• Active Entry APS Score (Excl. LO): {total_aps} Points\n"
        f"• Pure Mathematics Tracker: {math_mark}% | Science Gateway Tracker: {sci_mark}%"
    )

    return render_template(
        'index.html', 
        subjects=subjects, 
        result=result_text, 
        costs=costs, 
        wellness_checks=wellness_checks
    )

@app.route('/courses')
def view_courses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    count, avg_mark, total_aps, math_mark, sci_mark = get_user_academic_stats(session['user_id'])
    qualified_courses = []

    if count > 0:
        csv_courses = load_courses_from_csv()
        for course in csv_courses:
            if (total_aps >= course["min_aps"] and 
                avg_mark >= course["min_avg"] and 
                math_mark >= course["req_math"] and 
                sci_mark >= course["req_sci"]):
                qualified_courses.append(course)

    return render_template('courses.html', courses=qualified_courses)

@app.route('/bursaries')
def view_bursaries():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    count, avg_mark, total_aps, math_mark, _ = get_user_academic_stats(session['user_id'])
    qualified_bursaries = []

    if count > 0:
        csv_bursaries = load_bursaries_from_csv()
        for bursary in csv_bursaries:
            if (total_aps >= bursary["min_aps"] and 
                avg_mark >= bursary["min_avg"] and 
                math_mark >= bursary["req_math"]):
                qualified_bursaries.append(bursary)

    return render_template('bursaries.html', bursaries=qualified_bursaries)

# --- PROTECTED ACTION FORMS (DEMO EXCLUSION BLOCKS ACTIVE) ---

@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_id'] == 'demo_guest_account':
        return "Database manipulation locked during public preview sessions. Register an account to record custom ledgers.", 403
        
    subject = request.form['subject']
    mark = int(request.form['mark'])
    level = 0 if "life orientation" in subject.lower() else calculate_aps(mark)

    conn = get_db_connection()
    conn.execute("INSERT INTO subjects (user_id, subject, mark, level) VALUES (?, ?, ?, ?)", 
                 (session['user_id'], subject, mark, level))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_id'] == 'demo_guest_account':
        return "Action locked during public previews.", 403
        
    conn = get_db_connection()
    conn.execute("DELETE FROM subjects WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_cost', methods=['POST'])
def add_cost():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_id'] == 'demo_guest_account':
        return "Action locked during public previews.", 403
        
    course_name = request.form['course_name']
    tuition = int(request.form['tuition'])
    books = int(request.form['books'])
    accommodation = int(request.form['accommodation'])
    
    conn = get_db_connection()
    conn.execute("INSERT INTO costs (user_id, course_name, tuition, books, accommodation) VALUES (?, ?, ?, ?, ?)",
                 (session['user_id'], course_name, tuition, books, accommodation))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_wellness', methods=['POST'])
def add_wellness():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_id'] == 'demo_guest_account':
        return "Action locked during public previews.", 403
        
    feeling = request.form['feeling']
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = get_db_connection()
    conn.execute("INSERT INTO wellness_checks (user_id, feeling, check_date) VALUES (?, ?, ?)",
                 (session['user_id'], feeling, current_date))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
