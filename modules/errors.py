import discord


class TauticordException(Exception):
    """
    Base exception class for Tauticord
    """
    code: int

    def __init__(self, code: int, message: str):
        self.code: int = code or 300  # Default to 300 if no code is provided
        super().__init__(message)


class TauticordMigrationFailure(TauticordException):
    """
    Raised when an error occurs during Tauticord migrations
    """

    def __init__(self, message: str):
        super().__init__(code=301, message=message)


class TauticordSetupFailure(TauticordException):
    """
    Raised when an error occurs during Tauticord setup
    """

    def __init__(self, message: str):
        super().__init__(code=302, message=message)


class TauticordDiscordCollectionFailure(TauticordException):
    """
    Raised when an error occurs during collecting a Discord object
    """

    def __init__(self, message: str):
        super().__init__(code=303, message=message)


def determine_exit_code(exception: Exception) -> int:
    """
    Determine the exit code based on the exception that was thrown

    :param exception: The exception that was thrown
    :return: The exit code
    """
    if isinstance(exception, discord.LoginFailure):
        return 101  # Invalid Discord token
    elif isinstance(exception, discord.PrivilegedIntentsRequired):
        return 102  # Privileged intents are required
    elif isinstance(exception, TauticordException):
        return exception.code
    else:
        return 1
