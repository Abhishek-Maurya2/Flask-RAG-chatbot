from flask import Blueprint, request, jsonify, render_template
from utils.logic import (
    get_bot_response,
    _initialize_conversation,
    switchKey,
)
from utils.db import (conversations, save_conversation_to_supabase, supabase)
from utils.systemPrompt import (get_sys_prompt, set_sys_prompt)

routes_blueprint = Blueprint("routes_blueprint", __name__)

@routes_blueprint.route("/")
def home():
    return render_template("chat.html")

@routes_blueprint.route("/chat", methods=["POST"])
def chat():
    try:
        # Expect user_id along with conversation_id and message
        user_id = request.form.get("user_id", "default")
        conversation_id = request.form.get("conversation_id", "default")
        message = request.form.get("message", "")
        response = get_bot_response(message, conversation_id, user_id)
        return jsonify({"response": response}), 200
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/delete", methods=["DELETE"])
def clear_history():
    try:
        # Expect user_id to clear only that user's conversations
        user_id = request.args.get("user_id", "default")
        # Clear only conversations for the given user
        keys_to_delete = [k for k, v in conversations.items() if v and v[0].get("user_id", user_id) == user_id]
        for key in keys_to_delete:
            conversations.pop(key, None)
        supabase.table("conversations").delete().eq("user_id", user_id).execute()
        return jsonify({"message": "All conversations deleted for the user"}), 200
    except Exception as e:
        print(f"Clear history error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/delete/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    try:
        user_id = request.args.get("user_id", "default")
        conversations.pop(conversation_id, None)
        supabase.table("conversations").delete()\
            .eq("conversation_id", conversation_id)\
            .eq("user_id", user_id).execute()
        return jsonify({"message": "Conversation deleted"}), 200
    except Exception as e:
        print(f"Delete conversation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/delete/<conversation_id>/<idx>", methods=["DELETE"])
def delete_message(conversation_id, idx):
    try:
        user_id = request.args.get("user_id", "default")
        idx = int(idx)
    except ValueError:
        return jsonify({"error": "Index must be an integer"}), 400

    try:
        if conversation_id not in conversations:
            from utils.db import get_conversation_from_supabase
            messages = get_conversation_from_supabase(conversation_id, user_id)
            if messages:
                conversations[conversation_id] = messages
            else:
                return jsonify({"error": "Conversation not found"}), 404

        count = 0
        delete_index = None
        for i, msg in enumerate(conversations[conversation_id]):
            if msg.get("role") == "user":
                count += 1
            if count == idx:
                delete_index = i
                break

        if delete_index is None:
            return jsonify({"error": "Invalid index"}), 400

        conversations[conversation_id] = conversations[conversation_id][:delete_index]
        save_conversation_to_supabase(conversation_id, user_id)
        return jsonify({"message": "Messages after the given index deleted"}), 200
    except Exception as e:
        print(f"Delete message error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/history")
def list_history():
    try:
        user_id = request.args.get("user_id", "default")
        res = supabase.table("conversations").select("*").eq("user_id", user_id).execute()
        return jsonify(res.data), 200
    except Exception as e:
        print(f"List history error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/history/<conversation_id>")
def get_history(conversation_id):
    try:
        user_id = request.args.get("user_id", "default")
        _initialize_conversation(user_id, conversation_id)
        return jsonify(conversations.get(conversation_id, []))
    except Exception as e:
        print(f"Get history error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/set-system-prompt", methods=["POST"])
def set_system_prompt_route():
    try:
        system_prompt = request.form.get("system_prompt")
        user_id = request.form.get("user_id", "default")
        set_sys_prompt(user_id, system_prompt)
        return jsonify({"message": "System prompt updated"}), 200
    except Exception as e:
        print(f"Set system prompt error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/get-system-prompt")
def get_system_prompt_route():
    try:
        user_id = request.args.get("user_id", "default")
        return jsonify({"system_prompt": get_sys_prompt(user_id)}), 200
    except Exception as e:
        print(f"Get system prompt error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/switch-api", methods=["GET"])
def switch_api():
    try:
        switchKey()
        return jsonify({"message": "API key switched"}), 200
    except Exception as e:
        print(f"Switch API error: {str(e)}")
        return jsonify({"error": str(e)}), 500