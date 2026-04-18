from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.db import lifespan
from src.exceptions import UserNotFoundError, UserAlreadyExistsError
from src.routes.users import router

app = FastAPI(lifespan=lifespan)


@app.exception_handler(UserNotFoundError)
def user_not_found_exception_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "User not found"},
    )


@app.exception_handler(UserAlreadyExistsError)
def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Пользователь с таким именем уже существует"},
    )


app.include_router(router)
