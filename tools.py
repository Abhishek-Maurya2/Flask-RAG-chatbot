import base64
import io
import qrcode
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from news import main

load_dotenv()

my_local_tools = [
    {
        "type": "function",
        "function": {
            "name": "newsFinder",
            "description": "Retrieves the news from the internet for the query you provide.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Topic to search for in the news.",
                    },
                    "required": [
                        "query",
                    ],
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "webSearch",
            "description": "Search the web for the query you provide and return [title](url) and description. as output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to search the web for.",
                    },
                    "required": [
                        "query",
                    ],
                },
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "imageSearch",
            "description": "Search the web for the query you provide and return image urls in proper markdown as output. Example ![ALT](URL)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to search the web for images.",
                    },
                    "required": [
                        "query",
                    ],
                },
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "readWebsite",
            "description": "Read the content of the website provided by the URL and return its content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the website to read.",
                    },
                    "required": [
                        "url",
                    ],
                },
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_qr_code",
            "description": "Generate a QR code from text data",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The text to encode in QR code"
                    }
                },
                "required": ["data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "WikipediaSearch",
            "description": "Search wikipedia for the query you provide and answer the question based on the search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to search wikipedia for.",
                    },
                    "required": [
                        "query",
                    ],
                },
            },
        }
    },
    {
        "type": "function",
        "function" : {
            "name": "code_executor",
            "description": "Execute the python code you provide and return the output. Code should be provided without any ``` or ```python",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to execute without any ``` or ```python",
                    },
                    "required": [
                        "code",
                    ],
                },
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sendEmail",
            "description": "Send an email using Gmail SMTP user name is Abhishek Kumar Maurya and email is 208akmaurya@gmail.com",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject of the email",
                    },
                    "message": {
                        "type": "string",
                        "description": "The body of the email",
                    },
                    "to_addr": {
                        "type": "string",
                        "description": "Recipient's email address",
                    },
                    "required": [
                        "subject",
                        "message",
                        "to_addr",
                    ],
                },
            },
        }
    }
]

def newsFinder(query: str) -> str:
    try:
        return main(query)
    except Exception as e:
        return f"Error: {str(e)}"

def webSearch(query: str) -> str:
    """Perform a web search and return top 3 links"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        "num": 5,
    }
    response = requests.get(url, params=params)
    data = response.json()
    output = ""
    count = 1
    for item in data["items"]:
        output += f"{count}. {item['title']}\n{item['link']}\n{item['snippet']}\n\n"
        output += "\nRemember to return it in proper markdown format example: 1. [\'title\'](\'url\')\n\'Description\'\n"
        count += 1
    return output

def imageSearch(query: str) ->str:
    """Search web for images using the given query and return urls"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        "searchType": "image",

    }
    response = requests.get(url, params=params)
    data = response.json()["items"]
    res = ""
    count = 1
    for item in data:
        res += f"{count}. URL: {item['link']}\nALT: {item['title']}\n\n"
        res += "\nRemember to return it in proper markdown format example: ![\'ALT\'](\'URL\')\n"
        count += 1
    return res

def read_website(url: str) -> str:
    """Read the content of the given website and return the text"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Cache-Control": "max-age=0",
        "Host": "www.google.com",
        "Referer": "https://www.google.com/",
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    return "\n\n".join([p.get_text() for p in paragraphs])

def generate_qr_code(data: str) -> str:
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def wikipediaSearch(query: str) -> str:
    """"search wikipedia for the query and return the texts on the webpage"""
    texts = ""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}"
        response = requests.get(url)
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        if search_results:
            page_id = search_results[0].get("pageid")
            page_url = f"https://en.wikipedia.org/w/api.php?action=parse&format=json&pageid={page_id}"
            # print("\n\n", query, "\n\n", page_url, "\n\n")
            page_response = requests.get(page_url)
            page_data = page_response.json()
            page_text = page_data.get("parse", {}).get("text", {}).get("*")
            soup = BeautifulSoup(page_text, "html.parser")
            paragraphs = soup.find_all("p")
            texts = "\n\n".join([p.get_text() for p in paragraphs])
        texts = texts[:1800]
        return texts
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"

def code_executor(code: str) -> str:
    """Execute the python code and return the output"""
    try:
        # send code to this url https://rag-webservice-vfpn.onrender.com/run for execution
    #      if "error" in result:
    #     return jsonify({"error": result["error"]}), 400
    # return jsonify({"output": result["output"]}), 200
    
    
        url = "https://rag-webservice-vfpn.onrender.com/run"
        # url = "http://192.168.1.24:3200/run"
        data = {
            "code": code
        }
        response = requests.post(url, json=data)
        data = response.json()
        if "error" in data or response.status_code != 200:
            # print("Error executing code:\n", data)
            return f"Error executing code: {data['error']}"
        return data["output"]
        
    except Exception as e:
        return f"Error executing code: {str(e)}"

def sendEmail(subject:str, message:str, to_addr:str) -> str:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    """
    Send an email using Gmail SMTP.
    
    Requires an App-Specific Password from Google:
    1. Enable 2-Step Verification in your Google Account
    2. Go to Security > App passwords
    3. Generate a new app password for 'Mail'
    4. Use that password instead of your regular Gmail password
    
    Args:
        subject (str): The subject of the email
        message (str): The body of the email
        from_addr (str): Sender's Gmail address
        to_addr (str): Recipient's email address
        password (str): Gmail App-Specific Password
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        from_addr = os.getenv("MAIL_FROM")
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_addr, os.getenv("MAIL_PASS"))
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)
        server.quit()
        return "Email sent successfully!\nto: " + to_addr + "\nsubject: " + subject + "\nmessage: " + message + "\n" + "from: " + from_addr
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return "Error sending email. Please check the logs for more details."

