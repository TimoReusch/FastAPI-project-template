from src.config.database import Base
from sqlalchemy import Column, String, Integer, Boolean


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(length=30))
    last_name = Column(String(length=30))
    email = Column(String(length=100))
    password = Column(String(length=250))
    super_admin = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)
