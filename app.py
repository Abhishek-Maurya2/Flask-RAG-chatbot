from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from dotenv import load_dotenv
from flask_cors import CORS
from tools import (generate_qr_code,
                   web_search,
                   search_wikipedia_for_extra_information,
                   image_search,
                   read_website,
                   newsFinder,
                   parse_tool_calls)
import json
import re

load_dotenv()
app = Flask(__name__)
CORS(app)
groq_api = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api)
conversations = {}

SYSTEM_PROMPT = ""
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
                search the web for images based on the user's query
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for images"
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
                "description": "Read the content of the given website and summarize it to answer the query",
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
        },
        {
            "type": "function",
            "function": {
                "name": "newsFinder",
                "description" : "Search the internet for news and answer the question",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for news"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    

def get_bot_response(user_query, conversation_id):
    if conversation_id not in conversations:
        conversations[conversation_id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT or "You are Luna, an AI assistant built by Abhishek. You have realtime access to the internet and can help with a variety of tasks."
            }
        ]

    conversations[conversation_id].append({"role": "user", "content": user_query})

    try:
        # Initial response with tool calls
        response = client.chat.completions.create(
            messages=conversations[conversation_id],
            # model="llama3-groq-70b-8192-tool-use-preview",
            model = "llama-3.3-70b-versatile",
            tools=tools,
            tool_choice="auto",
        )

        # print(response)
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # parse tool calls if used as a response with regex to get the function name and arguments
        if "<function=" and "}</function>" in response_message.content:
            tools_used = parse_tool_calls(response_message.content)
        else:
            tools_used = None
        
        # Process tool calls if present
        if tool_calls or tools_used:
            if tools_used:
                tool_calls = tools_used
            tool_outputs = []
            
            print(f"{tool_calls}")
            
            # Execute each tool call and collect outputs
            for tool_call in tool_calls:
                function_name = tool_call['function']['name']
                function_args = tool_call['function']['arguments']
                        
                tool_handlers = {
                        "generate_qr_code": generate_qr_code,
                        "web_search": web_search,
                        "search_wikipedia_for_extra_information": search_wikipedia_for_extra_information,
                        "image_search": image_search,
                        "read_website": read_website,
                        "newsFinder": newsFinder
                    }
                    
                if function_name in tool_handlers:
                    print(f"Executing tool: {function_name} with args: {str(function_args)}")
                    try:
                        result = tool_handlers[function_name](**function_args) 
                        print(f"Result: {result}")
                    except Exception as e:
                        print(f"Error executing tool: {function_name} with args: {str(function_args)}")
                        print(e)
                    # Special handling for QR codes
                    if function_name == "generate_qr_code":
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"data:image/png;base64,{result}"
                        })
                    else:
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": result
                        })
                    
                        
            # Add all tool outputs to conversation
            print("TOOL OUTPUT:\n", tool_outputs)
            conversations[conversation_id].extend(tool_outputs)

            # Get final response incorporating tool outputs
            final_response = client.chat.completions.create(
                messages=conversations[conversation_id],
                model="llama-3.3-70b-versatile"
            )
            
            bot_message = final_response.choices[0].message.content + "\n<?THIS_MESSAGE_WAS_RESULT_OF_TOOL_USE_AND_NOT_TO_BE_COPIED?>"

            # Handle QR code display
            qr_outputs = [output for output in tool_outputs if output["name"] == "generate_qr_code"]
            if qr_outputs:
                qr_base64 = qr_outputs[0]["content"].split(",")[1]
                bot_message += f"\n\n<img src='data:image/png;base64,{qr_base64}' alt='QR Code' class='rounded h-[300px] w-[300px] rounded-2xl mt-3'/>"

        else:
            bot_message = response_message.content

        # Add final response to conversation history
        conversations[conversation_id].append({
            "role": "assistant",
            "content": bot_message
        })

        return bot_message

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        conversations[conversation_id].append({
            "role": "assistant",
            "content": error_msg
        })
        return error_msg

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        conversation_id = request.form.get("conversation_id", "default")
        message = request.form.get("message", "")
        # RAG = request.form.get("RAG-service")
        # Get bot response
        response = get_bot_response(message, conversation_id)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete", methods=["DELETE"])
def clear_history():
    try:
        conversations.clear()
        return jsonify({"message": "History cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    try:
        conversations.pop(conversation_id)
        return jsonify({"message": "Conversation deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history")
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

@app.route("/set-system-prompt", methods=["POST"])
def set_system_prompt():
    try:
        prompt = request.form.get("system_prompt")
        global SYSTEM_PROMPT
        SYSTEM_PROMPT = prompt
        # print(SYSTEM_PROMPT)
        return jsonify({"message": "System prompt updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-system-prompt")
def get_system_prompt():
    global SYSTEM_PROMPT
    print(SYSTEM_PROMPT)
    return jsonify({"system_prompt": SYSTEM_PROMPT})

if __name__ == "__main__":
    app.run()

# gunicorn -c gunicorn_config.py app:app