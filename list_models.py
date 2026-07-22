import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("Available models:")
print("=" * 50)

for model in genai.list_models():
    # Only show models that support generateContent
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
    else:
        print(f"❌ {model.name} (no generateContent support)")