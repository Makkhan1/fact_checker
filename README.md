# 👁️ The Visionary

The Visionary is a hybrid, multimodal fact-checking agent built entirely into a **single Python file**. It uses Groq's high-speed LPU infrastructure and Tavily's search API to cross-reference images and text claims against real-world data instantly.

## 🚀 Quick Start Setup

### 1. Requirements
Ensure you have Python 3.9+ installed. You will need API keys for:
* **Groq:** [console.groq.com](https://console.groq.com/)
* **Tavily:** [tavily.com](https://tavily.com/)

### 2. Install Dependencies
Open your terminal and install the required Python libraries:
```bash
pip install fastapi uvicorn python-multipart groq tavily-python python-dotenv
