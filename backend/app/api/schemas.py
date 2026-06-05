from pydantic import BaseModel


class StoryEntry(BaseModel):
    id: str
    type: str
    character: str | None = None
    text: str


class MessageEntry(BaseModel):
    id: str = ""
    sender: str = ""
    recipient: str = ""
    content: str = ""
    status: str = "unread"
    day: int = 1
    time: str = "00:00"


class GameStartResponse(BaseModel):
    scenario: str
    player_character: str
    entries: list[StoryEntry]
    messages: list[MessageEntry]
    contacts: list[str] = []
    current_date: str = ""
    current_time: str = ""


class ActionRequest(BaseModel):
    text: str


class ActionResponse(BaseModel):
    entries: list[StoryEntry]
    new_messages: list[MessageEntry]


class SmsRequest(BaseModel):
    to: str
    text: str


class SmsResponse(BaseModel):
    sent: bool
    player_message: MessageEntry | None = None
    npc_replies: list[MessageEntry]
