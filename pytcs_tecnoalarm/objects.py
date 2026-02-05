from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class HandshakeEntrypoint(BaseModel):
    serviceName: str
    baseUrl: str
    token: str
    expiration: datetime


class HandshakeAccount(BaseModel):
    accountId: int
    backupDate: Optional[int] = None
    features: Optional[list] = Field(default=None)
    lastLogin: Optional[int] = None
    subscriptionDate: Optional[int] = None


class HandshakeAnswer(BaseModel):
    appID: int
    entrypoints: list[HandshakeEntrypoint]
    account: HandshakeAccount | None

