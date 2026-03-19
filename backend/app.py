import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from agent import VisionaryAgent

app = FastAPI(title="The Visionary API")

# --- ADD CORS MIDDLEWARE ---
# Crucial: This allows your statically hosted frontend (e.g., on Vercel) 
# to securely make requests to this API hosted elsewhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = VisionaryAgent()

# Get the directory where app.py is located to save temp files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Simple health check route
@app.get("/health")
async def health_check():
    return {"status": "online", "message": "The Visionary API is running. Send POST requests to /api/analyze"}

@app.post("/api/analyze")
async def analyze_claim(
    text_claim: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    image_path = None
    try:
        if image and image.filename:
            # Save temporary files safely inside the backend folder
            image_path = os.path.join(BASE_DIR, f"temp_{image.filename}")
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        
        verdict = agent.analyze(text_claim=text_claim, image_path=image_path)
        return verdict

    except Exception as e:
        print(f"Backend Error: {str(e)}")
        return {"error": str(e)}
    
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
