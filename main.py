import asyncio

from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()


class UserNotFoundError(Exception):
    pass


class UserIn(BaseModel):
    name: str
    age: int
    email: str | None = None


class UserOut(BaseModel):
    name: str
    age: int


fake_users = {
    1: {"id": 1, "name": "Алиса"},
    2: {"id": 1, "name": "Боб  "},
}


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc) or "User not Found"},
    )


# db
async def get_db():
    print("open db")
    db = {
        "users": {
            1: {"id": 1, "name": "Алиса"},
        }
    }
    try:
        yield db
    finally:
        print("close db")


# service
def get_user_service(db=Depends(get_db)):
    print("Создание сервиса")

    class UserService:
        def get_user(self, user_id: int):
            user = db["users"].get(user_id)
            if not user:
                raise UserNotFoundError(f"Пользователь {user_id} не найден")
            return user

    return UserService()


# repo
async def get_repo(db=Depends(get_db)):
    print("create repo")
    repo = {"repo": f"repo using {db['conn']}"}
    try:
        yield repo
    finally:
        print("close repo")


# handler
@app.get("/us")
async def get_us(repo=Depends(get_repo)):
    print("Вызов handler")
    await asyncio.sleep(0.1)
    print("Завершение handler")
    return {"repo": repo["repo"]}


def get_message():
    return "Привет от зависимости"


def get_user_agent(request: Request):
    return request.headers.get("User-Agent")


def get_debug(request: Request):
    print(f"{request.url=}")
    return "OK"


@app.get("/test")
def test(x=Depends(get_debug)):
    return {"x": x}


@app.get("/info")
def info(user_agent: str | None = Depends(get_user_agent)):
    return {"user_agent": user_agent}


@app.get("/hello")
def hello(message: str = Depends(get_message)):
    return {"message": message}


@app.get("/")
def root():
    return {"message": "Привет, мир!"}


@app.get("/users/{user_id}")
def get_user(user_id: int, service=Depends(get_user_service)):
    print("handler")
    return service.get_user(user_id)


@app.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    return {
        "skip": skip,
        "limit": limit,
        "skip_type": str(type(skip)),
        "limit_type": str(type(limit)),
    }


@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    return {
        "name": user.name,
        "age": user.age,
        "email": user.email,
        "is_admin": True,
        "interlal_note": "created from docs",
    }
