import typing

import httpx
import loguru


async def make_request(  # pylint: disable=too-many-arguments,too-many-statements  # noqa: E501,C901
    url: str,
    logger: 'loguru.Logger',
    method: str = 'GET',
    data: typing.Any | None = None,
    custom_headers: dict[str, str] | None = None,
    timeout: int | None = None,
    retry_count: int = 1,
    content_type: str | None = 'application/json',
    files: dict[str, typing.Any] | None = None,
) -> httpx.Response:
    custom_headers = custom_headers or {}
    while retry_count > 0:
        async with httpx.AsyncClient() as client:
            log_data = str(data)
            if len(log_data) > 128:
                log_data = log_data[:128] + '... (truncated)'
            logger.info(
                'Making request: {} {} (timeout: {})',
                method,
                url,
                timeout,
                body=log_data,
            )  # TODO: hide data (token, password)

            client.headers.update({**custom_headers})
            if content_type is not None:
                client.headers.update({'Content-Type': content_type})

            if method == 'GET':
                try:
                    response = await client.get(
                        url,
                        timeout=timeout,
                    )
                except (httpx.ReadTimeout, httpx.ReadError):
                    logger.warning('Request timed out')
                    retry_count -= 1
                    continue
            elif method == 'POST':
                try:
                    response = await client.post(
                        url,
                        data=data if content_type != 'application/json' else None,
                        json=data if content_type == 'application/json' else None,
                        timeout=timeout,
                        files=files,
                    )
                except (httpx.ReadTimeout, httpx.ReadError):
                    logger.warning('Request timed out')
                    retry_count -= 1
                    continue
            else:
                raise ValueError('Invalid method')
            break
    if retry_count == 0:
        raise httpx.ReadTimeout('Request timed out')
    response_data = '*failed to parse response data*'
    try:
        response_data = response.json()
    except Exception:  # pylint: disable=broad-except
        try:
            response_data = response.text
        except Exception:  # pylint: disable=broad-except
            pass
    if len(str(response_data)) > 128:
        response_data = str(response_data)[:128] + '... (truncated)'
    logger.info(
        'Got response [{}]: {} {}.',
        response.status_code,
        method,
        url,
        body=response_data,
    )
    return response
