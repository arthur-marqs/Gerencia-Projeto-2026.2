import re

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, value: str) -> str:
        email = value.strip().lower()

        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Informe um e-mail válido.")

        return email