from fastapi.testclient import TestClient
from backend.main import app
from backend.src.util.db_dependeny import get_db
from backend.src.config.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"""
    Explaination of what is happening here can be found in the FastAPI Docs:
    https://fastapi.tiangolo.com/advanced/testing-database/
    https://fastapi.tiangolo.com/tutorial/testing/
"""

# TODO: Set test database (take another one then your production one!)
db_username = "user"
db_password = "password123"
db_url = "127.0.0.1:3306"
db_name = "example"

connectionString = f'mariadb+pymysql://{db_username}:{db_password}@{db_url}/{db_name}'
engine = create_engine(connectionString, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
