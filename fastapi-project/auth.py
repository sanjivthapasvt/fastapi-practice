from datetime import datetime, timedelta
from typing import Union
import jwt
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
