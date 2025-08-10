import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS # Required for cross-origin requests from frontend

# Securely get your API key
# It's highly recommended to use environment variables for API keys in production
GEMINI_API_KEY = "AIzaSyBjatV-0puUSHYY-PYbUVyj3GuYJYV918g" # Replace with your actual Gemini API key

# Initialize Flask app
app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing frontend to access it

# Reverse each word (same as before)
def invert_words(sentence):
    """
    Reverses each word in a given sentence.
    Example: "hello world" becomes "olleh dlrow"
    """
    return ' '.join(word[::-1] for word in sentence.split())

# Get response from Gemini API (same as before)
def generate_reply(user_input):
    """
    Generates a reply using the Gemini API based on user input.
    """
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_input}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()

        if result and 'candidates' in result and len(result['candidates']) > 0 and \
           'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and \
           len(result['candidates'][0]['content']['parts']) > 0 and \
           'text' in result['candidates'][0]['content']['parts'][0]:
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print("Backend Error: Unexpected response structure from Gemini API.")
            return "I couldn't generate a reply. Unexpected response structure."

    except requests.exceptions.RequestException as e:
        print(f"Backend Error: API request failed: {e}")
        return f"API request error: {e}"
    except json.JSONDecodeError as e:
        print(f"Backend Error: JSON decoding failed: {e}")
        return f"JSON decoding error: {e}"
    except Exception as e:
        print(f"Backend Error: An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"

# Flask route for chat interaction
@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat requests from the frontend.
    Receives user input, generates a reply, and returns both original and inverted replies.
    """
    data = request.get_json()
    user_input = data.get('user_input', '')

    if not user_input:
        return jsonify({"error": "No user input provided"}), 400

    original_reply = generate_reply(user_input)
    inverted_reply = invert_words(original_reply)

    return jsonify({
        "original_reply": original_reply,
        "inverted_reply": inverted_reply
    })

# Main entry point to run the Flask app
if __name__ == '__main__':
    # Run the Flask app on localhost:5000
    # In a production environment, you would use a more robust WSGI server like Gunicorn
    app.run(debug=True) # debug=True allows for auto-reloading and better error messages
