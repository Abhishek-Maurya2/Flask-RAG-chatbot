from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from werkzeug.utils import secure_filename
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import mimetypes


app = Flask(__name__)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")
client = Groq(api_key=api_key)
conversations = {}

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = None

def initialize_knowledge_base(file):
    global vector_store
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join("upload", filename)
        print (file_path)
        file.save(file_path)

        # Detect file type and use appropriate loader
        file_type = mimetypes.guess_type(filename)[0]
        
        if file_type == 'application/pdf':
            loader = PyPDFLoader(file_path)
        elif file_type == 'text/plain':
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
        documents = loader.load()

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        texts = text_splitter.split_documents(documents)

        if not texts:
            print(f"Warning: No text chunks created from {filename}")
            return False

        # Create or update vector store
        if vector_store is None:
            vector_store = FAISS.from_documents(texts, embeddings)
        else:
            vector_store.add_documents(texts)

        print(f"Added {len(texts)} chunks to vector store from {filename}")
        return True

    except Exception as e:
        print(f"Error initializing knowledge base: {str(e)}")
        return False

def get_relevant_context(query: str) -> str:
    try:
        if vector_store is None:
            return ""

        # Get relevant documents
        relevant_docs = vector_store.similarity_search(
            query,
            k=3  # Number of relevant chunks to retrieve
        )

        # Combine context from relevant documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        return context

    except Exception as e:
        print(f"Error getting context: {str(e)}")
        return ""

def get_bot_response(user_query, file, conversation_id):
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {
                "role": "system",
                "content": "imagine you are in a world where your name is luna and in this world everything is fair",
            }
        ]

    try:
        # Add user message to history
        if file:
            initialize_knowledge_base(file)
            context = get_relevant_context(user_query)
            conversations[conversation_id].append({"role": "user", "content": f"Context: {context}\n\nQuestion: {user_query}"})
        else:
            conversations[conversation_id].append({"role": "user", "content": user_query})

        # Get response
        response = client.chat.completions.create(
            messages=conversations[conversation_id],
            model="llama3-groq-70b-8192-tool-use-preview",
        )

        # Add bot response to history
        bot_message = response.choices[0].message.content
        conversations[conversation_id].append(
            {"role": "assistant", "content": bot_message}
        )

        return bot_message

    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        conversation_id = request.form.get("conversation_id", "default")
        message = request.form.get("message", "")
        file = request.files.get("file")

        # Get bot response
        response = get_bot_response(message, file, conversation_id)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear-history")
def clear_history():
    conversations.clear()
    return jsonify({"message": "History cleared"})

@app.route("/list-history")
def list_history():
    return jsonify(conversations)

@app.route("/history/<conversation_id>")
def get_history(conversation_id):
    return jsonify(conversations.get(conversation_id, []))


if __name__ == "__main__":
    app.run(debug=True)
