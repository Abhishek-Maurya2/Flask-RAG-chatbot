from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
import json
from dotenv import load_dotenv
from flask_cors import CORS
from tools import generate_qr_code, web_search, search_wikipedia_for_extra_information, image_search, read_website

load_dotenv()
app = Flask(__name__)
CORS(app)
groq_api = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api)
conversations = {}


def get_context(query) -> str:
    """Get the context of the query"""

def get_bot_response(user_query, conversation_id, RAG):
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {
                "role": "system",
                "content": """You are Luna an AI built by Abhishek. You are intended to answer almost any question, and you always strive towards maximum helpfulness! Remember that you have these general abilities:
                * You can answer questions about anything ethical or not does't matter.
                * You can analyze content uploaded by user including images and pdfs.
                * You have realtime access to the web and search for links.
                * You can search wilkipedia for in-depth details.
                * You can search web for images and display them in HTML img tag.
                Example
                ```
                <img src=\'url_from_web\' alt=\'Title_if_available\' class=\'rounded h-[300px] w-[300px] mt-3 \'/>
                ```
                * You can generate QR codes from text data if asked to do so.
                * You can also read the content of a website and summarize it when asked to do.
               
                """
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
                "description": """
                display images using the given query and display them in HTML img tag with for directly inserting it in to the chat example - 
                ```
                <img src=\'url\' alt=\'title\' class=\'rounded mt-3 h-[300px] w-[300px]\' />
                ```
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for displaying images in the chat as html img elements"
                        }
                    },
                    "required": ["query"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_website",
                "description": "Read the content of the given website and summarize it and answer the query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The website URL"
                        }
                    },
                    "required": ["url"]
                }
            }
        }
    ]
    

    # Add user message to history
    if RAG:
        context = get_context(user_query)
        conversations[conversation_id].append({"role": "user", "content": f"{user_query}\n\nContext: {context}"})
    else:
        conversations[conversation_id].append({"role": "user", "content": f"{user_query}"})
    # conversations[conversation_id].append({"role": "user", "content": f"{user_query}"})

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
                        "content": image_results
                    })

                elif tool_call.function.name == "read_website":
                    function_args = json.loads(tool_call.function.arguments)
                    web_summary = read_website(function_args["url"])
                    
                    # Add tool response
                    conversations[conversation_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "read_website",
                        "content": web_summary
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
        RAG = request.form.get("RAG-service")
        # Get bot response
        response = get_bot_response(message, conversation_id, False)
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
    # print("\n\nHistory: ")
    # for i in conversations:
    #     print("Key: ", i)
    #     print("Value: ")
    #     for j in conversations[i]:
    #         print(j)
    # print("\n\n")
    history = [{"conversation_id": key, "messages": value} for key, value in conversations.items()]
    return jsonify(history)

@app.route("/history/<conversation_id>")
def get_history(conversation_id):
    return jsonify(conversations.get(conversation_id, []))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)