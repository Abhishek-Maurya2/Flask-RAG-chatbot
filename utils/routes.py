from flask import Blueprint, request, jsonify, render_template
from utils.logic import (
    get_bot_response,
    conversations,
    get_sys_prompt,
    set_sys_prompt,
    save_conversation_to_supabase,
    _initialize_conversation,
    supabase,
)

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
        print(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@routes_blueprint.route("/delete", methods=["DELETE"])
def clear_history():
    try:
        conversations.clear()
        supabase.table("conversations").delete().neq("conversation_id", "").execute()
        return jsonify({"message": "All conversations deleted"}), 200
    except Exception as e:
        print(f"Clear history error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@routes_blueprint.route("/delete/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    try:
        conversations.pop(conversation_id, None)
        supabase.table("conversations").delete().eq("conversation_id", conversation_id).execute()
        return jsonify({"message": "Conversation deleted"}), 200
    except Exception as e:
        print(f"Delete conversation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@routes_blueprint.route("/delete/<conversation_id>/<idx>", methods=["DELETE"])
def delete_message(conversation_id, idx):
    try:
        idx = int(idx)
    except ValueError:
        return jsonify({"error": "Index must be an integer"}), 400

    try:
        # Load conversation from in-memory store or fetch from Supabase if missing
        if conversation_id not in conversations:
            from utils.logic import get_conversation_from_supabase  # Import locally if needed
            messages = get_conversation_from_supabase(conversation_id)
            if messages:
                conversations[conversation_id] = messages
            else:
                return jsonify({"error": "Conversation not found"}), 404

        # Determine the deletion index based on the count of user messages
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

        # Truncate conversation messages up to the deletion index
        conversations[conversation_id] = conversations[conversation_id][:delete_index]

        # Update Supabase with the truncated conversation
        save_conversation_to_supabase(conversation_id)
        return jsonify({"message": "Messages after the given index deleted"}), 200
    except Exception as e:
        print(f"Delete message error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/history")
def list_history():
    try:
        res = supabase.table("conversations").select("*").execute()
        return jsonify(res.data), 200
    except Exception as e:
        print(f"List history error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@routes_blueprint.route("/history/<conversation_id>")
def get_history(conversation_id):
    _initialize_conversation(conversation_id)
    return jsonify(conversations.get(conversation_id, []))


@routes_blueprint.route("/set-system-prompt", methods=["POST"])
def set_system_prompt_route():
    try:
        system_prompt = request.form.get("system_prompt")
        set_sys_prompt(system_prompt)
        return jsonify({"message": "System prompt updated"}), 200
    except Exception as e:
        print(f"Set system prompt error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@routes_blueprint.route("/get-system-prompt")
def get_system_prompt_route():
    try:
        return jsonify({"system_prompt": get_sys_prompt()}), 200
    except Exception as e:
        print(f"Get system prompt error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Optional WhatsApp Route (Commented out)
# @routes_blueprint.route("/whatsapp", methods=["GET", "POST"])
# def whatsapp():
#     from twilio.twiml.messaging_response import MessagingResponse
#     whatsapp_client = MessagingResponse()
#     msg = request.values.get("Body", "")
#     number = request.values.get("From", "")
#     
#     try:
#         res = get_bot_response(msg, number)
#         if len(res) > 1000:
#             whatsapp_client.message(res[:1000])
#             whatsapp_client.message(res[1000:])
#         else:
#             whatsapp_client.message(res)
#         return str(whatsapp_client)
#     except Exception as e:
#         whatsapp_client.message("Failed to process request: " + str(e))
#         return str(whatsapp_client)