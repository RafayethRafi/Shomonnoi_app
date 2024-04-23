from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional
from pydantic import BaseModel,EmailStr,Field



class UserBase(BaseModel):
    name : Optional[str] = Field(None,min_length=3,max_length=50)
    phone_no : Optional[str] = Field(None,min_length=10,max_length=20)
    email : Optional[EmailStr] = None
    address : Optional[str] = Field(None,min_length=10,max_length=100)

class UserCreate(UserBase):
    name : str = Field(...)
    phone_no : str = Field(...)
    email : EmailStr = Field(...)
    password : str = Field(...,min_length=8,max_length=50)
    address : Optional[str] = Field(...)

class UserUpdate(UserBase):
    password : Optional[str] = Field(None,min_length=8,max_length=50)

class UserInDB(UserBase):
    user_id : int
    name : Optional[str]
    phone_no : Optional[str]
    email : Optional[EmailStr]
    address : Optional[str]
    role : str
    created_at : datetime

    class Config:
        from_attributes = True


class DepositBase(BaseModel):
    name : Optional[str] = Field(None,min_length=3,max_length=50)
    amount : Optional[int] = Field(None,gt=0)
    
class DepositCreate(DepositBase):
    name : str = Field(...)
    amount : int = Field(...,gt=0)
    extra_charges : Optional[int] = Field(0)
    payment_month : int = Field(...,gt=0)
    payment_year : int = Field(...,gt=0)

class DepositUpdate(DepositBase):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    amount: Optional[int] = Field(None, gt=0)
    extra_charges: Optional[int] = None
    payment_month: Optional[int] = None
    payment_year: Optional[int] = None


class DepositInDB(DepositBase):
    deposit_id : int
    user_id : int
    name : Optional[str]
    amount : Optional[int]
    extra_charges: Optional[int]
    payment_month: Optional[int]
    payment_year: Optional[int]

    diposit_date : datetime

    class Config:
        from_attributes = True


class InvitationBase(BaseModel):
    email : EmailStr
    role : str

class InvitationCreate(InvitationBase):
    admin_id : int
    organization_id : int


class Token(BaseModel):
    access_token: str
    token_type : str


class TokenData(BaseModel):
    id : Optional[int] = None



class ForgotPassword(BaseModel):
    email : EmailStr


class PassReset(BaseModel):
    password : str = Field(...,min_length=8,max_length=50)