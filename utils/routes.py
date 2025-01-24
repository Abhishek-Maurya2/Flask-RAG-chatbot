from flask import Blueprint, request, jsonify, render_template
from utils.logic import get_bot_response, conversations, sys_prompt, set_sys_prompt
# from twilio.twiml.messaging_response import MessagingResponse


routes_blueprint = Blueprint("routes_blueprint", __name__)

@routes_blueprint.route("/")
def home():
    return render_template("chat.html")

@routes_blueprint.route("/chat", methods=["POST"])
def chat():
    try:
        conversation_id = request.form.get("conversation_id", "default")
        message = request.form.get("message", "")

        response = get_bot_response(message, conversation_id)
        
        return jsonify({"response": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/delete", methods=["DELETE"])
def clear_history():
    try:
        conversations.clear()
        return jsonify({"message": "History cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/delete/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    try:
        conversations.pop(conversation_id)
        return jsonify({"message": "Conversation deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/delete/<conversation_id>/<idx>", methods=["DELETE"])
def delete_message(conversation_id, idx):
    idx = int(idx)
    try:
        # remove everything after the index idx where idx is the index of the message where role is user
        count = 0
        for i, msg in enumerate(conversations[conversation_id]):
            if msg["role"] == "user":
                count += 1
            if count == idx:
                idx = i
                break
        
        conversations[conversation_id] = conversations[conversation_id][:idx]
        return jsonify({"message": "Message deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @routes_blueprint.route("/edit/<conversation_id>/<idx>", methods=["POST"])
# def edit_message(conversation_id, idx):
#     idx = int(idx)
#     try:
#         # remove everything after the index idx where idx is the index of the message where role is user
#         count = 0
#         for i, msg in enumerate(conversations[conversation_id]):
#             if msg["role"] == "user":
#                 count += 1
#             if count == idx:
#                 idx = i
#                 break
        
#         conversations[conversation_id] = conversations[conversation_id][:idx]
#         return jsonify({"message": "Message deleted"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/history")
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

@routes_blueprint.route("/history/<conversation_id>")
def get_history(conversation_id):
    return jsonify(conversations.get(conversation_id, []))

@routes_blueprint.route("/set-system-prompt", methods=["POST"])
def set_system_prompt():
    try:
        sys_prompt = request.form.get("system_prompt")
        set_sys_prompt(sys_prompt)
        return jsonify({"message": "System prompt updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/get-system-prompt")
def get_system_prompt():
    return jsonify({"system_prompt": sys_prompt}) if sys_prompt else jsonify({"message": "No system prompt set"})

# @routes_blueprint.route("/whatsapp", methods=['GET', 'POST'])
# def whatsapp():
    whatsapp_client = MessagingResponse()
    msg = request.values.get('Body', '')
    number = request.values.get('From', '')
    # user_profile = request.values.get('ProfileName', '')
    
    try:
        res = get_bot_response(msg, number)
        
        if len(res) > 1000:
            whatsapp_client.message(res[:1000])
            whatsapp_client.message(res[1000:])
        else:
            whatsapp_client.message(res)
        
        return str(whatsapp_client)
        
    except Exception as e:
        whatsapp_client.message("Failed to process request: " + str(e))
        return str(whatsapp_client)