from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, String




class Users(SQLModel, table=True):      
    id : Optional[int] = Field(default=None, primary_key=True, index=True)
    username : str = Field(sa_column=Column(String(255), unique=True))
    email: str = Field(sa_column=Column(String(255), unique=True))
    hashed_password: str = Field(sa_column=Column(String(255)))
    is_admin: bool = Field(default=0)
