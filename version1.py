import os
import logging
from dotenv import load_dotenv
from mem0 import MemoryClient
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero, deepgram

# =====================================================
# ENVIRONMENT
# =====================================================
load_dotenv()

# =====================================================
# LOGGING
# =====================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("livekit-mem0")

# =====================================================
# MEM0 CLIENT
# =====================================================
MEMORY_USER_ID = "b3"

mem0_client = MemoryClient(
    api_key=os.getenv("MEM0_API_KEY"),
    org_id=os.getenv("MEM0_ORG_ID"),
    project_id=os.getenv("MEM0_PROJECT_ID"),
)

# =====================================================
# MEM0 CUSTOM INSTRUCTIONS (PROJECT LEVEL)
# =====================================================
CUSTOM_INSTRUCTIONS = """
Store useful, non-sensitive user information for personalized assistance.

Include: user name, professional role, technical interests, tools and frameworks, 
communication preferences, project context, learning goals, email addresses, physical addresses.

Exclude: phone numbers, passwords, API keys, access tokens, credit card numbers, 
bank details, Aadhaar numbers, PAN numbers, passport numbers, government IDs, OTPs.

Extract facts only when clearly stated. Ignore casual or temporary information.
"""

mem0_client.project.update(custom_instructions=CUSTOM_INSTRUCTIONS)

# =====================================================
# AGENT INSTRUCTIONS (CONCISE)
# =====================================================
AGENT_INSTRUCTION = """
You are a friendly AI assistant with memory.

Ask ONE question at a time to learn about the user:
1. Name
2. Email
3. Physical Address
4. Role or focus
5. Technical interests
6. Tools used
7. Projects

Be natural. Don't mention memory or storage. Never ask for sensitive data.
"""

SESSION_INSTRUCTION = "Greet the user warmly. If new, ask their name."

# =====================================================
# MEMORY FUNCTION
# =====================================================
def add_memory(user_text: str):
    mem0_client.add(
        messages=[{"role": "user", "content": user_text}],
        user_id=MEMORY_USER_ID,
        version="v2",
        includes="""
            user name,
            professional role,
            technical interests,
            tools and frameworks,
            communication preferences,
            project context,
            learning goals,
            email addresses,
            physical addresses
        """,
        excludes="""
            phone numbers,
            passwords,
            API keys,
            access tokens,
            credit card numbers,
            bank details,
            Aadhaar numbers,
            PAN numbers,
            passport numbers,
            government IDs,
            OTPs
        """,
        infer=True
    )

def search_memory(query: str):
    result = mem0_client.search(
        query=query,
        version="v2",
        filters={"user_id": MEMORY_USER_ID},
        top_k=3
    )
    return result.get("results", [])

# =====================================================
# MEMORY-ENABLED AGENT
# =====================================================
class MemoryEnabledAgent(Agent):
    def __init__(self):
        super().__init__(instructions=AGENT_INSTRUCTION)

    async def on_user_turn_completed(self, turn_ctx, new_message):
        user_text = (new_message.text_content or "").strip()
        if not user_text:
            return

        logger.info(f"User: {user_text}")

        # Store memory with filters
        add_memory(user_text)

        # Ground with relevant memories
        memories = search_memory(user_text)
        if memories:
            context = "\n".join(f"- {m['memory']}" for m in memories if m.get("memory"))
            turn_ctx.add_message(
                role="system",
                content=f"Known context:\n{context}"
            )

        await super().on_user_turn_completed(turn_ctx, new_message)

# =====================================================
# LIVEKIT ENTRYPOINT
# =====================================================
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        vad=silero.VAD.load(),
        stt="assemblyai/universal-streaming:en",
        llm=openai.LLM(model="gpt-4.1-mini"),
        tts=deepgram.TTS(model="aura-asteria-en"),
    )

    agent = MemoryEnabledAgent()
    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions=SESSION_INSTRUCTION)

# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
