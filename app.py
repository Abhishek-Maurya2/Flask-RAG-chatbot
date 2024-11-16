from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from werkzeug.utils import secure_filename
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import mimetypes
import base64
import io
import json
import qrcode


app = Flask(__name__)
groq_api = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api)
conversations = {}

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = None

def generate_qr_code(data: str) -> str:
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


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

def get_bot_response(user_query, file, conversation_id, webAccess):
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {
                "role": "system",
                "content": "imagine you are in a world where your name is luna and in this world everything is fair",
            }
        ]

    tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_qr_code",
                    "description": "Generate a QR code from text data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "string",
                                "description": "The text to encode in QR code"
                            }
                        },
                        "required": ["data"]
                    }
                }
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
        

        # Get response from bot
        response = client.chat.completions.create(
            messages=conversations[conversation_id],
            model="llama3-groq-70b-8192-tool-use-preview",
            tools=tools,
            tool_choice="auto"
        )

        # Add bot response to history
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Handle tool calls
            conversations[conversation_id].append(
                {"role": "assistant", "content": response_message.content}
            )
            
            for tool_call in tool_calls:
                if tool_call.function.name == "generate_qr_code":
                    function_args = json.loads(tool_call.function.arguments)
                    qr_base64 = generate_qr_code(function_args["data"])
                    
                    # Add tool response
                    conversations[conversation_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "generate_qr_code",
                        "content": f"data:image/png;base64,{qr_base64}"
                    })

            # Get final response
            second_response = client.chat.completions.create(
                messages=conversations[conversation_id],
                model="llama3-groq-70b-8192-tool-use-preview"
            )
            bot_message = second_response.choices[0].message.content
        else:
            bot_message = response_message.content

        conversations[conversation_id].append({"role": "assistant", "content": bot_message})
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
        webAccess = request.form.get("webAccess")

        # Get bot response
        response = get_bot_response(message, file, conversation_id, webAccess)
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
