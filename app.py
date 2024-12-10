from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from werkzeug.utils import secure_filename
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import mimetypes
import base64
import io
import json
import qrcode
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)
groq_api = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api)
conversations = {}

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = None

# Ai Agents - wikipedia, web search, qr code, email sender



def image_search(query):
    """Search for images using the given query and return top 5 images url"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        "searchType": "image",
        "num": 5,

    }
    response = requests.get(url, params=params)
    data = response.json()["items"]
    results = []
    for item in data:
        results.append(item["link"])
    return results

def email_sender(email: str, subject: str, message: str) -> str:
    """Send an email with the given subject and message"""
    
    return f"Email sent to {email} with subject '{subject}' and message '{message}'"

def search_wikipedia_for_extra_information(query: str) -> str:
    """"search wikipedia for the query and return the texts on the webpage"""
    texts = ""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}"
        response = requests.get(url)
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        if search_results:
            page_id = search_results[0].get("pageid")
            page_url = f"https://en.wikipedia.org/w/api.php?action=parse&format=json&pageid={page_id}"
            print("\n\n", query, "\n\n", page_url, "\n\n")
            page_response = requests.get(page_url)
            page_data = page_response.json()
            page_text = page_data.get("parse", {}).get("text", {}).get("*")
            soup = BeautifulSoup(page_text, "html.parser")
            paragraphs = soup.find_all("p")
            texts = "\n\n".join([p.get_text() for p in paragraphs])
        texts = texts[:1200]
        return texts
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"

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


def web_search(query: str) -> str:
    """Perform a web search and return top 3 links"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        
    }
    response = requests.get(url, params=params)
    data = response.json()
    output = ""
    for item in data["items"]:
        output += f"Title: {item['title']}\n"
        output += f"URL: {item['link']}\n\n"
        output += f"Description: {item['snippet']}\n\n"
    return output


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

def get_bot_response(user_query, conversation_id, web_access):
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {
                "role": "system",
                "content": """You are Luna a girl who knows everything and can search web for urls, images and also generate qr codes and search wilkipedia for detailed information."""
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
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Perform a web search and return top 3 links",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_wikipedia_for_extra_information",
                "description": "Search Wikipedia for extra information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "image_search",
                "description": "Search for images using the given query and return top 5 urls",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                },
            }
        }
    ]
    

    # Add user message to history
    context = get_relevant_context(user_query)
    if context:
        conversations[conversation_id].append({"role": "user", "content": f"{user_query}\n\nContext: {context}"})
    else:
        conversations[conversation_id].append({"role": "user", "content": f"{user_query}"})

    try:
        response = client.chat.completions.create(
            messages=conversations[conversation_id],
            model="llama3-groq-70b-8192-tool-use-preview",
            tools=tools,
            tool_choice="auto",
        )

        # Add bot response to history
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            qr_base64 = None
            image_results = None
            web_results = None
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
                
                elif tool_call.function.name == "web_search":
                    function_args = json.loads(tool_call.function.arguments)
                    web_results = web_search(function_args["query"])
                    
                    # Add tool response
                    conversations[conversation_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "web_search",
                        "content": web_results
                    })
                
                elif tool_call.function.name == "search_wikipedia_for_extra_information":
                    function_args = json.loads(tool_call.function.arguments)
                    wiki_results = search_wikipedia_for_extra_information(function_args["query"])
                    
                    # Add tool response
                    conversations[conversation_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "search_wikipedia_for_extra_information",
                        "content": wiki_results
                    })
                
                elif tool_call.function.name == "image_search":
                    function_args = json.loads(tool_call.function.arguments)
                    image_results = image_search(function_args["query"])
                    
                    # Add tool response
                    conversations[conversation_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "image_search",
                        "content": "\n".join(image_results)
                    })
            # Get final response
            second_response = client.chat.completions.create(
                messages=conversations[conversation_id],
                model="llama3-groq-70b-8192-tool-use-preview"
            )
            
            bot_message = second_response.choices[0].message.content
            if(qr_base64):
                bot_message += f"\n\n<img src='data:image/png;base64,{qr_base64}' alt='QR Code' class='rounded h-[300px] w-[300px] rouned-2xl mt-3 '/>"
            elif(image_results):
                bot_message += f"\n\n[image_search_tool_used]"
            elif(web_results):
                bot_message += f"\n\n[web_search_tool_used]"
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
        webAccess = request.form.get("provide-web-Access")
        if(webAccess == "true"):
            webAccess = True
        else:
            webAccess = False
        # Get bot response
        response = get_bot_response(message, conversation_id, webAccess)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear-history")
def clear_history():
    conversations.clear()
    return jsonify({"message": "History cleared"})

@app.route("/list-history")
def list_history():
    history = jsonify(conversations)
    print("\n\nHistory: ")
    for i in conversations:
        print("Key: ", i)
        print("Value: ")
        for j in conversations[i]:
            print(j)
    print("\n\n")
    history = [{"conversation_id": key, "messages": value} for key, value in conversations.items()]
    return jsonify(history)

@app.route("/history/<conversation_id>")
def get_history(conversation_id):
    return jsonify(conversations.get(conversation_id, []))

@app.route("/upload", methods=["POST"])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        success = initialize_knowledge_base(file)
        if success:
            return jsonify({"message": "Document processed successfully"})
        else:
            return jsonify({"error": "Failed to process document"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/check-context")
def isRAG():
    # check knowledge is initalised
    global vector_store
    if vector_store:
        return jsonify({
            "message": True
        })
    return jsonify({"message": False})

@app.route("/remove-context")
def removeRAG():
    global vector_store
    vector_store = None
    # empty uplaod folder
    for file in os.listdir("upload"):
        os.remove(os.path.join("upload", file))
    return jsonify({"message": "Context removed"})



if __name__ == "__main__":
    app.run(debug=True)
