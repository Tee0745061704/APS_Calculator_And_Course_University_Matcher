# South African Varsity & Bursary Matching Portal

A comprehensive Flask-based web application designed to help South African Matric students match their **National Senior Certificate (NSC)** academic results against university course entry criteria and available bursaries. It also features a cost calculator and a student wellness tracker.

---

## 🚀 Features

*   **Academic Dashboard:** Automatically calculates **APS (Admission Point Score)** excluding Life Orientation, overall academic averages, and specific Math/Science gateway trackers.
*   **Course Matching Engine:** Evaluates student profiles against a local database (`universities.csv`) of minimal APS requirements, subject thresholds, and averages.
*   **Bursary Engine:** Flags financial opportunities (`bursaries.csv`) matching a user's field of study and matric marks.
*   **Cost Calculator:** Tracks custom tuition, accommodation, and book estimates per course.
*   **Wellness Tracker:** Allows students to document how they are coping through check-ins during stressful matric cycles.
*   **Demo Bypass:** Entering the username `Themba` (with any password) bypasses database setup to provision a high-performing dummy metric suite for evaluation or presentation.

---

## 🛠️ Tech Stack

*   **Backend:** Python 3.x, Flask, Gunicorn (for production)
*   **Database:** SQLite3
*   **Security:** Werkzeug password hashing, Flask cookie-based session management
*   **Deployment:** Render Cloud Platform

---

## 📦 Project Directory Structure

```text
├── app.py                  # Main application router and execution logic
├── database.py             # SQLite helper functions (init_db, get_db_connection)
├── requirements.txt        # Python library dependencies for installation and hosting
├── render.yaml             # Render Blueprint configuration for seamless deployment
├── templates/              # HTML template UI files
│   ├── index.html          # Central workspace reporting dashboard
│   ├── bursaries.html      # Bursary search, matching, and exploration viewport
│   ├── login.html          # Secure authentication gate
│   ├── register.html       # Profile provisioning route
│   └── courses.html        # Course matching matrix and academic eligibility view
├── universities.csv        # Seed file containing university courses entry requirements
└── bursaries.csv           # Seed file containing available student funding structures
```

---

## ⚙️ Initial Data Structure Requirements

To keep the application processing routines error-free, ensure your data seed files match the structural headers below:

### 1. `universities.csv`
```csv
University,Course,Min_APS,Min_Avg,Req_Math,Req_Science
University of the Witwatersrand,BEng Mechanical Engineering,42,75,70,70
University of Johannesburg,BSc Computer Science,32,65,60,0
```

### 2. `bursaries.csv`
```csv
Name,Provider,Min_APS,Min_Avg,Req_Math,Amount,Field,Deadline,Covers
Thuthuka Bursary,SAICA,32,65,60,Full Cost,Accounting,2026-08-31,Tuition & Boarding
```

---

## 💻 Local Installation & Quickstart

Follow these steps to run the application on your local machine.

### 1. Clone the repository and navigate into it
```bash
cd varsity-bursary-portal
```

### 2. Set up a virtual environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install required packages
Install all dependencies listed inside the production manifest:
```bash
pip install -r requirements.txt
```

### 4. Initialize Database and Run
Start your local server execution block:
```bash
python app.py
```
The application will automatically invoke `init_db()` from `database.py` to seed your local SQLite database tables if they do not exist.

### 5. Access the app
Open your web browser and navigate to: **`http://127.0.0`**

---

## 🌐 Production Deployment (Render)

This repository includes a native **`render.yaml`** Blueprint specification. To deploy this application live:

1. Push your code repository to **GitHub** or **GitLab**.
2. Log into your **Render Dashboard** (`://render.com`).
3. Click **New** -> **Blueprint**.
4. Connect this repository. Render will automatically parse `render.yaml` to spin up your Flask web service with the correct Python environment, disk variables, and `gunicorn` configuration.

---

## 🔒 Security Notice
The current `app.secret_key` string inside development environments is set to a static development value. Before pushing this software to live environments via Render, make sure to add a custom environment variable named `SECRET_KEY` inside your environment dashboard settings to prevent session high-jacking.
