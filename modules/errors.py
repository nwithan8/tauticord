import discord


def determine_exit_code(exception: Exception) -> int:
    """
    Determine the exit code based on the exception that was thrown

    :param exception: The exception that was thrown
    :return: The exit code
    """
    if isinstance(exception, discord.LoginFailure):
        return 101  # Invalid Discord token
    else:
        return 1
