import sqlite3
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
import os  
import google.generativeai as genai
from collections import deque

genai.configure(api_key='Your_API_KEY')

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
        text = f"Dr. {doctor_name} availability Times are: Monday: {mon}, Tuesday: {tue}, Wednesday: {wed}, Thursday: {thu}, Friday: {fri}, Saturday: {sat}, Sunday: {sun}."
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

process_and_store()

# Rag starts here

# Initialize the memory buffer to Store the last 5 interactions
N = 5
memory_buffer = deque(maxlen=N) 

# Function to add interactions to memory buffer
def add_to_memory(query, answer):
    memory_buffer.append({"query": query, "answer": answer})

# Perform similarity search for a query
def perform_query(query):
    # Tokenize and embed the query
    query_embedding = embedding_model.encode(query).tolist()

    # Perform similarity search on ChromaDB
    results = collection.query(query_embeddings=[query_embedding], n_results=5)

    # Retrieve top results
    return results['documents']


def generate_answer_with_memory(documents, query):
    # Load the context from memory buffer (past conversations)
    context = ""
    for memory in memory_buffer:
        context += f"Q: {memory['query']}\nA: {memory['answer']}\n"

    # Flatten the list of documents into strings only
    document_texts = [doc[0] for doc in documents]  
    
    # Combine memory and documents context
    context += "\n".join(document_texts)
    
    # Prepare the prompt with context and the current query
    prompt = f"You are a customer service chatbot in a hospital. Your task is to help the user by answering their query from the provided context. Please answer with all the relevant details found in the context below:\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
    
    # Call the Gemini API for content generation
    model = genai.GenerativeModel(model_name='gemini-pro')
    response = model.generate_content(prompt)  

    # Save the query and answer in memory buffer
    add_to_memory(query, response.text.strip())

    return response.text.strip()


# Example usage
#  who are the doctors whose specilitiy is Cardiologist
#  what time is she available in?
#  but I asked about dr.alice's time
#  how much is her service is gonna cost
#  what is the hospital policy ?

for _ in range(N):  # Asking N times
    query = input("Please enter a query or end to exit: ")  # asks user for input
    if query == "end":
        break
    top_docs = perform_query(query)
    
    # Display the top documents found just for checking
    # for doc in top_docs:
    #     print(doc)
    
    answer = generate_answer_with_memory(top_docs, query)
    print("Answer:", answer)
