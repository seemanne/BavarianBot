from pydantic import BaseModel


class Status(BaseModel):
    is_ready: bool
    is_closed: bool

class Reaction(BaseModel):

    emoji_id: str
    count: int

class Message(BaseModel):

    author_id: int
    content: str
    reactions: list[Reaction]

