# agents2.py
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
llm_base_url = os.getenv("LLM_BASE_URL")
llm_model_id = os.getenv("LLM_MODEL_ID")

def extract_search_string(content):
    possible_operators = ['AND', 'OR', 'NOT', '"']
    for line in content.split('\n'):
        if any(op in line for op in possible_operators):
            return line
    return content
def generate_search_string_with_gpt(objective, research_questions):

    headers = {
        "Content-Type": "application/json"
    }
    # Removed the explicit instruction for logical operators
    combined_prompt = f"Given the research objective: '{objective}', and the following research questions: {', '.join(research_questions)}, generate two concise search string for identifying relevant literature for literature review.Do not include OR. Use AND if needed."
    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": combined_prompt}
        ],
        "temperature": 0.7
    }
    response = requests.post(f"{llm_base_url}/v1/chat/completions", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        search_string = extract_search_string(content)
        return search_string.strip()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return "An error occurred while generating the search string."