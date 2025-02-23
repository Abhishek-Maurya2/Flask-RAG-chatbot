from utils.db import supabase
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def register_user(name: str, imgUrl: str, email: str, password: str, system_prompt: str = None) -> tuple:
    """
    Registers a new user if one does not already exist.

    Returns a tuple with a response dictionary and an HTTP status code.
    """
    try:
        # Check if a user with the provided email already exists
        existing = supabase.table("users").select("*").eq("email", email).execute()
        if existing.data:
            return {"error": "User already exists with this email"}, 400
        
        # Insert the new user into the database
        user = {
            "name": name,
            "imgurl": imgUrl,
            "email": email,
            "password": password,
            "system_prompt": system_prompt
        }
        
        res = supabase.table("users").insert(user).execute()
        return {"message": "User registered successfully", "data": res.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def login_user(email: str, password: str) -> tuple:
    """
    Authenticates a user using their email and password.

    Returns a tuple with a response dictionary and an HTTP status code.
    """
    try:
        # Query for a user with matching email and password
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        if res.data:
            return {"message": "Login successful", "data": res.data[0]}, 200
        else:
            return {"error": "Invalid credentials"}, 401
    except Exception as e:
        return {"error": str(e)}, 500