from groq import Groq
import os
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
llm = Groq(api_key=os.getenv('GROQ_API_KEY'))

def getLinks(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        "num": 6
        
    }
    response = requests.get(url, params=params)
    data = response.json()
    links = []
    for item in data["items"]:
        links.append({
            "link" : item["link"],
            "title" : item["title"]
        })
    return links

def readContent(url):
    """Read the content of the given website and return the text"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n\n".join([p.get_text() for p in paragraphs])[:500]
    except Exception as e:
        print(e)
        return ""

def getResponse(context, question):
    message = [
        {
            "role":"system",
            "content":"Hello! How can I help you today?"
        },
        {
            "role":"user",
            "content": f"Answer the following question: {question}\n\nContext: {context}"
        },
    ]
    response = llm.chat.completions.create(
        model = 'llama-3.3-70b-versatile',
        messages = message,
    )
    return response.choices[0].message.content

def main(question):
    links = getLinks(question)
    responses = ""
    count = 1
    for link in links:
        print(f"{count}. Reading content from {link['link']}")
        context = readContent(link['link'])
        if(len(context) < 90):
            print(f"{count}. Context too short.")
            continue
        
        print(f"{count}. Generating response")
        response = getResponse(context, question)
        
        responses += f"Source: [{link['title']}]({link['link']})\nResponse: {response}\n\n"
        count += 1
    
    answer = getResponse(responses, f"Answer my question in detail and also mention the sources at the end. Question:  {question}")
    return answer
