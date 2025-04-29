# agent4.py
import requests
import os
import re

from dotenv import load_dotenv
load_dotenv()
llm_base_url = os.getenv("LLM_BASE_URL")
llm_model_id = os.getenv("LLM_MODEL_ID")

def check_paper_relevance_and_keywords(title, search_string):
    headers = {"Content-Type": "application/json"}
    # Adjust the prompt to ask for relevance and keywords
    prompt = (f"Determine if the paper titled '{title}' is relevant to the topic '{search_string}'. "
              "and in return just informed paper is relevant or paper is not relevant, to the point.")

    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a knowledgeable assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(f"{llm_base_url}/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        response_text = result['choices'][0]['message']['content'].strip().lower()
        print(response_text)
        # Check for explicit confirmation of relevance
        if "not relevant" in response_text:
            return False
        else:
            # Assuming the model lists keywords after confirming relevance
            # Extracting keywords from the response assuming they are listed after "key words:" phrase
            return True
    else:
        print(f"Error: {response.status_code}, Detail: {response.text}")
    
    return (False, [])

def filter_papers_with_gpt_turbo(search_string, papers):

    filtered_papers = []

    for paper in papers:
        title = paper['title']
        if check_paper_relevance_and_keywords(title, search_string):
            filtered_papers.append(paper)
            
    return filtered_papers


def is_response_relevant(response):
    # Define a pattern that matches sentences indicating irrelevance
    irrelevance_pattern = re.compile(r"does not appear to be directly relevant", re.IGNORECASE)
    
    # Define a pattern that matches sentences indicating relevance
    relevance_pattern = re.compile(r"topics related", re.IGNORECASE)
    
    # Check for irrelevance
    if irrelevance_pattern.search(response):
        return False  # Irrelevant based on the matched pattern
    
    # Check for relevance
    if relevance_pattern.search(response):
        return True  # Relevant based on the matched pattern
    
    # If neither pattern is matched, you might decide based on other criteria or default assumption
    return None  # Or False/True based on your default assumption


def generate_response_gpt4_turbo(question, papers_info):
    messages = [{
        "role": "system",
        "content": "You are a knowledgeable assistant who can answer research questions based on provided papers information."
    }]

    papers_context = "\n".join([f"- Title: '{paper['title']}', Author: {paper['creator']}, Year: {paper['year']}'." for paper in papers_info])
    messages.append({
        "role": "system",
        "content": f"Research Question: {question}\n\nPapers Information:\n{papers_context}"
    })
    
    messages.append({
        "role": "user",
        "content": "Based on the provided papers information, please answer the research question and cite relevant references for cross-verification."
    })
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "model": llm_model_id,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 256
    }
    
    response = requests.post(f"{llm_base_url}/v1/chat/completions", headers=headers, json=data, timeout=800)
    
    if response.status_code == 200:
        result = response.json()
        latest_response = result['choices'][0]['message']['content']
        return latest_response
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return "An error occurred while generating the response."