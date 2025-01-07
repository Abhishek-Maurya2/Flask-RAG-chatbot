from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from dotenv import load_dotenv
from flask_cors import CORS
from tools import (th, my_local_tools)

load_dotenv()
app = Flask(__name__)
CORS(app)
groq_api = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api)
conversations = {}

SYSTEM_PROMPT = ""


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
            model = "llama-3.1-8b-instant",
            tools=my_local_tools,
            tool_choice="auto",
        )
        
        tool_calls = response.choices[0].message.tool_calls
        qr_tool = None
        
        if tool_calls:
            try:
                tool_run = th.run_tools(response)
                if tool_run[1]['name'] == "generate_qr_code":
                    qr_tool = tool_run[1]['content']
                
                conversations[conversation_id].extend(tool_run)
                
                response = client.chat.completions.create(
                    messages=conversations[conversation_id],
                    model = "llama-3.3-70b-versatile",
                    )
                
            except Exception as e:
                return "Failed to call tool: " + str(e)
            
        
        res = response.choices[0].message.content
        if qr_tool:
            res += f"\n\n<img src='data:image/png;base64,{qr_tool}' alt='QR Code' class='rounded h-[300px] w-[300px] rouned-2xl mt-3 '/>"
            
        res = res + "\n<?THIS_MESSAGE_WAS_RESULT_OF_TOOL_USE_AND_NOT_TO_BE_COPIED?>" if tool_calls else res
        
        conversations[conversation_id].append({"role": "assistant", "content": res})
        return res
    
    except Exception as e:
        print("Error: ", e)
        return str(e)



@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        conversation_id = request.form.get("conversation_id", "default")
        message = request.form.get("message", "")

        response = get_bot_response(message, conversation_id)
        
        return jsonify({"response": response}), 200

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