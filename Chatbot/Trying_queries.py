import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('C:/Users/Alaa/Desktop/AI-Powered HIS Customer Service/SQLite database/hospital_data.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Query all rows from the Physicians table (change the table name as needed)
cursor.execute("SELECT * FROM Schedules")

# Fetch all results and print them
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection when done
conn.close()
