# FastAPI Project Template

The basic requirement was to create an easy-to-follow project structure that integrates SQLAlchemy and Unit Tests nicely. Furthermore, I wanted to achieve a clear separation of concerns by using different modules.

## Basic folder structure

We structure our project into two modules: src and test:

```
.
└── backend/
    ├── src/
    │   ├── config/
    │   ├── routes/
    │   ├── util/
    │   └── __init__.py
    ├── test/
    │   ├── routes/
    │   ├── test_util/
    │   ├── __init.py__
    │   ├── app_test.py
    │   └── conftest.py
    ├── main.py
    └── requirements.txt
```

## Basic FastAPI

The application start is the `main.py`. In this file, we can define our FastAPI server as expected:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

app = FastAPI(
    title=APP_NAME,
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# Redirect / -> Swagger-UI documentation
@app.get("/")
def main_function():
    """
    # Redirect
    to documentation (`/docs/`).
    """
    return RedirectResponse(url="/docs/")
```

Some general app parameters are defined in the `config.py` located in `/config`. Those values could also be environment variables later in deployment.

```python
APP_NAME = "My fancy app"
VERSION = "v1.0.0"
```

## Routes

When it comes to the individual routes, I took inspiration from SvelteKit. They use file-based routing, which makes searching for a certain piece of code pretty straightforward — you just have to traverse the file structure the same way the URL is structured. This seems like a good idea for APIs, too, so I went with this approach, despite having the downside of creating files with the same names over and over again.

Let's say we build a very basic API for booking meeting rooms. We would probably face the following endpoints:

```
/rooms          GET
                POST
                DELETE
                PUT

/bookings       GET
                POST
                DELETE
                PUT

/users          GET
                POST
                DELETE
                PUT
```

As well as the following database tables:
```
rooms           bookings                users
=========       =============           =====
id              id                      id
name            booker_id               name
capacity        starting_time           mail
building        ending_time
                room_id
```

In this example, we would create three folders inside the `routes`-directory:

```
.
└── backend/
    └── src/
        └── routes/
            ├── users
            ├── bookings
            ├── rooms
            └── __init.py__
```

Additionally, I like to keep the authentication-logic on its own route.

Inside each of these folders, we would have three files: 

- `main.py`: Place for the actual API-Endpoint-Function, could look like this:
    ```python
    @router.get("/")
    async def get_all_users(user: User = 
    Depends(get_current_active_user),
                            db: Session = Depends(get_db)):
        """
        # Get a list of all users

        **Access:**
        - Admins get a list of all users.
        - Users with lower rights get a list with only the enabled users.
        """
        if user.super_admin:
            return get_users_admin(db=db)
        else:
            return get_users(db=db)
```

- `controller.py`: Handles your logic
    ```python
    def get_user_by_id(user_id: int, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
    
        if not user:
            raise HTTPException(
                status_code=404,
                detail="There is no user with this id."
            )
    
        return user
    ```

- `schemas.py`: Home to Pydantic schemas relevant for this route

To use those routes, we have to create a router for each route in the corresponding `{route}/main.py`:

```python
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)
```

We then import those routers into the applications `main.py`:

```python
from src.routes import bookings, users

# ---- Do this for all of your routes ----
app.include_router(users.main.router)
app.include_router(bookings.main.router)
# ----------------------------------------
```

## Database integration
With the above steps done, we have successfully organized our FastAPI server into several folders. However, access to a database is still not possible. We will use SQLAlchemy as an ORM.

Following the FastAPI-docs, we first need to specify our connection parameters inside `src/config/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_username = "user"
db_password = "password123"
db_url = "127.0.0.1:3306"
db_name = "example"

connectionString = f'mariadb+pymysql://{db_username}:{db_password}@{db_url}/{db_name}'

# use echo=True for debugging
engine = create_engine(connectionString, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

Depending on which database you use, you may need to modify the connection string and install a different pip-package. For MariaDB, the relevant ones are `mariadb`, `pymysql` and `SQLAlchemy==1.4.36`. 

> Keep in mind, that SQLAlchemy >= v2.0 introduced serious changes, so you will need to modify the template, if you wish to use the new version!

For interacting with the database from an endpoint called, we will use dependency injection. We define our dependency in `src/util/db_dependency.py`:

```python
from src.config.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

We can now create db-model-files for every route, e.g. `src/routes/users/models.py`:

```python
from src.config.database import Base
from sqlalchemy import Column, String, Integer


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=50))
    mail = Column(String(length=100))
```

Lastly, we import every model into our global `main.py` and create the specified tables from there:

```python
from src.config.database import engine

from src.routes.users import main, models
from src.routes.auth import main, models

users.models.Base.metadata.create_all(bind=engine)
auth.models.Base.metadata.create_all(bind=engine)
```

## Unit tests
For Unit Tests, `/test` mirrors the folder structure of `/src`. The tests are organized in the same routing-structure as before.
