import enum


class EventStatus(enum.StrEnum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    DELETED = 'deleted'
    NOT_COMPLETED = 'not_completed'
