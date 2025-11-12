# 🧰 Rework Tracker

A lightweight Flask-based desktop web app to record, monitor, and export **PCB rework activities**.  
Built for manufacturing process tracking — with automatic backups, Excel export, and persistent local storage in a hidden AppData folder.
It runs locally, stores data securely in a hidden folder, and can be packaged as a standalone `.exe` for easy deployment.

---

## 🚀 Features

- 📋 Add and manage rework records  
- 🧾 Track board serials, defect types, and operator details  
- 🔄 Auto timestamp for rework in/out  
- ⛔ Once a record is marked **Rework Completed**, it cannot be reverted to **Rework Pending**  
- 💾 Weekly automatic database backups (`.bak` files)  
- 📦 Export full rework data to Excel format (`.xlsx`) 
- 🔒 Stores all data securely in hidden AppData folder  
- 🌐 Auto-launches in browser when started
- 🧠 Smart dropdowns for Customer, FG Assert, and Defect lists that update dynamically  

---

## 🏗️ Project Structure

ReworkTracker/
│
├── app.py # Main Flask backend
├── templates/
│ └── index.html # Frontend UI
├── Solderingiron.ico # App icon
└── README.md # Documentation


---

## ⚙️ Installation & Setup

### 1. Install Python
Ensure **Python 3.10+** is installed and added to your system PATH.  
To verify, run:
python --version

### 2. Install Dependencies

pip install flask pandas openpyxl

python app.py

http://127.0.0.1:5009/

## 🧱 Building Executable

pyinstaller --onefile --noconsole --icon=Solderingiron.ico --name "ReworkTracker" --hidden-import=sqlite3 app.py

## 📦 App Data Location

C:\Users\<USERNAME>\AppData\Roaming\.Rework\

### Contents:

- rework.db — Main database
- backups\ — Weekly .bak backups
- Rework_Export_YYYYMMDD_HHMMSS.xlsx — Excel exports

## 🛡️ Backup System

rework_Week_<week_number>.bak

## 📋 Data Flow & Rules

- User fills in rework details on the form.
- Data is stored in rework.db.
- The app logs timestamps automatically:
  - Rework In → Time when record is added
  - Rework Out → Time when status changes to “Rework Completed”
- Status “Rework Completed” cannot be changed back to “Rework Pending”.
- Weekly backups ensure data safety.
- Users can export all records to Excel anytime. “⬇️ Download Excel”
- Records are timestamped automatically on entry.
- Once a record is updated to Rework Completed, it cannot be reverted.
- All lists (Customer, FG Assert, Defect) are auto-expanded when new entries are added.

## 🧰 How to Maintain / Update
🔄 Reset the Database

- If you want to start fresh (delete all records):
- Navigate to the hidden AppData folder:
- C:\Users\<USERNAME>\AppData\Roaming\.Rework\
- Delete rework.db.
- Restart the app — it will auto-create a new blank database.

## 🧑‍💻 Developer Info

Developed by: Bala Ganesh (Process) RT6
App Name: Rework Tracker
Version: 1.0
Framework: Flask
Database: SQLite (local)
Language: Python 3.10+

## 🛡️ Security Notes

The app runs entirely offline — no data is uploaded anywhere.
Database and backups are local to each user.
The hidden .Rework folder is protected but still accessible to advanced users if needed.

## 🧾 License

This project is for internal or educational use only.
No warranty or liability is provided for any data loss or misuse.

# 💙 Thank You for Using Rework Tracker!
