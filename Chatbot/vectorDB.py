import sqlite3
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
import os  
import google.generativeai as genai

# Initialize ChromaDB client and embedding model
client = chromadb.Client()
collection = client.create_collection("hospital_data")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

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

# Split large text into smaller chunks
def split_into_chunks(text, chunk_size=500):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

# Store data in ChromaDB
def process_and_store():
    physicians_data, schedules_data, services_data, policy_data = extract_data()

    docs = []
    
    # Process physicians data
    for doctor_name, degree, speciality, definition in physicians_data:
        text = f"Dr. {doctor_name}, holding a {degree}, specializes in {speciality}. {definition}"
        docs.append((text, {"doctor": doctor_name, "speciality": speciality}))

    # Process schedules data
    for doctor_name, mon, tue, wed, thu, fri, sat, sun in schedules_data:
        text = f"Dr. {doctor_name} Times are: Monday: {mon}, Tuesday: {tue}, Wednesday: {wed}, Thursday: {thu}, Friday: {fri}, Saturday: {sat}, Sunday: {sun}."
        docs.append((text, {"doctor": doctor_name}))

    # Process services data
    for service_name, price in services_data:
        text = f"The cost for {service_name} is {price} USD."
        docs.append((text, {"service": service_name}))

    # Process policy data
    for name, description, address, landline, open_date in policy_data:
        text = f"Hospital Policy: {name}. {description} Address: {address}. Contact: {landline}. Open since: {open_date}."
        docs.append((text, {"policy": name}))

    # Split large documents into chunks and embed them
    for i, (doc_text, metadata) in enumerate(docs):
        chunks = split_into_chunks(doc_text)
        for chunk in chunks:
            embedding = embedding_model.encode(chunk).tolist()
            collection.add(documents=[chunk], metadatas=[metadata], embeddings=[embedding], ids=[f"{i}_{chunks.index(chunk)}"])

    print("Data successfully stored in ChromaDB.")

# Perform similarity search for a query
def perform_query(query):
    # Tokenize and embed the query
    query_embedding = embedding_model.encode(query).tolist()

    # Perform similarity search on ChromaDB
    results = collection.query(query_embeddings=[query_embedding], n_results=5)

    # Retrieve top results
    return results['documents']

def generate_answer_with_gemini(documents, query):
    # load_dotenv('API.env')  # Load environment variables
    # gemini_api_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key='AIzaSyB4V3q1GvCY8R_RJfHFCNQOf7GKfL2eoqI')

    
    # Flatten the list of documents into strings only
    document_texts = [doc[0] for doc in documents]  
    
    # Combine the retrieved documents into a prompt for Gemini
    context = "\n".join(document_texts)
    prompt = f"You are a customer service chatbot in a hospital. Your task is to help the user by answering their query from the provided context. If you don't know the answer, say you don't know and don't come up with an answer from your own. Answer the following question based on the context below:\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
    
    model = genai.GenerativeModel(model_name='gemini-pro')
    response = model.generate_content(prompt)  

    return response.text.strip()


# Example usage
process_and_store()

query = "What are the doctors names and availability?"
top_docs = perform_query(query)

for doc in top_docs:
    print(doc)

answer = generate_answer_with_gemini(top_docs, query)
print("Answer:", answer)
