# agents.py
import requests
import json
from flask import jsonify
import os
import re  # Import the regular expressions library

from dotenv import load_dotenv
load_dotenv()
llm_base_url = os.getenv("LLM_BASE_URL")
llm_model_id = os.getenv("LLM_MODEL_ID")

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



def generate_summary_conclusion(papers_info):
    headers = {"Content-Type": "application/json"}

    prompt_parts = ["Summarize the conclusions of the following papers:"]
    for paper in papers_info:
        title = paper.get("title")
        author = paper.get("creator", "An author")
        year = paper.get("year", "A year")
        prompt_parts.append(f"- '{title}' by {author} ({year})")
    prompt = " ".join(prompt_parts)

    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(
        f"{llm_base_url}/v1/chat/completions",
        headers=headers,
        data=json.dumps(data),
    )

    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        summary_conclusion = content.strip()
    else:
        return jsonify({"error": "Failed to generate a summary conclusion."}), 500

    return summary_conclusion


def generate_abstract_with_openai(prompt):
    """Generates a summary abstract using OpenAI's GPT model based on the provided prompt."""
    # Fetching the API key from environment variables for better security practice

    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(f"{llm_base_url}/v1/chat/completions", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content.strip()
    else:
        raise Exception("Failed to generate a summary abstract from OpenAI.")


def generate_introduction_summary_with_openai(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(f"{llm_base_url}/v1/chat/completions", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content.strip()
    else:
        raise Exception("Failed to generate the introduction summary from OpenAI.")
