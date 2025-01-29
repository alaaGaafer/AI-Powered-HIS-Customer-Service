import pandas as pd
import sqlite3

# Load Excel file
file_path = "excel_sheets/Xyris HIS_data.xlsx"
xls = pd.ExcelFile(file_path)

# Connect to SQLite
conn = sqlite3.connect("SQLite database/hospital_data.db")
cursor = conn.cursor()

# Create Tables 
cursor.execute("""
CREATE TABLE IF NOT EXISTS Specialities (
    Speciality_id INTEGER PRIMARY KEY AUTOINCREMENT,
    speciality_name TEXT UNIQUE NOT NULL,
    definition TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Physicians (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT UNIQUE NOT NULL,
    Speciality_id INTEGER NOT NULL,
    Degree TEXT NOT NULL,
    FOREIGN KEY (Speciality_id) REFERENCES Specialities(Speciality_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Schedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    monday TEXT,
    tuesday TEXT,
    wednesday TEXT,
    thursday TEXT,
    friday TEXT,
    saturday TEXT,
    sunday TEXT,
    FOREIGN KEY (doctor_id) REFERENCES Physicians(doctor_id)
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

# Insert Specialities
for _, row in specialities_df.iterrows():
    speciality_name = row["Speciality Name"]
    definition = row["Definition"]
    
    cursor.execute("INSERT OR IGNORE INTO Specialities (speciality_name, definition) VALUES (?, ?)", 
                   (speciality_name, definition))

# Insert Physicians with Speciality References
for _, row in physicians_df.iterrows():
    doctor_name = row["Name"]
    speciality_name = row["Speciality"]
    degree = row["Degree"]

    # Get Speciality_id
    cursor.execute("SELECT Speciality_id FROM Specialities WHERE speciality_name = ?", (speciality_name,))
    result = cursor.fetchone()
    if result:
        speciality_id = result[0]
    else:
        cursor.execute("INSERT INTO Specialities (speciality_name) VALUES (?)", (speciality_name,))
        speciality_id = cursor.lastrowid

    # Insert Physician
    cursor.execute("INSERT OR IGNORE INTO Physicians (Name, Speciality_id, Degree) VALUES (?, ?, ?)", 
                   (doctor_name, speciality_id, degree))

# Insert Schedules for Doctors
for _, row in schedules_df.iterrows():
    doctor_name = row["Doctor Name"]

    # Get doctor_id
    cursor.execute("SELECT doctor_id FROM Physicians WHERE Name = ?", (doctor_name,))
    result = cursor.fetchone()
    
    if result:
        doctor_id = result[0]
    else:
        continue  # Skip if doctor is not found in Physicians table

    # Insert schedule
    cursor.execute("""
        INSERT INTO Schedules (doctor_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (doctor_id, row["Monday"], row["Tuesday"], row["Wednesday"], row["Thursday"], row["Friday"], row["Saturday"], row["Sunday"]))

# Insert Pricelist
for _, row in pricelist_df.iterrows():
    service_name = row["Service Name"]
    price_usd = row["Price (USD)"]
    
    cursor.execute("INSERT OR IGNORE INTO Pricelist (service_name, price_usd) VALUES (?, ?)", (service_name, price_usd))

# Insert Policy
for _, row in policy_df.iterrows():
    name = row["Name"]
    policy_description = row["Policy Description"]
    address = row["Address"]
    landline = row["Landline"]
    
    open_date = row["Open Date"]
    if isinstance(open_date, pd.Timestamp):
        open_date = open_date.strftime('%Y-%m-%d')  # Convert to YYYY-MM-DD format

    cursor.execute("INSERT OR IGNORE INTO Policy (name, policy_description, address, landline, open_date) VALUES (?, ?, ?, ?, ?)", 
                   (name, policy_description, address, landline, open_date))

# Commit and close connection
conn.commit()
conn.close()
