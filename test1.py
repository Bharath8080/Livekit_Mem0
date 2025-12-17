from mem0 import MemoryClient
import os
from dotenv import load_dotenv
load_dotenv()

client = MemoryClient(
    api_key=os.getenv("MEM0_API_KEY"),
    org_id=os.getenv("MEM0_ORG_ID"),
    project_id=os.getenv("MEM0_PROJECT_ID"),
)

messages = [
    {"role": "user", "content": "My full name is Bharath Munakala."},
    {"role": "user", "content": "I work as a final-year AI/ML student and freelance developer."},
    {"role": "user", "content": "I primarily use Python, LangChain, LiveKit, Groq, Gemini, and Mem0."},
    {"role": "user", "content": "My email is bharath@example.com and phone number is +91-9876543210."},
    {"role": "user", "content": "My GitHub token is ghp_xxxxxxxxxxxxx."},
    {"role": "user", "content": "I prefer direct, technical answers with code examples."},
    {"role": "user", "content": "My Aadhaar number is 1234-5678-9012."},
]

result = client.add(
    messages=messages,
    user_id="bharath",
    version="v2",

    includes="""
    user name,
    professional role,
    education level,
    technical interests,
    tools and frameworks,
    communication preferences
    """,

    excludes="""
    email addresses,
    phone numbers,
    physical addresses,
    passwords,
    API keys,
    access tokens,
    OAuth tokens,
    GitHub tokens,
    banking details,
    credit card numbers,
    debit card numbers,
    Aadhaar numbers,
    PAN numbers,
    passport numbers,
    government-issued identifiers,
    biometric data
    """
)

print(result)
