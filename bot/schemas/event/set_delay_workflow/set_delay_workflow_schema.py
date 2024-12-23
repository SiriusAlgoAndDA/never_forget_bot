import dataclasses
import uuid


@dataclasses.dataclass
class SetDelayInfo:
    event_id: uuid.UUID | str
    delta: int
    msg_id: int
    tg_id: int
