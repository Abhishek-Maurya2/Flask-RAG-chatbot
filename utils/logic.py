from groq import Groq
import os
import json
from tools.tools import ( my_local_tools, newsFinder, webSearch, imageSearch, read_website, generate_qr_code, wikipediaSearch, code_executor, sendEmail )
from tools.parseTool import get_tool
from utils.db import conversations, save_conversation_to_supabase, get_conversation_from_supabase
from utils.systemPrompt import get_sys_prompt

_switchKey = False
def switchKey():
    global _switchKey
    _switchKey = not _switchKey
    return _switchKey

client = Groq(api_key= _switchKey and os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_2"))

def _initialize_conversation(user_id: str, conversation_id: str) -> None:
    if conversation_id not in conversations:
        data = get_conversation_from_supabase(conversation_id, user_id)
        if data:
            conversations[conversation_id] = data
        else:
            conversations[conversation_id] = [{
                "role": "system",
                "content": get_sys_prompt(user_id)
            }]

TOOLS = {
    "newsFinder": newsFinder,
    "webSearch": webSearch,
    "imageSearch": imageSearch,
    "readWebsite": read_website,
    "generate_qr_code": generate_qr_code,
    "WikipediaSearch": wikipediaSearch,
    "code_executor": code_executor,
    "sendEmail": sendEmail,
}

def _handleTools(tool_calls, conversation_id, user_id):
    qr_tool = None
    for t in tool_calls:
        name = t.function.name
        func = TOOLS[name]
        if not func:
            continue
        
        try:
            args = json.loads(t.function.arguments)
            res = func(**args)
            
            if name == "generate_qr_code":
                qr_tool = res
                res = f"data:image/png;base64,{res}"
            
            conversations[conversation_id].append({"role": "tool", "content": res, "tool_call_id" : t.id, "name" : name})
        
        except json.JSONDecodeError as e:
            return f"JSON Decode Error: {str(e)}"
        except Exception as e:
            return f"Tool {name} execution failed: {str(e)}"
    
    try:
        finalRes = client.chat.completions.create(
            messages=conversations[conversation_id],
            model = "llama-3.3-70b-versatile",
            ).choices[0].message.content
        
        if qr_tool:
            finalRes += f"\n\n<img src='data:image/png;base64,{qr_tool}' alt='QR Code' class='rounded h-[300px] w-[300px] rouned-2xl mt-3 '/>"
        
        conversations[conversation_id].append({"role": "assistant", "content": finalRes})
        save_conversation_to_supabase(conversation_id, user_id)
        return finalRes
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_bot_response(user_query, conversation_id, user_id):
    _initialize_conversation(user_id, conversation_id)
    
    conversations[conversation_id].append({"role": "user", "content": user_query})

    try:
        # Initial response with tool calls
        response = client.chat.completions.create(
            messages=conversations[conversation_id],
            model = "llama-3.3-70b-versatile",
            tools=my_local_tools,
            tool_choice="auto",
        )
        
        
        tool_calls = response.choices[0].message.tool_calls
        
        if not tool_calls and len(response.choices[0].message.content) < 70 and len(response.choices[0].message.content) > 35:
            tool_calls = get_tool(response.choices[0].message.content)
            if tool_calls:
                response.choices[0].message.tool_calls = tool_calls
                response.choices[0].finish_reason = "tool_calls"
                response.choices[0].message.content = None
        
        if tool_calls:  
            return _handleTools(tool_calls, conversation_id, user_id)
            
        
        res = response.choices[0].message.content
        conversations[conversation_id].append({"role": "assistant", "content": res})
        save_conversation_to_supabase(conversation_id, user_id)
        return res
    
    except Exception as e:
        return str(e)