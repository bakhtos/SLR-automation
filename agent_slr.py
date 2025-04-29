import requests
import json
import os
from dotenv import load_dotenv

from agent_summary import llm_model_id, llm_base_url

load_dotenv()
llm_base_url = os.getenv("LLM_BASE_URL")
llm_model_id = os.getenv("LLM_MODEL_ID")


def llm_search_string(objective, research_questions):

    headers = {
        "Content-Type": "application/json"
    }
    # Removed the explicit instruction for logical operators
    user_prompt = (f"Given the research objective: '{objective}', and the following research questions: {', '.join(research_questions)}, generate one concise search string for identifying relevant literature for literature review.")
    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant assisting with the literature reviews. Your aim to provide relevant search string based on the given research objectives and questions. Only the search string should be in the response"},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    response = requests.post(f"{llm_base_url}/v1/chat/completions", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content.strip()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return "An error occurred while generating the search string."


def llm_research_questions(objective, num_questions):

    headers = {
        "Content-Type": "application/json"
    }
    # Construct the prompt dynamically
    user_prompt = f"Given the research objective: '{objective}', generate {num_questions} distinct research questions, each followed by its specific purpose."
    data = {
        "model": llm_model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant capable of generating research questions along with their purposes for a systematic literature review."
                                          "For X requested research questions, your output should contain 2X lines - a research question followed by the purpose."
                                          "Do not start lines with 'Research question' or 'Purpose', output only the relevant text."},
            {"role": "user", "content": user_prompt}
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
            question = lines[i]
            purpose = lines[i+1] if i+1 < len(lines) else "Purpose not provided"
            question_purpose_objects.append({"question": question, "purpose": purpose})


        return {"research_questions": question_purpose_objects}
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []
