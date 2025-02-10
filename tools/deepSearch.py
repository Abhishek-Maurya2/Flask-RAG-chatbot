import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from groq import Groq
from collections import deque

load_dotenv()
llm = Groq(api_key=os.getenv('GROQ_API_KEY'))

def getLinks(query, num=3):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        "num": num
    }
    response = requests.get(url, params=params)
    data = response.json()
    links = []
    if "items" in data:
        for item in data["items"]:
            if("wikipedia" in item["link"].lower()):
                continue
            links.append({
                "link": item["link"],
                "title": item["title"]
            })
    return links

def readContent(url, limit=500):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n\n".join([p.get_text() for p in paragraphs])[:limit]
    except Exception:
        return ""

def getResponse(context, question, model='llama-3.3-70b-versatile'):
    messages = [
        {"role": "system", "content": "You are an expert research assistant."},
        {"role": "user", "content": f"{question}\n\nContext: {context}"}
    ]
    response = llm.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def wikipediaSearch(query):
    texts = ""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}"
        response = requests.get(url)
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        if search_results:
            page_id = search_results[0].get("pageid")
            page_url = f"https://en.wikipedia.org/w/api.php?action=parse&format=json&pageid={page_id}"
            page_response = requests.get(page_url)
            page_data = page_response.json()
            page_text = page_data.get("parse", {}).get("text", {}).get("*", "")
            soup = BeautifulSoup(page_text, "html.parser")
            paragraphs = soup.find_all("p")
            texts = "\n\n".join([p.get_text() for p in paragraphs])
        return texts[:1800]
    except Exception as e:
        return f"Error: {str(e)}"

def imageSearch(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "q": query,
        "searchType": "image",
        "num": 2,
    }
    response = requests.get(url, params=params)
    data = response.json()
    res = ""
    if "items" in data:
        for item in data["items"]:
            res += f"![{item['title']}]({item['link']})\n"
    return res

def extractRelatedTopics(text):
    prompt = (
        "From the following content, list additional only 3 related topics that should be researched to provide a comprehensive report. List only distinct topics separated by commas and nothing else not a single extra word.\n\n"
        f"{text}\n\nTopics:"
    )
    topics_str = getResponse(text, prompt)
    topics = [t.strip() for t in topics_str.split(",") if t.strip()]
    return topics

def processTopic(topic):
    print(f"Processing topic: {topic}\n")
    content_parts = {}
    
    wiki_content = wikipediaSearch(topic)
    if wiki_content and not wiki_content.startswith("Error"):
        content_parts['Wikipedia'] = wiki_content

    links = getLinks(topic, num=3)
    web_content = ""
    for link in links:
        page_text = readContent(link['link'])
        if len(page_text) > 150:
            web_content += f"\nSource: [{link['title']}]({link['link']})\n{page_text}\n"
    if web_content:
        content_parts['Web'] = web_content

    # images = imageSearch(topic)
    # if images:
    #     content_parts['Images'] = images

    combined = "\n\n".join(content_parts.values())
    return combined, content_parts

def ai_agent_generate_report(initial_query):
    processed_topics = set()
    topics_queue = deque([initial_query])
    report_sections = {}
    max_topics = 7  # maximum number of topics to process

    while topics_queue and len(processed_topics) < max_topics:
        current_topic = topics_queue.popleft()
        topic_key = current_topic.lower()
        if topic_key in processed_topics:
            continue
        processed_topics.add(topic_key)
        content, sections = processTopic(current_topic)
        if not content:
            continue
        report_sections[current_topic] = sections
        new_topics = extractRelatedTopics(content)
        for nt in new_topics:
            nt_key = nt.lower()
            if nt_key not in processed_topics and nt not in topics_queue:
                topics_queue.append(nt)

    report_lines = ["# Comprehensive Report"]
    for topic, sections in report_sections.items():
        report_lines.append(f"## {topic}")
        if "Wikipedia" in sections:
            report_lines.append(f"### Wikipedia Summary\n{sections['Wikipedia']}")
        if "Web" in sections:
            report_lines.append(f"### Web Sources\n{sections['Web']}")
        # Uncomment below if Images section needed
        # if 'Images' in sections:
        #     report_lines.append(f"### Images\n{sections['Images']}")

    final_report = "\n\n".join(report_lines)
    refined_report = getResponse(
        final_report,
        f"Refine and format the following content into a detailed and structured report. Report:\n{final_report}",
    )
    return refined_report
