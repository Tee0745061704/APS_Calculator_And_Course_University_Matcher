from flask import Flask, render_template, request, redirect, url_for
from database import init_db, get_db_connection
from models import UNIVERSITIES_COURSES

app = Flask(__name__)

def calculate_aps(mark):
    if mark >= 80: return 7
    if mark >= 70: return 6
    if mark >= 60: return 5
    if mark >= 50: return 4
    if mark >= 40: return 3
    if mark >= 30: return 2
    return 1

@app.route('/')
def index():
    conn = get_db_connection()
    subjects = conn.execute("SELECT id, subject, mark, level FROM subjects").fetchall()
    conn.close()

    total_marks = sum(row['mark'] for row in subjects)
    count = len(subjects)
    avg_mark = total_marks / count if count > 0 else 0
    
    # Strictly exclude Life Orientation from the active entry APS calculation
    total_aps = sum(
        row['level'] for row in subjects 
        if "life orientation" not in row['subject'].lower()
    )

    # Academic path tracking checks
    math_mark = 0
    sci_mark = 0
    for row in subjects:
        subj_name = row['subject'].lower()
        if "mathematics" in subj_name and "literacy" not in subj_name:
            math_mark = max(math_mark, row['mark'])
        if "physical science" in subj_name or "life science" in subj_name:
            sci_mark = max(sci_mark, row['mark'])

    result_text = (
        f"📊 Operational Profile Stats:\n"
        f"• Total Registered NSC Subjects: {count} / 7 Recommended\n"
        f"• Group Academic Average: {avg_mark:.2f}%\n"
        f"• Active Entry APS Score (Excl. LO): {total_aps} Points\n"
        f"• Pure Mathematics Tracker: {math_mark}% | Science Gateway Tracker: {sci_mark}%"
    )

    qualified_courses = []
    if count > 0:
        for course in UNIVERSITIES_COURSES:
            if (total_aps >= course["min_aps"] and 
                avg_mark >= course["min_avg"] and 
                math_mark >= course["req_math"] and 
                sci_mark >= course["req_sci"]):
                qualified_courses.append(course)

    return render_template('index.html', subjects=subjects, result=result_text, courses=qualified_courses)

@app.route('/add', methods=['POST'])
def add():
    subject = request.form['subject']
    mark = int(request.form['mark'])
    
    # Life Orientation explicitly set to 0 level in database
    level = 0 if "life orientation" in subject.lower() else calculate_aps(mark)

    conn = get_db_connection()
    conn.execute("INSERT INTO subjects (subject, mark, level) VALUES (?, ?, ?)", (subject, mark, level))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM subjects WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
