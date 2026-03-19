import os
import base64
import json
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# Load environment variables from the .env file
load_dotenv()

class VisionaryAgent:
    def __init__(self):
        # 1. Securely load API keys
        groq_key = os.environ.get("GROQ_API_KEY")
        tavily_key = os.environ.get("TAVILY_API_KEY")

        # Basic error handling to alert you if keys are missing
        if not groq_key:
            raise ValueError("GROQ_API_KEY is missing. Please check your .env file.")
        if not tavily_key:
            raise ValueError("TAVILY_API_KEY is missing. Please check your .env file.")

        # 2. Initialize clients
        self.groq_client = Groq(api_key=groq_key)
        self.tavily_client = TavilyClient(api_key=tavily_key)
        
        # 3. Define the Groq models
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.reasoning_model = "openai/gpt-oss-120b"

    def _encode_image(self, image_path: str) -> str:
        """Converts an image to a base64 encoded string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _vision_extraction_pass(self, base64_image: str) -> str:
        """Phase 2: Interrogates the image for text, claims, and visual anomalies."""
        print("[*] Running Vision Interrogation Phase...")
        response = self.groq_client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a forensic image analyst. Extract any visible text, identify the core claim being made in the image, and note any visual anomalies (warped text, lighting errors, obvious AI generation markers). Be concise."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image and extract the claims and forensic details."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0.1
        )
        return response.choices[0].message.content

    def _tavily_research_pass(self, query: str) -> list:
        """Phase 3: Fetches real-world context using Tavily News API."""
        print(f"[*] Executing Tavily Search for: '{query}'")
        try:
            # We use 'advanced' depth and focus on news/general verification
            search_result = self.tavily_client.search(
                query=query, 
                search_depth="advanced", 
                max_results=5
            )
            return search_result.get("results", [])
        except Exception as e:
            print(f"[!] Tavily search failed: {e}")
            return []

    def _synthesis_and_verdict(self, original_claim: str, vision_data: str, search_results: list) -> Dict[str, Any]:
        """Phase 4: Cross-references data and outputs a structured JSON verdict."""
        print("[*] Synthesizing Evidence and Generating Verdict...")
        
        context = f"""
        Original User Claim: {original_claim}
        Vision Model Extraction (if any): {vision_data}
        Web Search Results: {json.dumps(search_results)}
        """

        sys_prompt = """
        You are 'The Visionary', an elite fact-checking AI. 
        Analyze the provided context (user claim, image forensics, and web search results).
        Cross-reference the claims against the web evidence. 
        
        You MUST respond ONLY with a valid JSON object matching this schema:
        {
            "truth_rating": <int 0-100, where 100 is unequivocally true>,
            "verdict": "<True | False | Misleading | Unverified>",
            "explanation": "<A concise 2-3 sentence explanation of your findings>",
            "visual_anomalies_detected": <boolean>,
            "key_sources": ["<url1>", "<url2>"]
        }
        """

        response = self.groq_client.chat.completions.create(
            model=self.reasoning_model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": context}
            ],
            response_format={"type": "json_object"},
            temperature=0.0 # Deterministic output for strict JSON formatting
        )
        
        return json.loads(response.choices[0].message.content)

    def analyze(self, text_claim: Optional[str] = None, image_path: Optional[str] = None) -> Dict[str, Any]:
        """Phase 1: The Input Router orchestrating the pipeline."""
        if not text_claim and not image_path:
            return {"error": "Must provide either a text claim or an image path."}

        vision_extraction = "No image provided."
        search_query = text_claim or ""

        # Branch 1: Image provided (Hybrid or Image-Only)
        if image_path:
            base64_img = self._encode_image(image_path)
            vision_extraction = self._vision_extraction_pass(base64_img)
            
            # If no text claim was given, use the vision extraction to build the search query
            if not text_claim:
                search_query = f"Fact check this claim: {vision_extraction}"
            else:
                search_query = f"{text_claim} {vision_extraction}"

        # Branch 2: Execution (Search + Synthesis)
        search_results = self._tavily_research_pass(search_query)
        verdict = self._synthesis_and_verdict(str(text_claim), vision_extraction, search_results)
        
        return verdict

# ==========================================
# Example Usage (Only runs if you execute agent.py directly)
# ==========================================
if __name__ == "__main__":
    try:
        agent = VisionaryAgent()
        
        print("--- Testing Text Only ---")
        text_result = agent.analyze(text_claim="The moon landing was faked in a Hollywood studio.")
        print(json.dumps(text_result, indent=2))
        
    except Exception as e:
        print(f"Initialization Error: {e}")