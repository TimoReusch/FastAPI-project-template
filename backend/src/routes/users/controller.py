from fastapi import HTTPException
from pydantic import EmailStr

from .models import User
from sqlalchemy.orm import Session


def get_users_admin(db: Session):
    users = db.query(User.id, User.first_name, User.last_name, User.email, User.super_admin, User.disabled).all()
    return users


def get_users(db: Session):
    users = db.query(User.first_name, User.last_name, User.email, User.disabled).filter(User.disabled == False).all()
    return users


def get_user_by_id(user_id: int, db: Session):
    user = db.query(User.id, User.first_name, User.last_name, User.email, User.super_admin, User.disabled).filter(
        User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="There is no user with this id."
        )

    return user


def get_user_by_mail(mail: EmailStr, db: Session):
    user = db.query(User).filter(User.email == mail).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"There is no user with the E-Mail \"{mail}\"."
        )

    return user


def check_user_existence_by_id(user_id: int, db: Session):
    count = db.query(User).filter(User.id == user_id).count()
    if count < 1:
        return False

    return True


def check_user_existence_by_email(mail: EmailStr, db: Session):
    count = db.query(User).filter(User.email == mail).count()
    if count > 0:
        return True

    return False