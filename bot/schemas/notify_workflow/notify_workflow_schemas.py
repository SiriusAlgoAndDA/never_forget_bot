import dataclasses
import uuid


@dataclasses.dataclass
class NotifyData:
    notify_id: uuid.UUID | str


@dataclasses.dataclass
class NotifyDataSent:
    notify_id: uuid.UUID | str
    sent_ts: str


@dataclasses.dataclass
class NotifyDataForCreated:
    notify_id: uuid.UUID | str
    as_is: bool
    message_id: int
