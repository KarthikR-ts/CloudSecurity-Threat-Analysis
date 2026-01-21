import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {bool(api_key)}")
print(f"Key prefix: {api_key[:15]}..." if api_key else "No key")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

try:
    response = model.generate_content('Say hello in one word')
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
