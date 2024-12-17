import typing as tp

from bot.database.connection import SessionManager


def main(*_: tp.Any) -> None:
    """Open sqlalchemy session."""

    with SessionManager().create_session() as session:  # noqa: F841  # pylint: disable=unused-variable
        breakpoint()  # pylint: disable=forgotten-debug-statement
