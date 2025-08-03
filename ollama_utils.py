# ollama_utils.py

import ollama
from duckduckgo_search import DDGS

def run_ollama(prompt, model='llama3'):
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

def search_duckduckgo(query, max_results=5):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(f"- {r['title']}: {r['href']} — {r['body']}")
    return "\n".join(results)