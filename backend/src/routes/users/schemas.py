from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    super_admin: bool
    disabled: bool | None = None

    class Config:
        orm_mode = True
