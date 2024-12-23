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
class NotifyDataWithAsIs:
    notify_id: uuid.UUID | str
    as_is: bool
