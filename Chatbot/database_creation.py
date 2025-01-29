import pandas as pd
import sqlite3

# Load Excel file
file_path = "excel_sheets/Xyris HIS_data.xlsx"
xls = pd.ExcelFile(file_path)

# Connect to SQLite
conn = sqlite3.connect("SQLite database/hospital_data.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Physicians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Schedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER,
    monday TEXT,
    tuesday TEXT,
    wednesday TEXT,
    thursday TEXT,
    friday TEXT,
    saturday TEXT,
    sunday TEXT,
    FOREIGN KEY (doctor_id) REFERENCES Physicians(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Specialities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    speciality_name TEXT UNIQUE NOT NULL,
    definition TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Pricelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT UNIQUE NOT NULL,
    price_usd TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Policy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    policy_description TEXT,
    address TEXT,
    landline TEXT,
    open_date TEXT
)
""")

# Read data from sheets
physicians_df = pd.read_excel(xls, sheet_name="Physicians")
schedules_df = pd.read_excel(xls, sheet_name="Schedules")
specialities_df = pd.read_excel(xls, sheet_name="Specialities")
pricelist_df = pd.read_excel(xls, sheet_name="Pricelist")
policy_df = pd.read_excel(xls, sheet_name="Policy")

# Insert Physicians (doctors)
for _, row in physicians_df.iterrows():
    doctor_name = row["Name"]
    
    # Insert doctor if not exists
    cursor.execute("INSERT OR IGNORE INTO Physicians (name) VALUES (?)", (doctor_name,))

# Insert Specialities
for _, row in specialities_df.iterrows():
    speciality_name = row["Speciality Name"]
    definition = row["Definition"]
    
    # Insert speciality if not exists
    cursor.execute("INSERT OR IGNORE INTO Specialities (speciality_name, definition) VALUES (?, ?)", (speciality_name, definition))

# Insert Pricelist
for _, row in pricelist_df.iterrows():
    service_name = row["Service Name"]
    price_usd = row["Price (USD)"]
    
    # Insert service price if not exists
    cursor.execute("INSERT OR IGNORE INTO Pricelist (service_name, price_usd) VALUES (?, ?)", (service_name, price_usd))

# Insert Policy
for _, row in policy_df.iterrows():
    name = row["Name"]
    policy_description = row["Policy Description"]
    address = row["Address"]
    landline = row["Landline"]
    
    # Convert open_date to string (if it is a Timestamp)
    open_date = row["Open Date"]
    if isinstance(open_date, pd.Timestamp):
        open_date = open_date.strftime('%Y-%m-%d')  # Convert to YYYY-MM-DD format
    
    # Insert policy if not exists
    cursor.execute("INSERT OR IGNORE INTO Policy (name, policy_description, address, landline, open_date) VALUES (?, ?, ?, ?, ?)", 
                   (name, policy_description, address, landline, open_date))


# Insert Schedules for Doctors
for _, row in schedules_df.iterrows():
    doctor_name = row["Doctor Name"]
    
    # Insert doctor if not exists
    cursor.execute("INSERT OR IGNORE INTO Physicians (name) VALUES (?)", (doctor_name,))
    
    # Get doctor_id
    cursor.execute("SELECT id FROM Physicians WHERE name = ?", (doctor_name,))
    doctor_id = cursor.fetchone()[0]
    
    # Insert schedule
    cursor.execute("""
        INSERT INTO schedules (doctor_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (doctor_id, row["Monday"], row["Tuesday"], row["Wednesday"], row["Thursday"], row["Friday"], row["Saturday"], row["Sunday"]))

# Commit and close connection
conn.commit()
conn.close()
