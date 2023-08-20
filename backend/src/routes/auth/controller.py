"""Logic for authentication and authorization"""
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime

from starlette import status

from src.routes.users.controller import get_user_by_mail
from src.util.db_dependency import get_db
from sqlalchemy.orm import Session
from .schemas import TokenData
from src.routes.users.schemas import User
from src.routes.users.models import User as UserModel
from .models import PasswordResetToken
from src.util.mail.mail_sender import send_password_reset_mail
from src.routes.users.controller import check_user_existence_by_id
from pydantic import EmailStr

# TODO: Generate secret key with "openssl rand -hex 32" (also described in FastAPI docs)
SECRET_KEY = ""

"""Secret key used for encryption"""
ALGORITHM = "HS256"
"""Algorithm used for encryption"""
ACCESS_TOKEN_EXPIRE_MINUTES = 120
"""Time the JWT should live"""

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Verify the password by comparing it with the hashed one stored in the database

    :param plain_password: Password as plain text
    :param hashed_password: Password hash
    :return: `True` if the password matched the hash, else `False`.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """ Takes a plain text password and hashes it.

    :param password: Password as plain text
    :return: Hashed password
    """
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session) -> User:
    """ Method called to authenticate a user.

    :param username: Username
    :param password: Password as plain text
    :param db: Database dependency
    :return: `False` if the user does not exist or the password verification fails, otherwise the details of the person that wants to log in as object of type `User`.
    """

    user = get_user_by_mail(mail=username, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not get user with mail \"{username}\".",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """ Create a JWT

    :param data: Data to be encoded
    :param expires_delta: Timespan the JWT should be valid
    :return: JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """ Returns the information of a user by only using the JWT.

    :param db:
    :param token: Access token
    :raise credentials_exception: If token not valid
    :return: Object of type `User`
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_mail(mail=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """ Outputs the user information based on the JWT, if the user is not disabled

    :param current_user: Authentication-Token
    :raise HTTPException: 400 if user is disabled
    :return Object of type `User`
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="User disabled")
    return current_user


def is_user_disabled(user_email, db: Session):
    """ Check if a user is disabled by using the email/username

    :param db:
    :param user_email: Username
    :return: `False` if user is disabled, else `True`
    """
    user = get_user_by_mail(mail=user_email, db=db)

    return user.disabled


def update_user_password_by_id(user_id, new_password, db: Session):
    if check_user_existence_by_id(user_id=user_id, db=db):
        db.query(UserModel).filter(UserModel.id == user_id).update({
            UserModel.password: new_password
        })
        db.commit()
    else:
        raise HTTPException(status_code=404,
                            detail="User not found.")


async def generate_reset_token(email: EmailStr, db: Session):
    current_user = get_user_by_mail(mail=email, db=db)
    token = secrets.token_hex(32)

    # Check for an existing token. If there is one, delete it first
    existing_token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == current_user.id).first()
    if existing_token:
        db.delete(existing_token)
        db.commit()

    # Store the token
    db.add(PasswordResetToken(user_id=current_user.id, reset_token=token))
    db.commit()
    name = f"{current_user.first_name} {current_user.last_name}"
    await send_password_reset_mail(email, current_user.id, token, name)


def set_new_password(user_id: int, token: str, new_password: str, db: Session):
    # Check if the token is correct and not more than an hour passed
    db_entry = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id)
    if db_entry.count() > 0:
        reset_token = db_entry.first()
        if datetime.now() < reset_token.expires:
            if reset_token.reset_token == token:
                update_user_password_by_id(user_id=user_id, new_password=get_password_hash(new_password), db=db)
                db.delete(reset_token)
                db.commit()
                return True

    return False


def change_password(user_id: int, new_password: str):
    if check_user_existence_by_id(user_id):
        update_user_password_by_id(user_id, get_password_hash(new_password))
        return True
    else:
        raise HTTPException(status_code=404,
                            detail="User not found.")