import dataclasses
import typing
import uuid


@dataclasses.dataclass
class MessageInfo:
    gpt_json: dict[str, typing.Any] | None
    message_text: str
    user_id: uuid.UUID | str
    user_tz: float


@dataclasses.dataclass
class MessageInfoRequired(MessageInfo):
    gpt_json: dict[str, typing.Any]
