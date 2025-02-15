# ...existing imports...
from utils.db import supabase

def register_user(name: str, imgUrl: str, email: str, password: str, system_prompt: str = None) -> dict:
    try:
        data = {
            "name": name,
            "imgUrl": imgUrl,
            "email": email,
            "password": password,  # in production, hash the password
            "chats": [],  # initialize chats for the user
            "system_prompt": system_prompt.strip() if system_prompt and system_prompt.strip() else "Default system prompt"
        }
        res = supabase.table("users").insert(data).execute()
        if res.error:
            return {"error": res.error.message}
        return {"message": "Registration successful", "data": res.data}
    except Exception as e:
        return {"error": str(e)}

def login_user(email: str, password: str) -> dict:
    try:
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        if res.data:
            return {"message": "Login successful", "user": res.data[0]}
        return {"error": "Invalid credentials"}
    except Exception as e:
        return {"error": str(e)}
