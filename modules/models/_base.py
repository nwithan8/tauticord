from typing import Any

from pydantic import BaseModel, BeforeValidator
from typing_extensions import Annotated


def int_to_string(value: Any) -> str | None:
    """
    Handle coercing ints to strings for Pydantic models.
    :param value: The value to be converted.
    :return: The string representation of the int, or None if the value is None.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        raise ValueError("Boolean value is not allowed")

    if isinstance(value, int):
        return str(value)

    if isinstance(value, str):
        try:
            int(value)
        except ValueError as e:
            raise ValueError("String value is not a valid integer representation") from e
        return value

    raise ValueError("Input value must be an int, string, or None")


IntAsString: str | None = Annotated[str | None, BeforeValidator(int_to_string)]


class _Base(BaseModel):
    pass
