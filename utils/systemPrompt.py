DEFAULT_PROMPT = (
    "You are Luna, an AI assistant built by Abhishek. "
    "You have realtime access to the internet and can help with a variety of tasks. "
    "Use will only use one tool at a time"
)

def get_sys_prompt(user_id: str) -> str:
    from utils.db import supabase
    try:
        # from users table update system_prompt column with user_id
        res = supabase.table("users")\
            .select("system_prompt")\
            .eq("user_id", user_id)\
            .execute()
        if res.data:
            return res.data[0].get("system_prompt", DEFAULT_PROMPT)        
    except Exception as e:
        print(f"Error getting system prompt: {str(e)}")
    return DEFAULT_PROMPT

def set_sys_prompt(user_id: str, value: str) -> None:
    from utils.db import supabase
    try:
        # from users table update system_prompt column with user_id
        res = supabase.table("users")\
            .update({"system_prompt": value})\
            .eq("user_id", user_id)\
            .execute()
    except Exception as e:
        print(f"Error setting system prompt: {str(e)}")
