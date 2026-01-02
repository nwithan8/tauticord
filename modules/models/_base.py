from typing import Union, Optional, Any

from pydantic import BaseModel, BeforeValidator
from typing_extensions import Annotated


def int_to_string(value: Any) -> Union[str, None]:
    """
    Handle coercing ints to strings for Pydantic models.
    :param value: The value to be converted.
    :return: The string representation of the int, or None if the value is None.
    """
    if value is None:
        return None

    if isinstance(value, int):
        return str(value)

    if isinstance(value, str):
        try:
            int(value)
        except ValueError as e:
            raise ValueError("String value cannot be converted to int") from e
        return value

    raise ValueError("Input value is not an int or string")


IntAsString: Union[str, None] = Annotated[Optional[int | str], BeforeValidator(int_to_string)]


class _Base(BaseModel):
    pass
