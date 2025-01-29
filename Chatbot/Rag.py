from dotenv import load_dotenv
import requests
import chromadb
import sqlite3
import os
import torch
from transformers import AutoTokenizer, AutoModel
import google.generativeai as genai

import chromadb
import os

# Initialize ChromaDB client
db_path = "Chroma_db"
os.makedirs(db_path, exist_ok=True)

# Create a PersistentClient instance
client = chromadb.PersistentClient(path=db_path)

# Load the existing collection (replace 'hospital_knowledge' with your actual collection name)
collection = client.get_collection("hospital_knowledge")

# Load BERT tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModel.from_pretrained("distilbert-base-uncased")

def get_embeddings(text):
    """Converts text to embeddings using BERT"""
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    
    # Get the model output (hidden states)
    with torch.no_grad():  # We don't need gradients for inference
        outputs = model(**inputs)
    
    # Get the embeddings (we can take the mean of all token embeddings or just the [CLS] token)
    embeddings = outputs.last_hidden_state.mean(dim=1)  # Taking the mean of all token embeddings
    return embeddings.detach().numpy().tolist()  # Convert to a list for storage

# Function to retrieve documents from ChromaDB
def retrieve_documents(query):
    embeddings = get_embeddings(query)
    results = collection.query(query_embeddings=embeddings, n_results=3)
    return results['documents']

# Setup for Gemini API
def setup():
    load_dotenv('API.env')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
        
    if gemini_api_key is None:
        raise Exception("GEMINI_API_KEY is not set")
            
    genai.configure(api_key=gemini_api_key)

# Function to generate text using Gemini and retrieved data
def generate_text(query):
    # Retrieve context based on the query
    documents = retrieve_documents(query)
    context = " ".join(documents)  # Join the retrieved documents to create a context for the model
    
    prompt = f"""
    You are a customer service chatbot in a hospital. Your task is to help the user by answering their query from the retrieved data.
    User will mostly ask about which doctor to seek for their problem, what are the availability of the doctor, and what are the prices. If
    you don't know the answer, say you don't know and don't come up with an answer from your own.

    Now, given the query:

    Query: "{query}"

    Context: {context}

    Answer:
    """

    model = genai.GenerativeModel(model_name='gemini-pro')
    response = model.generate_content(prompt)
    command = response.text.strip().replace("```python", "").replace("```", "")
    return command

# Test the chatbot
query = "What are the hospital policies on patient care?"
response = generate_text(query)
print(response)
