import flask
from flask import request, jsonify
import sqlite3
import chromadb
from transformers import BertTokenizer, BertModel
import torch


# Initialize Flask app
app = flask.Flask(__name__)

# Connect to SQLite database
def connect_db():
    return sqlite3.connect("SQLite/hospital_data.db")

# Route to insert a new physician
@app.route('/insert_physician', methods=['POST'])
def insert_physician():
    data = request.get_json()
    name = data['name']
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Insert physician into SQLite
    cursor.execute("INSERT INTO Physicians (name) VALUES (?)", (name,))
    conn.commit()
    
    # Vectorize the physician name and insert into ChromaDB
    vector = get_embeddings(name)
    collection.add(documents=[name], metadatas=[{"name": name}], embeddings=vector)
    
    conn.close()
    return jsonify({"message": "Physician added successfully!"}), 200

# Route to insert a new schedule
@app.route('/insert_schedule', methods=['POST'])
def insert_schedule():
    data = request.get_json()
    doctor_name = data['doctor_name']
    schedule = data['schedule']  # Assuming it's a dictionary with the days of the week
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Insert schedule into SQLite (assuming the doctor already exists)
    cursor.execute("""
        INSERT INTO Schedules (doctor_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday)
        VALUES (
            (SELECT id FROM Physicians WHERE name = ?),
            ?, ?, ?, ?, ?, ?, ?
        )
    """, (doctor_name, schedule['monday'], schedule['tuesday'], schedule['wednesday'], schedule['thursday'], schedule['friday'], schedule['saturday'], schedule['sunday']))
    
    conn.commit()
    
    # Vectorize the schedule data and insert into ChromaDB
    schedule_text = f"Schedule for {doctor_name}: {schedule}"
    vector = get_embeddings(schedule_text)
    collection.add(documents=[schedule_text], metadatas=[{"doctor_name": doctor_name}], embeddings=vector)
    
    conn.close()
    return jsonify({"message": "Schedule added successfully!"}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
