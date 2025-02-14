import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

conversations = {}

def save_conversation_to_supabase(conversation_id: str) -> None:
    try:
        data = conversations.get(conversation_id, [])
        supabase.table("conversations").upsert({
            "conversation_id": conversation_id,
            "messages": data
        }).execute()
    except Exception as e:
        print(f"Error saving conversation to supabase: {str(e)}")

def get_conversation_from_supabase(conversation_id: str):
    try:
        res = supabase.table("conversations").select("*").eq("conversation_id", conversation_id).execute()
        if res.data:
            return res.data[0]["messages"]
    except Exception as e:
        print(f"Error getting conversation from supabase: {str(e)}")
