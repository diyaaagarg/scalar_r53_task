from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str


class AccountOut(BaseModel):
    aws_account_id: str
    display_name: str


class SessionOut(BaseModel):
    user: UserOut
    account: AccountOut
    region: str
