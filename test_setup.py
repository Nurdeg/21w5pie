# test_setup.py
import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        return

    print("✅ Environment loaded.")
    
    # 2. Configure Gemini
    genai.configure(api_key=api_key)
    
    print("⏳ Sending request to Gemini...")
    
    try:
        # 3. Initialize Model
        # "gemini-1.5-flash" is Google's fast, cost-effective model (great for this project)
        model = genai.GenerativeModel("gemini-3-flash-preview")
        
        # 4. Async Request
        response = await model.generate_content_async("Say 'System Operational' if you can hear me.")
        
        # 5. Extract Text
        print(f"🤖 Gemini Response: {response.text}")
        print("✅ System Operational! You are ready to build.")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())