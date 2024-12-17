import traceback
import typing
import uuid

import aiogram.types
import loguru

from bot.bot_helper import send


class UniqueIDMiddleware(aiogram.BaseMiddleware):
    async def __call__(
        self,
        handler: typing.Callable[[aiogram.types.TelegramObject, dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: aiogram.types.TelegramObject,
        data: dict[str, typing.Any],
    ) -> typing.Any:
        log_extra = {'request_id': uuid.uuid4().hex}
        data['request_id'] = log_extra['request_id']

        try:
            with loguru.logger.contextualize(**log_extra):
                loguru.logger.info('Got new event {}', event, log_type='request')
                result = await handler(event, data)
        except Exception as exc:
            with loguru.logger.contextualize(**log_extra):
                loguru.logger.exception('Exception occurred')
                await send.send_traceback_message_safe(
                    logger=loguru.logger,
                    message=f"Exception occurred\nrequest_id={log_extra['request_id']}",
                    code=traceback.format_exc(),
                )
            raise exc
        finally:
            with loguru.logger.contextualize(**log_extra):
                loguru.logger.info('Got response', log_type='request')
        return result
