from groq import Groq
import os
import json
from tools.tools import ( my_local_tools, newsFinder, webSearch, imageSearch, read_website, generate_qr_code, wikipediaSearch, code_executor, sendEmail )
from tools.parseTool import get_tool

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
conversations = {}
sys_prompt = ""

def set_sys_prompt(value):
    global sys_prompt
    sys_prompt = value

def get_bot_response(user_query, conversation_id):
    if (conversation_id not in conversations):
        conversations[conversation_id] = [
            {
            "role": "system",
            "content": sys_prompt or "You are Luna, an AI assistant built by Abhishek. You have realtime access to the internet and can also send email in realtime and can help with a variety of tasks."
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
        
        if not tool_calls and len(response.choices[0].message.content) < 70:
            tool_calls = get_tool(response.choices[0].message.content)
            # print("\n\nTool Calls:\n", tool_calls)
            if tool_calls:
                response.choices[0].message.tool_calls = tool_calls
                response.choices[0].finish_reason = "tool_calls"
                response.choices[0].message.content = None
            # print("\n\nTool:\n",  response)
        
        if tool_calls:
            tools = {
                "newsFinder": newsFinder,
                "webSearch": webSearch,
                "imageSearch": imageSearch,
                "readWebsite": read_website,
                "generate_qr_code": generate_qr_code,
                "WikipediaSearch": wikipediaSearch,
                "code_executor": code_executor,
                "sendEmail": sendEmail
            }
            
            try:
                for tool_call in tool_calls:
                    name = tool_call.function.name
                    func = tools[name]
                    args = json.loads(tool_call.function.arguments)
                    res = func(**args)
                    
                    # print("Tool Response: ", res)
                    
                    if name == "generate_qr_code":
                        qr_tool = res
                        res = f"data:image/png;base64,{res}"
                    
                    conversations[conversation_id].append({"role": "tool", "content": res, "tool_call_id" : tool_call.id, "name" : name})
                
                
                finalResponse = client.chat.completions.create(
                    messages=conversations[conversation_id],
                    model = "llama-3.3-70b-versatile",
                    )
                
                finalRes = finalResponse.choices[0].message.content
                if(qr_tool):
                    finalRes += f"\n\n<img src='data:image/png;base64,{qr_tool}' alt='QR Code' class='rounded h-[300px] w-[300px] rouned-2xl mt-3 '/>"
                conversations[conversation_id].append({"role": "assistant", "content": finalRes})
                return finalRes
                
                
            except Exception as e:
                return "Failed to call tool: " + str(e)
            
        
        res = response.choices[0].message.content
        if qr_tool:
            res += f"\n\n<img src='data:image/png;base64,{qr_tool}' alt='QR Code' class='rounded h-[300px] w-[300px] rouned-2xl mt-3 '/>"
            
        conversations[conversation_id].append({"role": "assistant", "content": res})
        return res
    
    except Exception as e:
        print("Error: ", e)
        return str(e)