"""Handling authentication and authorization"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from .controller import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, is_user_disabled, \
    generate_reset_token, set_new_password
from .schemas import Token, EmailSchema, SetNewPassword
from src.util.db_dependency import get_db
from src.routes.users.controller import check_user_existence_by_email

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    # Login

    Gives you a JWT in return for a correct username and password.

    **Access:** Public.

    `form_data`: x-www-form-urlencoded with `username` and `password`
    """

    if not check_user_existence_by_email(mail=form_data.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no user with this email."
        )

    if is_user_disabled(user_email=form_data.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This user has been disabled. Login is not possible."
        )

    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/reset-password")
async def reset_password(user_email: EmailSchema, db: Session = Depends(get_db)):
    """
    # Reset password

    The user can insert his email. If there is a user with this mail in the database, a mail will be sent.
    This includes a link with a unique token, the user can use to set a new password over `/auth/set-new-password`.

    **Access:** Public.
    """
    await generate_reset_token(email=user_email.email, db=db)
    return JSONResponse(status_code=200, content={"detail": "Password reset mail successfully sent."})


@router.post("/set-new-password")
async def set_password(reset_data: SetNewPassword, db: Session = Depends(get_db)):
    """
    # Set new password

    The user can set a new password with his user_id and the token he obtained over `/auth/reset-password`.

    **Access**: Public.
    """
    if set_new_password(user_id=reset_data.user_id, token=reset_data.reset_token, new_password=reset_data.new_password,
                        db=db):
        return JSONResponse(status_code=200, content={"detail": "Password successfully changed."})
    else:
        raise HTTPException(status_code=500, detail="An error occurred while trying to change the password.")
