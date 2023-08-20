from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from src.config.database import engine
from src.config.config import APP_NAME, VERSION


from src.routes import auth, users

from src.routes.users import main, models
from src.routes.auth import main, models

users.models.Base.metadata.create_all(bind=engine)
auth.models.Base.metadata.create_all(bind=engine)
# ----------------------------------------

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

# ---- Do this for all of your routes ----
app.include_router(users.main.router)
app.include_router(auth.main.router)
# ----------------------------------------


# Redirect / -> Swagger-UI documentation
@app.get("/")
def main_function():
    """
    # Redirect
    to documentation (`/docs/`).
    """
    return RedirectResponse(url="/docs/")


# Swagger expects the auth-URL to be /token, but in our case it is /auth/token
# So, we redirect /token -> /auth/token
@app.post("/token")
def forward_to_login():
    """
    # Redirect
    to token-generation (`/auth/token`). Used to make Auth in Swagger-UI work.
    """
    return RedirectResponse(url="/auth/token")
