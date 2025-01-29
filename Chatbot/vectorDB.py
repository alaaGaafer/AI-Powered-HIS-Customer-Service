from dotenv import load_dotenv
import requests
import chromadb
import sqlite3
import os
import torch
from transformers import AutoTokenizer, AutoModel

# Initialize ChromaDB client
db_path = "Chroma_db"
os.makedirs(db_path, exist_ok=True)
client = chromadb.PersistentClient(path=db_path)
collections = client.list_collections()
if "hospital_knowledge" not in collections:
    collection = client.create_collection("hospital_knowledge")
else:
    collection = client.get_collection("hospital_knowledge")
    
# Load the DistilBERT tokenizer and model (dimension 384)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModel.from_pretrained("distilbert-base-uncased")

# Function to get embeddings using BERT
def get_embeddings(text):
    """Converts text to embeddings using BERT"""
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    
    with torch.no_grad():  
        outputs = model(**inputs)
    
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.detach().numpy().tolist()  


# Function to extract data from SQLite
def extract_data():
    conn = sqlite3.connect("SQLite database\\hospital_data.db")
    cursor = conn.cursor()

    cursor.execute(""" 
        SELECT Physicians.name, Physicians.Degree, Specialities.speciality_name, Specialities.Definition 
        FROM Physicians 
        JOIN Specialities ON Physicians.Speciality_id = Specialities.Speciality_id
    """)
    physicians_data = cursor.fetchall()

    cursor.execute("""
        SELECT Physicians.name, Schedules.monday, Schedules.tuesday, Schedules.wednesday, 
               Schedules.thursday, Schedules.friday, Schedules.saturday, Schedules.sunday 
        FROM Physicians 
        JOIN Schedules ON Physicians.doctor_id = Schedules.doctor_id
    """)
    schedules_data = cursor.fetchall()
    
    cursor.execute("SELECT service_name, price_usd FROM Pricelist")
    services_data = cursor.fetchall()
    
    cursor.execute("SELECT name, policy_description, address, landline, open_date FROM Policy")
    policy_data = cursor.fetchall()

    conn.close()

    return physicians_data, schedules_data, services_data, policy_data

# Store data in ChromaDB
def process_and_store():
    physicians_data, schedules_data, services_data, policy_data = extract_data()

    docs = []
    
    for doctor_name, degree, speciality, definition in physicians_data:
        text = f"Dr. {doctor_name}, holding a {degree}, specializes in {speciality}. {definition}"
        docs.append((text, {"doctor": doctor_name, "speciality": speciality}))

    for doctor_name, mon, tue, wed, thu, fri, sat, sun in schedules_data:
        text = f"Dr. {doctor_name} Times are: Monday: {mon}, Tuesday: {tue}, Wednesday: {wed}, Thursday: {thu}, Friday: {fri}, Saturday: {sat}, Sunday: {sun}."
        docs.append((text, {"doctor": doctor_name}))

    for service_name, price in services_data:
        text = f"The cost for {service_name} is {price} USD."
        docs.append((text, {"service": service_name}))

    for name, description, address, landline, open_date in policy_data:
        text = f"Hospital Policy: {name}. {description} Address: {address}. Contact: {landline}. Open since: {open_date}."
        docs.append((text, {"policy": name}))

    for i, (doc_text, metadata) in enumerate(docs):
        collection.add(documents=[doc_text], metadatas=[metadata], ids=[str(i)])

    print("Data successfully stored in ChromaDB.")

process_and_store()

