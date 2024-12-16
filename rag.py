from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer, util
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize MongoDB client
uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(uri)
db = mongo_client["RAG"]
collection = db["RAG"]

try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment.\nYou successfully connected to MongoDB!🚀🚀\n")
except Exception as e:
    print(e)
    exit()

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def split_text(text, chunk_size=100):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def initialize_knowledge(doc):
    
    chunks = split_text(doc)
    embeddings = model.encode(chunks)
    
    collection.delete_many({})
    
    for chunk, embedding in zip(chunks, embeddings):
        collection.insert_one({"content": chunk, "embedding": embedding.tolist()})

def retrieve_documents(query):
    query_embedding = model.encode([query])[0]
    documents = list(collection.find())
    similarities = [(doc, util.cos_sim(query_embedding, doc["embedding"]).item()) for doc in documents]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [doc[0]["content"] for doc in similarities[:5]]

@app.route('/')
def home():
    return render_template('1.html')

@app.route('/initialize', methods=['POST'])
def initialize():
    file = request.files['file']
    if not file:
        return jsonify({"error": "File parameter is required"}), 400
    try:
        doc = file.read().decode("utf-8")
    except Exception as e:
        return jsonify({"error": "Invalid file format Only txt file is suppored"}), 400
    initialize_knowledge(doc)
    return jsonify({"message": "Knowledge base initialized"}), 200

@app.route('/retrieve', methods=['GET'])
def retrieve():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    documents = retrieve_documents(query)
    return jsonify({"context": documents}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
