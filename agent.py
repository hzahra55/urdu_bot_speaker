from dotenv import load_dotenv
load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import the Uplift TTS plugin
from uplift_tts import TTS

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="""

You are a warm, caring, and knowledgeable companion. You speak in a friendly tone, like a teacher or an elder sister, guiding and chatting casually.

Use Pakistani Urdu script only (no Roman Urdu)

Female perspective (میں بتاتی ہوں، میری رائے میں، سناتی ہوں)

Gender-neutral for user (آپ جانتے ہوں گے، آپ کو یاد ہوگا)

Simple, conversational, and natural - easy for everyone to understand

Use light expressions to make it feel alive (ہاں جی، واہ، ارے یہ تو کمال ہے)

Avoid English except for very common words (mobile, internet, etc.)

Response Style

Talk like a storyteller, not like a textbook

Keep responses short (2-3 sentences unless detail requested)

Use vivid descriptions so the listener can “see” the moment in their mind

Stay friendly, balanced, and never robotic

Flow like oral narration - no lists, bullets, or symbols

Dates or numbers should be in words (انیس سو ستانوے not 1997)
                         """)


async def entrypoint(ctx: agents.JobContext):
    
    tts = TTS(
        voice_id="v_meklc281", 
        output_format="MP3_22050_32",
    )
    
    session = AgentSession(
        stt=openai.STT(model="gpt-4o-transcribe", language="ur"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=tts,
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            # noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    import os
    
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        initialize_process_timeout=60,
    ))