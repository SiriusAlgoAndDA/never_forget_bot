from bot.handlers.cancel import router as cancel_router
from bot.handlers.change_timezone import router as timezone_router
from bot.handlers.error import router as error_router
from bot.handlers.message import router as message_router
from bot.handlers.notify_processing import router as notify_processing_router
from bot.handlers.start import router as start_router
from bot.handlers.upcoming_events import router as upcoming_events_router
from bot.handlers.upcoming_notifications import router as upcoming_notifications_router
from bot.handlers.voice import router as voice_router


list_of_routers = [
    start_router,
    cancel_router,
    error_router,
    message_router,
    voice_router,
    timezone_router,
    notify_processing_router,
    upcoming_events_router,
    upcoming_notifications_router,
]


__all__ = [
    'list_of_routers',
]
