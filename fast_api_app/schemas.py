from pydantic import BaseModel, validator
from datetime import datetime
import re

class URLBase(BaseModel):
    target_url: str

class URL(URLBase):
    is_active: bool
    clicks: int

    class Config:
        orm_mode = True

class URLInfo(URL):
    url: str
    admin_url: str


class URLUpdate(BaseModel):
    class Config:
        orm_mode = True


class URLStats(BaseModel):
    target_url: str
    created_at: datetime or None
    clicks: int
    last_used: datetime or None
    expires_at: datetime or None
    shortened_url: str

    class Config:
        orm_mode = True


class URLCustomCreate(BaseModel):
    target_url: str
    custom_key: str

    @validator('custom_key')
    def validate_custom_key(cls, v):
        if v is not None:
            if len(v) < 4 or len(v) > 20:
                raise ValueError('Ключ должен быть длиной от 4 до 20 символов')

            if not re.match("^[a-zA-Z0-9_-]+$", v):
                raise ValueError('Ключ может содержать только буквы, числа, подчеркивания и дефисы')

            if not v[0].isalnum():
                raise ValueError('Ключ должен начинаться с буквы или цифры')

        return v

class URLCustomResponse(BaseModel):
    key: str
    custom_key: str
    target_url: str
    shortened_url: str
    admin_url: str
    expires_at: datetime
    message: str

    class Config:
        orm_mode = True

class URLSummary(BaseModel):
    key: str
    shortened_url: str
    target_url: str
    clicks: int
    last_used: datetime
    created_at: datetime

class AnalyticsResponse(BaseModel):
    period: dict
    summary: dict
    recent_activity: dict
    expiration: dict
    top_urls: dict
    timestamp: str