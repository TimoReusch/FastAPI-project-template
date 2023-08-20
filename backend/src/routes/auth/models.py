from datetime import datetime, timedelta
from src.config.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from src.routes.users.models import User


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True, default=0)
    reset_token = Column(String(length=100), primary_key=True)
    expires = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now() + timedelta(hours=1))