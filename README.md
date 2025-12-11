# 🌍 Tourli - AI Travel Companion for Morocco

An intelligent chatbot system that answers travel-related questions about Morocco, integrated with a modern web interface and Flask API backend.

**Version:** 1.0.0  
**Author:** Amine Akh  
**License:** MIT

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [How It Works](#how-it-works)
8. [Technologies](#technologies)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [Future Improvements](#future-improvements)

---

## 🎯 Project Overview

**Tourli** is a sophisticated AI travel companion designed to help users explore and plan trips to Morocco. It combines:

- **Intelligent Chatbot** - Uses TF-IDF vectorization and intent detection to understand and answer travel queries
- **Web Interface** - Modern, responsive landing page and interactive chat interface
- **REST API** - Flask backend that handles chatbot logic and integrates with external services
- **Data Processing** - Comprehensive Q&A dataset with edge cases and global city information

The system can answer questions about:
- Popular destinations and attractions
- Beaches, hiking, and outdoor activities
- Restaurants, food, and local cuisine
- Hotels, accommodations, and transportation
- Weather, distance calculations, and travel tips
- Safety, culture, and history

---

## ✨ Features

### Chatbot Capabilities
- **Intent Detection** - Automatically recognizes user intent from 40+ intent categories
- **Fuzzy City Matching** - Detects Moroccan and global cities even with typos
- **Weather Integration** - Fetches real-time weather data via OpenWeatherMap API
- **Confidence Scoring** - Returns confidence levels for answers
- **Edge Case Handling** - Handles personal questions, jokes, and off-topic queries
- **Normalization & Lemmatization** - Processes text with NLTK for accurate matching

### Web Interface
- **Dark Modern Design** - Futuristic UI with gradient backgrounds and neon accents
- **Fully Responsive** - Optimized for mobile, tablet, and desktop
- **Chat History** - Stores conversations in browser localStorage
- **Multiple Chat Sessions** - Create and manage multiple conversations
- **Real-time Messaging** - Instant communication with the chatbot
- **Smooth Animations** - Hover effects, scroll animations, and transitions

### API Backend
- **RESTful Architecture** - Clean, well-documented endpoints
- **CORS Enabled** - Allows requests from different origins
- **Health Check** - Status endpoint for monitoring
- **Error Handling** - Comprehensive error messages and status codes
- **Scalability Ready** - Built with Flask for easy expansion

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Web Browser)                    │
│  (HTML + CSS + JavaScript - Landing & Chat Pages)           │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Flask API Server (Port 5000)                    │
│           (chatbot_api.py - REST Endpoints)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        ┌────────┐  ┌────────────┐  ┌──────────┐
        │Retriever│  │Intent      │  │City      │
        │(TF-IDF) │  │Detection   │  │Detector  │
        └────────┘  └────────────┘  └──────────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
    ┌─────────────┐ ┌──────────────┐ ┌────────────┐
    │Q&A Dataset  │ │Weather API   │ │World Cities│
    │(JSON files) │ │OpenWeatherMap│ │(CSV)       │
    └─────────────┘ └──────────────┘ └────────────┘
```

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "TOURLI CHATBOT"
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
```
Flask==2.3.0
Flask-CORS==4.0.0
scikit-learn==1.3.0
requests==2.31.0
nltk==3.8.1
numpy==1.24.0
```

### 3. Install Node Dependencies (Optional, for Website)
```bash
cd tourli-website
npm install
```

### 4. Download NLTK Data
The system automatically downloads required NLTK data on first run:
- `wordnet` - For lemmatization
- `omw-1.4` - Open Multilingual Wordnet

---

## 🚀 Usage

### Method 1: Web Interface (Recommended)

**Terminal 1 - Start API:**
```bash
python chatbot_api.py
```
Expected output:
```
[Retriever] Loading datasets...
[Retriever] Total Q&A entries loaded: 5000+
✓ Retriever initialized successfully
 * Running on http://localhost:5000
```

**Terminal 2 - Start Website:**
```bash
cd tourli-website
npm run dev
# or
npx http-server -p 8000
```

**Browser:** Open http://localhost:8000

**Chat:** Click "Chat" in navigation and start messaging!

---

### Method 2: Command-Line Interface

```bash
python src/chatbot/cli_chatbot.py
```

Example:
```
=== Morocco Tourism Chatbot ===
Type your questions about Morocco, or 'quit' to exit.

You: What are the best beaches in Morocco?
Chatbot: [Answer from knowledge base]

You: quit
Chatbot: Goodbye! Enjoy your trip to Morocco!
```

---

### Method 3: Direct API Calls

**Using cURL:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you tell me about Marrakech?"}'
```

**Using Python:**
```python
import requests
import json

url = "http://localhost:5000/api/chat"
payload = {"message": "Best time to visit Morocco?"}
response = requests.post(url, json=payload)
print(response.json())
```

**Using JavaScript:**
```javascript
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Tell me about Fes' })
})
.then(r => r.json())
.then(data => console.log(data.response));
```

---

## 📁 Project Structure

```
TOURLI CHATBOT/
│
├── 📄 chatbot_api.py                    # Flask API server (main entry point)
├── 📄 README.md                         # This file
├── 📄 QUICKSTART.md                     # Quick start guide
├── 📄 requirements.txt                  # Python dependencies
├── 📄 .gitignore                        # Git ignore rules
│
├── 📁 src/                              # Source code
│   ├── 📁 chatbot/
│   │   ├── apik.py                      # Chatbot API configuration
│   │   └── cli_chatbot.py               # Command-line chatbot interface
│   │
│   ├── 📁 preprocessing/
│   │   ├── data_loader.py               # Load & manage datasets
│   │   └── __pycache__/                 # Python cache
│   │
│   └── 📁 retrieval/
│       ├── retriever.py                 # Main chatbot logic
│       ├── city_detector.py             # Moroccan & world city detection
│       ├── world_city_formatter.py      # Format city response messages
│       └── __pycache__/
│
├── 📁 data/                             # Datasets
│   ├── 📁 raw/                          # Original, unprocessed data
│   │   ├── dataset1.json                # Main Q&A dataset (~4000 entries)
│   │   ├── edge_cases.json              # Special cases & personal intro
│   │   └── worldcities.csv              # Global cities database
│   │
│   └── 📁 processed/                    # Cleaned, ready-to-use data
│       ├── cleaned_dataset.json         # Processed main dataset
│       ├── edge_cases_cleaned.json      # Processed edge cases
│       ├── worldcities.json             # JSON version of cities
│       ├── worldcities_clean.csv        # Cleaned cities CSV
│       └── [other processed files]
│
└── 📁 tourli-website/                   # Frontend web application
    ├── 📄 index.html                    # Landing page (main entry point)
    ├── 📄 chat.html                     # Chat interface page
    ├── 📄 test-api.html                 # API testing page
    ├── 📄 package.json                  # Node.js configuration
    ├── 📄 README.md                     # Website-specific documentation
    │
    ├── 📁 css/
    │   ├── styles.css                   # Landing page styles
    │   └── chat-styles.css              # Chat page styles
    │
    ├── 📁 js/
    │   ├── main.js                      # Landing page interactivity
    │   ├── chat.js                      # Chat interface logic
    │   └── advanced-features.js         # Advanced UI features
    │
    └── 📁 assets/                       # Images, icons, media (expandable)
```

---

## 🧠 How It Works

### 1. Text Processing Pipeline

```
User Input
    ↓
[Normalization] → lowercase, remove accents, special chars
    ↓
[Lemmatization] → convert words to root form (run→run, running→run)
    ↓
[Tokenization] → split into individual words
    ↓
Ready for Analysis
```

### 2. Intent Detection

The system recognizes 40+ intent categories:
- `greeting` - "Hello", "Hi", "Salam"
- `farewell` - "Bye", "Goodbye"
- `ask_beaches` - "Best beaches", "Where to swim"
- `ask_weather` - "What's the weather", "Is it hot"
- `ask_restaurants` - "Where to eat", "Best food places"
- `ask_hotels` - "Accommodation", "Where to stay"
- `ask_hiking` - "Trails", "Mountain walks"
- `joke_or_troll` - Jokes, funny requests
- And 30+ more...

**Detection Method:**
```python
def detect_intent(user_input):
    normalized = normalize_text(user_input)
    for intent, keywords in intent_keywords.items():
        if any(keyword in normalized for keyword in keywords):
            return intent
    return "general_query"
```

### 3. Answer Retrieval (TF-IDF)

1. **TF-IDF Vectorization**
   - Converts questions and user input to numeric vectors
   - Measures importance of words in context

2. **Cosine Similarity**
   - Compares user question with all Q&A entries
   - Returns top matches with similarity scores

3. **Confidence Threshold**
   - Default threshold: 0.2 (20% similarity)
   - If confidence < threshold → "I don't know" response

```python
responses = retriever.get_answer("What beaches in Agadir?")
best_answer, confidence_score = responses[0]
# Example: ("Agadir Beach is known for...", 0.85)
```

### 4. City Detection

```
User: "What's the weather in Marrakech?"
    ↓
[City Detector]
    - Checks if "marrakech" matches Moroccan cities
    - Handles typos: "marrakch" → "marrakech"
    - Detects global cities if not Moroccan
    ↓
Detected City: "marrakech"
    ↓
[Weather API Call]
    - Fetches live weather from OpenWeatherMap
    - Returns: temp, humidity, condition, wind
    ↓
Response with Weather Data
```

### 5. Response Generation

```
Intent: ask_weather
City: marrakech
Weather: {"temp": 28, "condition": "sunny", "humidity": 45}
    ↓
[Template Matching]
    Q&A entry: "What's the weather in Morocco?"
    Answer: "[City] is typically [weather]..."
    ↓
[Personalization]
    Insert city name & live weather data
    ↓
Final Response: "In Marrakech it's 28°C and sunny with 45% humidity."
```

---

## 🛠️ Technologies

### Backend
- **Python 3.8+** - Programming language
- **Flask 2.3** - Web framework
- **Flask-CORS** - Cross-origin requests
- **scikit-learn** - Machine learning (TF-IDF, similarity)
- **NLTK** - Natural language processing
- **NumPy** - Numerical computations
- **requests** - HTTP library for APIs
- **JSON** - Data format for Q&A storage

### Frontend
- **HTML5** - Semantic structure
- **CSS3** - Modern styling with gradients, animations
- **JavaScript (ES6+)** - Client-side logic
- **localStorage API** - Chat history persistence
- **Fetch API** - HTTP requests to backend

### External APIs
- **OpenWeatherMap API** - Real-time weather data
- **HTTP Server** - Simple server for development

### Development Tools
- **npm** - Package manager
- **Node.js** - JavaScript runtime
- **Git** - Version control

---

## ⚙️ Configuration

### API Configuration

**File:** `chatbot_api.py`

```python
# Port (default: 5000)
if __name__ == '__main__':
    app.run(debug=True, port=5000)

# CORS allowed origins
CORS(app)  # Allows all origins
```

### Chatbot Parameters

**File:** `src/retrieval/retriever.py`

```python
# Confidence threshold (0-1)
CONFIDENCE_THRESHOLD = 0.2

# City matching threshold (0-1)
CITY_MATCH_THRESHOLD = 0.80

# Weather API key
_OWM_API_KEY = os.getenv("TOURLI_API_KEY")
```

### Data Paths

**File:** `src/preprocessing/data_loader.py`

```python
DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data/processed')

DATA_FILES = [
    'cleaned_dataset.json',
    'edge_cases_cleaned.json',
    'worldcities.json'
]
```

### Website Configuration

**File:** `tourli-website/js/chat.js`

```javascript
// API endpoint
this.apiUrl = 'http://localhost:5000/api/chat';

// Chat storage
const STORAGE_KEY = 'chatbot_all_chats';
```

---

## 🔍 API Reference

### POST /api/chat

Send a message to the chatbot and get a response.

**Request:**
```json
{
  "message": "What's the best time to visit Morocco?"
}
```

**Response (Success - 200):**
```json
{
  "response": "The best time to visit Morocco is spring (April-May) and fall (September-October)...",
  "success": true
}
```

**Response (Empty Message - 400):**
```json
{
  "error": "Message cannot be empty",
  "response": "Please ask me something about Morocco travel!",
  "status": 400
}
```

**Response (Server Error - 500):**
```json
{
  "error": "Chatbot not initialized",
  "response": "Sorry, the chatbot is having trouble starting up. Please try again.",
  "status": 500
}
```

### GET /api/health

Check if the API server is running.

**Response:**
```json
{
  "status": "online",
  "message": "Tourli Chat API is running"
}
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" on port 5000

**Solution:**
```bash
# Check if port is in use
netstat -ano | findstr :5000

# Kill the process using the port (Windows)
taskkill /PID <PID> /F

# Run API on different port
python chatbot_api.py --port 5001
```

### Issue: "No module named 'sklearn'"

**Solution:**
```bash
pip install scikit-learn
# or
pip install -r requirements.txt
```

### Issue: "NLTK data not found"

**Solution:**
```python
python -m nltk.downloader wordnet omw-1.4
```

### Issue: Datasets not loading

**Solution:**
1. Check file paths in `src/preprocessing/data_loader.py`
2. Verify files exist in `data/processed/`
3. Ensure JSON files are valid:
   ```bash
   python -m json.tool data/processed/cleaned_dataset.json
   ```

### Issue: Weather API not working

**Solution:**
```bash
# Check API key validity
curl "https://api.openweathermap.org/data/2.5/weather?q=marrakech&appid=YOUR_KEY"

# Get a new API key from https://openweathermap.org/api
```

### Issue: Website shows "API not available"

**Solution:**
1. Ensure Flask server is running on localhost:5000
2. Check browser console (F12) for CORS errors
3. Clear browser cache and reload

---

## 📈 Performance Metrics

- **Chatbot Response Time:** < 500ms (avg)
- **Q&A Dataset Size:** 5000+ entries
- **Supported Intent Categories:** 40+
- **City Coverage:** 150,000+ global cities + 30+ Moroccan cities
- **Website Load Time:** < 2s
- **Browser Compatibility:** Chrome, Firefox, Safari, Edge (modern versions)

---

## 🔮 Future Improvements

### Short Term
- [ ] Add user authentication & profiles
- [ ] Multi-language support (French, Arabic)
- [ ] Sentiment analysis for user satisfaction
- [ ] Recommendation engine for personalized suggestions
- [ ] Database integration (PostgreSQL/MongoDB)

### Medium Term
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced NLP (spaCy, transformers)
- [ ] Booking integration (hotels, flights)
- [ ] Image recognition for landmarks
- [ ] Voice input/output

### Long Term
- [ ] Machine learning model training pipeline
- [ ] Real-time collaborative travel planning
- [ ] AR/VR exploration features
- [ ] Multi-destination trip planning
- [ ] Community reviews & ratings integration

---

## 📝 Dataset Information

### cleaned_dataset.json
- **Entries:** ~10,000+
- **Categories:** All major tourism categories
- **Content:** Q&A pairs about Morocco attractions, activities, food, hotels, etc.

### edge_cases_cleaned.json
- **Entries:** ~900+
- **Categories:** Personal greetings, jokes, off-topic questions
- **Content:** "About yourself", jokes, special cases

### worldcities.json / worldcities_clean.csv
- **Entries:** 150,000+
- **Data:** City name, country, latitude, longitude, population
- **Use:** City detection and geolocation

---

## 📜 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Author

**Amine Akh** - Creator of Tourli, an AI travel companion for exploring Morocco.

---

## 📞 Support & Contributing

For issues, questions, or contributions:
1. Check existing documentation
2. Review code comments
3. Check browser console (F12) for JavaScript errors
4. Review Python error logs in terminal

---

## 🌟 Acknowledgments

- OpenWeatherMap API for weather data
- scikit-learn for machine learning tools
- NLTK for natural language processing
- Flask for web framework
- All contributors and testers

---

**Happy travels with Tourli! 🌍✈️🏖️**

*Last Updated: December 9, 2025*
