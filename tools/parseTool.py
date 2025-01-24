from pydantic import BaseModel
from groq import Groq
import os
import json
from typing import Dict
from dotenv import load_dotenv
from tools.tools import my_local_tools

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Function(BaseModel):
    name: str
    arguments: str  # Change type to str

class ChatCompletionMessageToolCall(BaseModel):
    id: str
    function: Function
    type: str

def get_tool(msg):
    conversations = [
        {
            "role": "system",
            "content": f"""Return all of your response in JSON format. with attribute toolNeeded, name and parameters only.\n\nTools are: {str(my_local_tools)}\n\n\nExample:
            {{
                "toolNeeded": true,
                "name": "newsFinder",
                "parameters": {{
                    "query": "HMPV virus in India"
                }}
            }}\n\nNOTE: Do not include any other information in the response and don't use backticks(```). If toolNeeded false leave other parameter blank and toolNeeded=true.
            """
        }
    ]
    
    conversations.append({"role": "user", "content": msg})
    
    try:
        response = client.chat.completions.create(
            messages=conversations,
            model = "llama-3.1-8b-instant",
        )
        
        res = response.choices[0].message.content
        res = json.loads(res)
        
        needed = res.get("toolNeeded")
        if not needed:
            return None
        
        name = res.get("name")
        
        if name not in ["newsFinder", "webSearch", "imageSearch", "readWebsite", "generate_qr_code", "WikipediaSearch", "code_executor", "sendEmail"]:
            print("Invalid tool name:", name)
            return None
        
        params = res.get("parameters")
        id = "call_" + name
        
        tool_call = ChatCompletionMessageToolCall(
            id=id,
            function=Function(
                name=name,
                arguments=json.dumps(params)  # Convert dict to JSON string
            ),
            type="function"
        )
        
        return [tool_call]
        
    except Exception as e:
        print("Error getting tool:", str(e))
        return None

# print(get_tool("<function=newsFinder{'query': 'HMPV virus in India'}>"))



# def runTool():
    