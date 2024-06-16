from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

from jose import jwt

from dotenv import load_dotenv
import os
load_dotenv()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.now(tz=timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM')
    )
    return encoded_jwt