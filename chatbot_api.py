"""
Flask API for Tourli Chatbot
Connects the web interface to the actual chatbot backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add paths for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.retrieval.retriever import Retriever

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize retriever globally
retriever = None

def init_retriever():
    """Initialize the retriever on first request"""
    global retriever
    if retriever is None:
        try:
            retriever = Retriever()
            print("✓ Retriever initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing retriever: {e}")
            return False
    return True

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    Expects: {"message": "user question"}
    Returns: {"response": "bot answer"}
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty',
                'response': 'Please ask me something about Morocco travel!'
            }), 400
        
        # Initialize retriever if needed
        if not init_retriever():
            return jsonify({
                'error': 'Chatbot not initialized',
                'response': 'Sorry, the chatbot is having trouble starting up. Please try again.'
            }), 500
        
        # Get response from retriever - this is the actual chatbot logic
        try:
            responses = retriever.get_answer(user_message)
            
            if not responses or len(responses) == 0:
                return jsonify({
                    'response': 'I apologize, but I don\'t have information about that. Please ask me something about Morocco tourism.',
                    'success': True
                })
            
            best_answer, confidence_score = responses[0]
            
            # Check confidence threshold (same as cli_chatbot.py)
            confidence_threshold = 0.2
            if confidence_score < confidence_threshold:
                response_text = 'I apologize, that seems to be outside my knowledge base. I can only answer questions about Morocco tourism.'
            else:
                response_text = best_answer
            
            return jsonify({
                'response': response_text,
                'success': True
            })
        
        except Exception as e:
            print(f"Error getting answer: {e}")
            return jsonify({
                'response': f'Sorry, I encountered an error: {str(e)}',
                'success': False
            }), 500
    
    except Exception as e:
        print(f"Request error: {e}")
        return jsonify({
            'error': str(e),
            'response': 'An error occurred processing your request.'
        }), 400

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'message': 'Tourli Chat API is running'
    })

@app.route('/api/init', methods=['POST'])
def initialize():
    """Initialize the chatbot"""
    try:
        if init_retriever():
            return jsonify({
                'status': 'initialized',
                'message': 'Chatbot initialized successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize chatbot'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Tourli Chat API Server...")
    app.run(debug=True, port=5000, host='127.0.0.1')
