# agents.py
import requests
import json
from flask import jsonify
import os

from dotenv import load_dotenv
load_dotenv()
llm_base_url = os.getenv("LLM_BASE_URL")
llm_model_id = os.getenv("LLM_MODEL_ID")


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
