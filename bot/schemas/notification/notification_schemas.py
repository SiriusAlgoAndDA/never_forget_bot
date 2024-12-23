import enum


class NotificationStatus(enum.StrEnum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
