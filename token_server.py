import os, time, secrets
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt  # pip install pyjwt

load_dotenv()

LIVEKIT_URL        = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY    = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
ALLOWED            = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
DEFAULT_ROOM       =  "demo-room"

if not (LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET):
    raise RuntimeError("Missing LIVEKIT_* env vars")

app = FastAPI(title="LiveKit Room & Token API")

# if ALLOWED:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=ALLOWED,
#         allow_credentials=True,
#         allow_methods=["POST","GET","OPTIONS"],
#         allow_headers=["Content-Type","Authorization"],
#     )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory current room (swap to Redis/DB in prod)
CURRENT_ROOM = None

class SetRoomRequest(BaseModel):
    room: str

class SessionRequest(BaseModel):
    room: Optional[str] = None
    identity: Optional[str] = None
    can_publish: bool = True
    can_subscribe: bool = True

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/room")
def get_room():
    global CURRENT_ROOM
    if not CURRENT_ROOM:
        CURRENT_ROOM = DEFAULT_ROOM
    return {"room": CURRENT_ROOM}

@app.post("/room")
def set_room(req: SetRoomRequest):
    """
    Admin endpoint: set the canonical room.
    Use this to match whatever room your agent joined (copy from agent logs).
    """
    global CURRENT_ROOM
    CURRENT_ROOM = req.room
    return {"room": CURRENT_ROOM}

@app.post("/session")
def create_session(req: SessionRequest = Body(default=SessionRequest())):
    """
    Returns { url, room, token, identity } for the *current* room.
    If req.room is provided, it overrides temporarily for this token only.
    """
    global CURRENT_ROOM
    room = req.room or CURRENT_ROOM or DEFAULT_ROOM
    identity = req.identity or f"user_{secrets.token_hex(4)}"

    now = int(time.time())
    exp = now + 60*60  # 1 hour

    payload = {
        "iss": LIVEKIT_API_KEY,
        "nbf": now - 10,
        "exp": exp,
        "sub": identity,
        "video": {
            "room": room,
            "roomJoin": True,
            "canPublish": req.can_publish,
            "canSubscribe": req.can_subscribe,
        },
    }

    try:
        token = jwt.encode(
            payload,
            LIVEKIT_API_SECRET,
            algorithm="HS256",
            headers={"kid": LIVEKIT_API_KEY},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token signing failed: {e}")

    return {"url": LIVEKIT_URL, "room": room, "token": token, "identity": identity, "expires_at": exp}
