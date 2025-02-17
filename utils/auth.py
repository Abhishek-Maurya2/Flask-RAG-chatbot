import ssl
from utils.db import supabase

# WARNING: Disabling certificate verification is insecure for production
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
            return {"message": "User already exists with this email"}, 400

        # Prepare user data payload
        data = {
            "name": name,
            "imgurl": imgUrl,
            "email": email,
            "password": password,  # Note: Hash the password before storing in production
            "chats": [],  # Initialize chats as an empty list
            "system_prompt": system_prompt.strip() if system_prompt and system_prompt.strip() else "Default system prompt"
        }
        
        # Insert the new user into the database
        res = supabase.table("users").insert(data).execute()
        if res.error:
            return {"message": res.error.message}, 500
        
        return {"message": "Registration successful", "data": res.data}, 201
    
    except Exception as e:
        return {"message": str(e)}, 500

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