# app.py
import re
from html import unescape
from flask import Flask, request, jsonify, render_template
import random
import requests  # Import requests to make API calls
from intents import intents  # Import the intents from intents.py

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    bot_response = get_bot_response(user_message)
    return jsonify({'response': bot_response})

def get_bot_response(message):
    message = message.lower()
    
    # Check for intents
    for intent, values in intents.items():
        for pattern in values['patterns']:
            if pattern in message:
                return random.choice(values['responses'])
    
    # If no intent matches, fetch information from Wikipedia
    return fetch_from_wikipedia(message)

def fetch_from_wikipedia(query):
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}&utf8=&srlimit=1"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Check if there are search results
        if 'query' in data and 'search' in data['query'] and len(data['query']['search']) > 0:
            title = data['query']['search'][0]['title']
            snippet = data['query']['search'][0]['snippet']
            
            # Remove HTML tags and unescape HTML entities
            snippet_clean = re.sub(r'<[^>]+>', '', snippet)  # Remove HTML tags
            snippet_clean = unescape(snippet_clean)  # Convert HTML entities
            
            # Limit snippet to one or two lines (approx. 200 characters)
            snippet_truncated = snippet_clean[:200].rsplit(' ', 1)[0] + "..." if len(snippet_clean) > 200 else snippet_clean
            
            return f"{snippet_truncated}"
        else:
            return "I couldn't find any information on that."
    
    except requests.exceptions.RequestException:
        return "I'm having trouble accessing the web right now."
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
