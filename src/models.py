from sqlmodel import SQLModel, Field
from typing import Annotated
from pydantic import StringConstraints, field_validator

NameStr = Annotated[str, StringConstraints(min_length=1)]


class ApiModel(SQLModel):
    model_config = {"extra": "forbid"}


class UserBase(ApiModel):
    name: NameStr

    # noinspection PyNestedDecorators
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Имя не должно быть пустым")
        return value


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int


class UserUpdate(ApiModel):
    name: str | None = None

    # noinspection PyNestedDecorators
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Name must not be empty")
        return value
