# 👁️ The Visionary

The Visionary is a hybrid, multimodal fact-checking agent. It uses Groq's high-speed LPU infrastructure and Tavily's search API to cross-reference images and text claims against real-world data instantly.

## 🚀 Quick Start Setup

### 1. Requirements
Ensure you have Python 3.9+ installed. You will need API keys for:
* **Groq:** [console.groq.com](https://console.groq.com/)
* **Tavily:** [tavily.com](https://tavily.com/)

### 2. Install Dependencies
Open your terminal and install the required Python libraries:
```bash
pip install fastapi uvicorn python-multipart groq tavily-python python-dotenv
```

3. Setup Environment Variables
Create a file named .env in the same directory as main.py and add your keys:

```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

4. Run the Application
Execute the single script from your terminal:

```
python main.py
```

Navigate to:
```
http://localhost:8000 in your web browser.
```

The beautiful split-screen UI.

🧠 Architecture
Frontend: Served via FastAPI HTMLResponse (Tailwind CSS, Lucide Icons, Vanilla JS).

Vision Pass: Uses ```meta-llama/llama-4-scout-17b-16e-instruct``` to extract OCR and hunt for visual artifacts in uploaded images.

Context Retrieval: Uses Tavily Search API to find live news sources.

Reasoning Pass: Uses ```llama-3.3-70b-versatile``` to ingest the vision data and web context, returning a structured JSON verdict and Trust Score.
