from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "rework.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
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
                    rework_out TEXT NOT NULL,
                    board_status TEXT NOT NULL,
                    remarks TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    data = conn.execute("SELECT * FROM rework_tracker ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/add', methods=['POST'])
def add():
    data = request.form
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO rework_tracker 
                 (customer, fg_assert, side, board_serial, rework_location, defect_type, line,
                  operator_id, shift, rework_in, rework_out, board_status, remarks)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (
                  data['customer'], data['fg_assert'], data['side'], data['board_serial'],
                  data['rework_location'], data['defect_type'], data['line'], data['operator_id'],
                  data['shift'], now, now, data['board_status'], data.get('remarks', '')
              ))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/get_fg_list', methods=['GET'])
def get_fg_list():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT DISTINCT fg_assert FROM rework_tracker ORDER BY fg_assert").fetchall()
    conn.close()
    return jsonify([r[0] for r in rows])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
