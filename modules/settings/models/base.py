from pydantic import BaseModel


class BaseConfig(BaseModel):
    def as_dict(self) -> dict:
        raise NotImplementedError
