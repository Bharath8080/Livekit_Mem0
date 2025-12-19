import os
import logging
from dotenv import load_dotenv
from mem0 import MemoryClient
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero, deepgram

load_dotenv()
logging.basicConfig(level=logging.INFO)

MEMORY_USER_ID = "b15"

mem0 = MemoryClient(
    api_key=os.getenv("MEM0_API_KEY"),
    org_id=os.getenv("MEM0_ORG_ID"),
    project_id=os.getenv("MEM0_PROJECT_ID"),
)

mem0.project.update(custom_instructions="""
Store useful, non-sensitive user information for personalized assistance.

Include: user name, professional role, technical interests, tools and frameworks, 
communication preferences, project context, learning goals, email addresses, physical addresses.

Exclude: phone numbers, passwords, API keys, access tokens, credit card numbers, 
bank details, Aadhaar numbers, PAN numbers, passport numbers, government IDs, OTPs.

Extract facts only when clearly stated. Ignore casual or temporary information.
""")

AGENT_INSTRUCTION = """
You are a friendly AI assistant with long-term memory capabilities.

IMPORTANT: You remember information about users across conversations. Use what you already know naturally in your responses.

Your goal is to learn about the user to provide personalized assistance in future conversations.
Ask ONE question at a time to gradually learn:
- Their name
- Their email address
- Their physical location/address
- Their professional role or area of focus
- Their technical interests
- Tools and frameworks they use
- Projects they're working on

Keep it conversational and natural. Wait for their answer before moving to the next topic.
If they share something, acknowledge it warmly before asking the next question.

If you already know something about the user, USE THAT INFORMATION and don't ask for it again.

NEVER ask for: phone numbers, passwords, API keys, tokens, credit card info, 
bank details, Aadhaar, PAN, passport numbers, government IDs, or OTPs.
"""

SESSION_INSTRUCTION = """
Greet the user warmly by their name if you know it, otherwise ask for their name in a friendly way.
"""

class MemoryAgent(Agent):
    def __init__(self, user_memories=""):
        super().__init__(instructions=f"{AGENT_INSTRUCTION}\n\n{user_memories}")
        self.conversation = []

    async def on_user_turn_completed(self, turn_ctx, new_message):
        user_text = new_message.text_content.strip()
        self.conversation.append({"role": "user", "content": user_text})
        await super().on_user_turn_completed(turn_ctx, new_message)

    async def on_agent_speech_created(self, speech):
        self.conversation.append({"role": "assistant", "content": speech.text})
        await super().on_agent_speech_created(speech)

    async def on_session_closed(self, reason=None):
        mem0.add(
            messages=self.conversation,
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

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # Get ALL memories for this user FIRST
    memories = mem0.get_all(
        filters={"user_id": MEMORY_USER_ID},
        version="v2"
    )
    
    results = memories.get("results", [])
    
    if results:
        memory_context = "=== WHAT YOU KNOW ABOUT THIS USER ===\n" + "\n".join(f"- {m['memory']}" for m in results) + "\n=== USE THIS INFORMATION IN ALL RESPONSES ===\n"
        greeting_instruction = f"{SESSION_INSTRUCTION}\n\nREMEMBER: Greet them using what you know above!"
    else:
        memory_context = ""
        greeting_instruction = SESSION_INSTRUCTION

    session = AgentSession(
        vad=silero.VAD.load(),
        stt="assemblyai/universal-streaming:en",
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=deepgram.TTS(model="aura-asteria-en"),
    )

    agent = MemoryAgent(user_memories=memory_context)
    
    @session.on("close")
    def on_close(event):
        import asyncio
        asyncio.create_task(agent.on_session_closed())
    
    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions=greeting_instruction)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
