from core.button import Button


class ButtonCog:  # For the cog-like class
    """Client for interfacing with the server."""

    def __init__(self, bot) -> None:
        self.bot = bot
        """Load the handlers."""
        buttonlist = {}
        for value in self.__class__.__dict__.values():
            if isinstance(value, Button):
                value.master = self
                buttonlist[value.match] = value

        self.buttons = buttonlist
