from bot.handlers.cancel import router as cancel_router
from bot.handlers.error import router as error_router
from bot.handlers.start import router as start_router


list_of_routers = [
    start_router,
    cancel_router,
    error_router,
]


__all__ = [
    'list_of_routers',
]
