import base64
import io
import qrcode
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from news import main
import json
import re

load_dotenv()

# <function=newsFinder{"query": "HMPV virus in India"}</function>
def parse_tool_calls(response: str):
    try:
        pattern = r'<function=(.*?){(.*?)</function>'
        pattern2 = r'<function=(.*?) {(.*?) </function>'
        matches = re.findall(pattern, response)
        if not matches:
            matches = re.findall(pattern2, response)
        name = matches[0][0]
        params = "{" + matches[0][1]
        # random id
        id = "call_5t3r"
        res = []
        res.append({
            "id": id,
            "type": "function",
            "function": {
                "name": name,
                "arguments": json.loads(params)
            }
        })
        return res
    except Exception as e:
        print(response)
        print(f"Error parsing tool calls: {str(e)}")
        return None
    


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

def image_search(query: str) ->str:
    """Search web for images using the given query and return urls"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        "searchType": "image",
        "num": 5,

    }
    response = requests.get(url, params=params)
    data = response.json()["items"]
    res = ""
    for item in data:
        res += f"URL: {item['link']}\n\nTitle: {item['title']}\n\n"
    return res

def search_wikipedia_for_extra_information(query: str) -> str:
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

def web_search(query: str) -> str:
    """Perform a web search and return top 3 links"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        
    }
    response = requests.get(url, params=params)
    data = response.json()
    output = ""
    for item in data["items"]:
        output += f"Title: {item['title']}\n"
        output += f"URL: {item['link']}\n\n"
        output += f"Description: {item['snippet']}\n\n"
    return output

def newsFinder(query: str) -> str:
    try:
        return main(query)
    except Exception as e:
        return f"Error: {str(e)}"
