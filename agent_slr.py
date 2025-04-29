# agents2.py
import re

import requests
import json
import os
from dotenv import load_dotenv

from agent_summary import llm_model_id, llm_base_url

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


def generate_research_questions_and_purpose_with_gpt(objective, num_questions):

    headers = {
        "Content-Type": "application/json"
    }
    # Construct the prompt dynamically
    prompt_content = f"You are a helpful assistant capable of generating research questions along with their purposes for a systematic literature review.\n"
    prompt_content = f"Given the research objective: '{objective}', generate {num_questions} distinct research questions, each followed by its specific purpose. 'To examine', or 'To investigate'."
    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant capable of generating research questions along with their purposes for a systematic literature review."},
            {"role": "user", "content": prompt_content}
        ],
        "temperature": 0.7
    }
    response = requests.post(f"{llm_base_url}/v1/chat/completions", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        messages = result['choices'][0]['message']['content']
        lines = [line for line in messages.strip().split('\n') if line]

        question_purpose_objects = []
        for i in range(0, len(lines), 2):
            # Using regex to dynamically remove "Research question X:" where X is any number
            question = re.sub(r"^Research question( \d+)?: ", "", lines[i], flags=re.IGNORECASE)
            purpose = lines[i+1] if i+1 < len(lines) else "Purpose not provided"
            # Optionally, remove the prefix from purpose if needed
            # purpose = purpose.replace("Purpose: ", "")
            question_purpose_objects.append({"question": question, "purpose": purpose})

        if num_questions == 1 and question_purpose_objects:

            return {"research_questions": question_purpose_objects}
        else:
            return {"research_questions": question_purpose_objects}
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []
