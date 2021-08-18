import re
import asyncio
import typing


class Button:  # Handler class
    """Create client buttons.

    This code is heavily inspired by discord.py's Command

    Attributes
    -----------
    name:
        The button id with regex included
    callback:
        Coroutine implementing the command
    """

    def __init__(self, func, match, **kwargs) -> None:
        """Initialize the command."""
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        self.callback = func
        self.master: typing.Any = None

        self.match = re.compile(match)

    async def __call__(self, *args, **kwargs) -> None:
        """Call the internal callback."""
        if self.master is None:
            raise TypeError("Self.master is not defined.")
        return await self.callback(self.master, *args, **kwargs)


def button(match, **attrs) -> typing.Any:  # Decorator to create a handler
    """Transform a function into a Command."""
    def decorator(func) -> Button:  # function -> command
        if isinstance(func, Button):
            raise TypeError("Callback is already a command.")
        return Button(func, match, **attrs)

    return decorator
