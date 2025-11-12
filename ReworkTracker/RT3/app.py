import os, sys, sqlite3, threading, webbrowser, ctypes, shutil
from datetime import datetime
from flask import Flask, render_template, request, redirect, jsonify, send_file
import pandas as pd

# ==============================================================
# 📂 Hidden AppData storage for database & backups
# ==============================================================

APPDATA = os.getenv("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
HIDDEN_DIR = os.path.join(APPDATA, ".Rework")

LOCAL_DB = os.path.join(HIDDEN_DIR, "rework.db")
BACKUP_DIR = os.path.join(HIDDEN_DIR, "backups")

os.makedirs(HIDDEN_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Hide folder on Windows
if os.name == "nt":
    try:
        ctypes.windll.kernel32.SetFileAttributesW(HIDDEN_DIR, 2)
    except Exception:
        pass


# ==============================================================
# 🗄 Weekly Auto Backup
# ==============================================================

def weekly_backup():
    """Create a .bak file once per week based on ISO week number."""
    if not os.path.exists(LOCAL_DB):
        return

    week_no = datetime.now().isocalendar().week
    backup_name = f"rework_Week_{week_no}.bak"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    # Always overwrite the current week's backup
    try:
        shutil.copy2(LOCAL_DB, backup_path)
        print(f"📦 Weekly backup created: {backup_name}")
    except Exception as e:
        print(f"⚠️ Backup failed: {e}")


# ==============================================================
# 🧩 Flask App & DB Initialization
# ==============================================================

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()

    # Main Table
    c.execute('''CREATE TABLE IF NOT EXISTS rework_tracker (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer TEXT NOT NULL,
                    fg_assert TEXT NOT NULL,
                    side TEXT NOT NULL,
                    board_serial TEXT NOT NULL,
                    rework_location TEXT NOT NULL,
                    defect_type TEXT NOT NULL,
                    line TEXT NOT NULL,
                    operator_id TEXT NOT NULL,
                    shift TEXT NOT NULL,
                    rework_in TEXT NOT NULL,
                    rework_out TEXT,
                    board_status TEXT NOT NULL,
                    remarks TEXT
                )''')

    # Lookup Tables
    c.execute('''CREATE TABLE IF NOT EXISTS customer_list (name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS fg_list (name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS defect_list (name TEXT UNIQUE)''')

    conn.commit()
    conn.close()


def insert_if_new(table, value):
    """Insert into lookup tables if not exists."""
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute(f"INSERT OR IGNORE INTO {table} (name) VALUES (?)", (value,))
    conn.commit()
    conn.close()


# ==============================================================
# 🌐 Flask Routes
# ==============================================================

@app.route('/')
def index():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    data = conn.execute("SELECT * FROM rework_tracker ORDER BY id DESC").fetchall()

    customer_list = [r[0] for r in conn.execute("SELECT name FROM customer_list ORDER BY name").fetchall()]
    fg_list = [r[0] for r in conn.execute("SELECT name FROM fg_list ORDER BY name").fetchall()]
    defect_list = [r[0] for r in conn.execute("SELECT name FROM defect_list ORDER BY name").fetchall()]

    conn.close()
    return render_template('index.html', data=data, customers=customer_list, fgs=fg_list, defects=defect_list)


@app.route('/add', methods=['POST'])
def add():
    data = request.form
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    customer = data['customer'].strip()
    fg = data['fg_assert'].strip()
    defect = data['defect_type'].strip()

    insert_if_new("customer_list", customer)
    insert_if_new("fg_list", fg)
    insert_if_new("defect_list", defect)

    rework_out = None
    if data['board_status'] == "Rework Completed":
        rework_out = now

    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute('''INSERT INTO rework_tracker 
                (customer, fg_assert, side, board_serial, rework_location, defect_type, 
                 line, operator_id, shift, rework_in, rework_out, board_status, remarks)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (customer, fg, data['side'], data['board_serial'], data['rework_location'],
               defect, data['line'], data['operator_id'], data['shift'],
               now, rework_out, data['board_status'], data.get('remarks', '')))
    conn.commit()
    conn.close()

    weekly_backup()
    return redirect('/')


@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    status = request.form['board_status']
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    if status == "Rework Completed":
        c.execute("UPDATE rework_tracker SET board_status=?, rework_out=? WHERE id=?", (status, now, id))
    else:
        c.execute("UPDATE rework_tracker SET board_status=?, rework_out=NULL WHERE id=?", (status, id))
    conn.commit()
    conn.close()

    weekly_backup()
    return redirect('/')


@app.route('/export_excel')
def export_excel():
    conn = sqlite3.connect(LOCAL_DB)
    df = pd.read_sql_query("SELECT * FROM rework_tracker", conn)
    conn.close()

    file_path = os.path.join(BACKUP_DIR, f"Rework_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)


# ==============================================================
# 🚀 Auto Open Browser
# ==============================================================

def open_browser():
    try:
        webbrowser.open("http://127.0.0.1:5007/")
    except Exception:
        pass


if __name__ == "__main__":
    init_db()
    weekly_backup()
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, port=5007)
