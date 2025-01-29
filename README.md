# AI-Powered-HIS-Customer-Service" 

## Overview
This project extracts data from an SQLite database and Excel sheets, processes the data, stores it in ChromaDB, and allows for querying using an AI model. The system utilizes various technologies, including ChromaDB, SentenceTransformers, and Google Gemini for query answering. The project is designed to handle hospital data, including information about physicians, schedules, services, and policies.

## Requirements
1- Before running the project, ensure that the required dependencies are installed. You can install them by running the following command:

```bash
pip install -r requirements.txt
2- Write your api key in the 10th line in vectorDB.py file
"genai.configure(api_key='Your_API_KEY')"



### Database_creation.py:
This code focuses on loading data from Excel sheets and inserting it into an SQLite database to establish tables that store information about hospital specialties, physicians, schedules, services, and policies.

1. **Excel File Loading**: Data from several sheets in an Excel file (`Xyris HIS_data.xlsx`) is loaded using `pandas`.
2. **SQLite Table Creation**: It sets up tables for `Specialities`, `Physicians`, `Schedules`, `Pricelist`, and `Policy` if they do not already exist.
3. **Inserting Data**: Data from the Excel sheets is iterated over, and relevant records are inserted into the corresponding tables in the SQLite database. Relationships like the connection between physicians and their specialties are handled with foreign keys.
4. **Committing Changes**: After inserting the data, the database connection is committed to ensure all changes are saved.



### ChromaDB.py:
This code processes data from an SQLite database and stores it in ChromaDB for further querying and AI-based answers.

1. **ChromaDB Client Setup**: The code initializes a connection to ChromaDB, a database designed for storing and querying document embeddings.
2. **Data Extraction**: It extracts data from an SQLite database (hospital_data.db) for various tables, including `Physicians`, `Schedules`, `Pricelist`, and `Policy`.
3. **Text Chunking**: Large documents are split into smaller chunks to manage size and improve storage efficiency.
4. **Embedding and Storing**: The extracted data is embedded using the `SentenceTransformer` model, and these embeddings (along with their corresponding metadata) are added to the ChromaDB collection for later querying.
5. **Query and Answer Generation**: Users can submit queries, which are embedded and compared against the ChromaDB collection. The top documents are retrieved, and Google Gemini AI is used to generate an answer based on the retrieved documents.
