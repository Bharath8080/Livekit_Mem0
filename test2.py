from mem0 import MemoryClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MemoryClient(
    api_key=os.getenv("MEM0_API_KEY"),
    org_id="org_xrFybOvllDmI2fz9Zr07Ze0XOg9ZdY2epKXyMsKC",
    project_id="proj_n40V9YXCWsaCtiAIRFk3MBNbFtEwIPR9IGKEzzO0",
)

messages = [
    # ---------- BASIC IDENTITY ----------
    {"role": "user", "content": "My full name is Bharath Munakala."},
    {"role": "user", "content": "You can call me Bharath."},

    # ---------- EDUCATION & ROLE ----------
    {"role": "user", "content": "I am a final-year AI/ML student at GIET."},
    {"role": "user", "content": "I also work as a freelance GenAI developer."},

    # ---------- TECHNICAL PROFILE ----------
    {"role": "user", "content": "I mainly work on Generative AI and AI voice agents."},
    {"role": "user", "content": "My tech stack includes Python, LangChain, LiveKit, Groq, Gemini, and Mem0."},
    {"role": "user", "content": "I prefer building production-ready systems rather than demos."},

    # ---------- PREFERENCES ----------
    {"role": "user", "content": "I like concise but technical explanations with examples."},
    {"role": "user", "content": "You can assume I understand advanced AI concepts."},

    # ---------- MIXED (INCLUDE + EXCLUDE) ----------
    {
        "role": "user",
        "content": (
            "I am Bharath Munakala, a freelance AI developer. "
            "My email is bharath@example.com."
        ),
    },

    # ---------- PURE EXCLUDE ----------
    {"role": "user", "content": "My phone number is +91-9876543210."},
    {"role": "user", "content": "My GitHub token is ghp_xxxxxxxxxxxxx."},
    {"role": "user", "content": "My Aadhaar number is 1234-5678-9012."},
    {"role": "user", "content": "My PAN number is ABCDE1234F."},
    {"role": "user", "content": "My credit card number is 4111 1111 1111 1111."},
]

result = client.add(
    messages=messages,
    user_id="bharath002",
    version="v2",

    includes="""
    user name,
    professional role,
    education level,
    technical interests,
    tools and frameworks,
    communication preferences,
    project preferences
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
