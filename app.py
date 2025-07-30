import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)

CORS(app)

from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')

load_dotenv()


OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

@app.route('/api/ai-password', methods=['POST'])
def ai_password():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'error': 'Missing or invalid JSON body'}), 400
    length = int(data.get('length', 12))
    has_upper = bool(data.get('uppercase', True))
    has_lower = bool(data.get('lowercase', True))
    has_number = bool(data.get('numbers', True))
    has_symbol = bool(data.get('symbols', True))

    prompt = f"Generate a password of length {length}. "
    allowed = []
    forbidden = []
    if has_upper:
        allowed.append('uppercase letters')
    else:
        forbidden.append('uppercase letters')
    if has_lower:
        allowed.append('lowercase letters')
    else:
        forbidden.append('lowercase letters')
    if has_number:
        allowed.append('numbers')
    else:
        forbidden.append('numbers')
    if has_symbol:
        allowed.append('symbols')
    else:
        forbidden.append('symbols')
    if allowed:
        prompt += f"Only use {', '.join(allowed)}. "
    if forbidden:
        prompt += f"Do not use {', '.join(forbidden)}. "
    prompt += "Only output the password, nothing else."

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'HTTP-Referer': 'http://127.0.0.1:5500', 
        'X-Title': 'PassGen',
    }
    payload = {
        'model': 'openai/gpt-4o',
        'messages': [{ 'role': 'user', 'content': prompt }],
        'max_tokens': 20,
        'temperature': 0.9
    }
    response = None
    try:
        response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        password = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        if password:
            return jsonify({'password': password})
        else:
            return jsonify({'password': None, 'raw_output': result}), 200
    except Exception as e:
        error_detail = str(e)
        if response is not None:
            try:
                error_detail = response.json().get('error', {}).get('message', str(e))
            except Exception:
                pass
        return jsonify({'error': 'Error generating password', 'detail': error_detail}), 500

if __name__ == '__main__':
    app.run(debug=True)
