from fastapi.testclient import TestClient
from main import app
import pytest
from src.util.db_dependency import get_db
from src.config.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.routes.users.models import User
from src.routes.auth.controller import get_password_hash


@pytest.fixture(scope="session")
def db_engine():
    # TODO: Set test databse (take another one then your production one!)
    db_username = "user"
    db_password = "password123"
    db_url = "127.0.0.1:3306"
    db_name = "example"

    connection_string = f'mariadb+pymysql://{db_username}:{db_password}@{db_url}/{db_name}'
    engine = create_engine(connection_string, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(db_engine):
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    with db_engine.connect() as connection:
        with connection.begin() as transaction:
            session = session_factory(bind=connection)
            app.dependency_overrides[get_db] = lambda: session
            yield session
            transaction.rollback()


@pytest.fixture
def client():
    return TestClient(app)


# TODO: Define your fixtures (like below) here
@pytest.fixture
def user_1(db):
    u = User(
        first_name="Saul",
        last_name="Goodman",
        email="saul.goodman@wexler-mcgill.law",
        password=get_password_hash("asdf"),
        super_admin=True,
        disabled=False
    )
    db.add(u)
    db.commit()

    return u
