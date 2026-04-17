from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from sqlmodel import Field, SQLModel, create_engine, Session, select
from starlette.responses import JSONResponse


class ErrorResponse(SQLModel):
    detail: str


class UserBase(SQLModel):
    name: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    model_config = {"extra": "forbid"}


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    model_config = {"extra": "forbid"}
    name: str | None = None


class UserNotFoundError(Exception):
    def __init__(self):
        self.detail = USER_NOT_FOUND_DETAIL


USER_NOT_FOUND_DETAIL = "User not found"

USER_NOT_FOUND_RESPONSE = {
    404: {
        "model": ErrorResponse,
        "description": USER_NOT_FOUND_DETAIL,
        "content": {"application/json": {"example": {"detail": "User not found"}}},
    }
}


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


def save_user(session: Session, user: User) -> User:
    session.commit()
    session.refresh(user)
    return user


@asynccontextmanager
async def lifespan(application: FastAPI):
    create_db_and_tables()
    yield


sqllite_file = "database.db"
sqllite_url = f"sqlite:///{sqllite_file}"

engine = create_engine(sqllite_url, echo=True)
app = FastAPI(lifespan=lifespan)


def get_user(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise UserNotFoundError()

    return user


def delete_user(session: Session, user_id: int) -> None:
    user = get_user(session, user_id)
    session.delete(user)
    session.commit()


def update_user(session: Session, user_id: int, user_data: UserCreate) -> User:
    db_user = get_user(session, user_id)
    db_user.name = user_data.name
    return save_user(session, db_user)


def patch_user(session: Session, user_id: int, user_data: UserUpdate) -> User:
    db_user = get_user(session, user_id)

    data = user_data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(db_user, key, value)

    changed = False
    if user_data.name is not None:
        db_user.name = user_data.name
        changed = True

    if data:
        session.commit()
    return db_user


@app.get("/")
async def root():
    return {"message": "Поехали!"}


@app.post(
    "/users",
    response_model=UserRead,
    status_code=201,
    summary="Создаём пользователя",
)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.model_validate(user)
    session.add(db_user)
    return save_user(session, db_user)


@app.get(
    "/users",
    response_model=list[UserRead],
    summary="Список пользователей",
)
def read_users(session: Session = Depends(get_session)):
    statement = select(User)
    users = session.exec(statement).all()
    return users


@app.get(
    "/users/{user_id}",
    response_model=UserRead,
    responses=USER_NOT_FOUND_RESPONSE,
    summary="Получаем информацию о пользователе",
)
def read_user(user_id: int, session: Session = Depends(get_session)):
    return get_user(session, user_id)


@app.delete(
    "/users/{user_id}",
    status_code=204,
    responses=USER_NOT_FOUND_RESPONSE,
    summary="Удаляем пользователя",
)
def delete_user_handler(user_id: int, session: Session = Depends(get_session)):
    delete_user(session, user_id)


@app.put(
    "/users/{user_id}",
    response_model=UserRead,
    responses=USER_NOT_FOUND_RESPONSE,
    summary="Заменяем пользователя",
)
def update_user_handler(
    user_id: int, user_data: UserCreate, session: Session = Depends(get_session)
) -> User:
    return update_user(session, user_id, user_data)


@app.patch(
    "/users/{user_id}",
    response_model=UserRead,
    responses=USER_NOT_FOUND_RESPONSE,
    summary="Частично заменяем информацию о пользовыателе",
)
def patch_user_handler(
    user_id: int, user_data: UserUpdate, session: Session = Depends(get_session)
) -> User:
    return patch_user(session, user_id, user_data)


@app.exception_handler(UserNotFoundError)
def user_not_found_except_handler(request: Request, exception: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exception.detail},
    )
